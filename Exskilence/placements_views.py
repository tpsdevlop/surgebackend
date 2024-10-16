# views.py
import csv
import datetime
from datetime import date, datetime, time, timedelta
import re
from django.utils import timezone
from django.core.mail import EmailMessage
import io
import json
import smtplib
import ssl
import certifi
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
from bson import Decimal128
from decimal import Decimal
from rest_framework.decorators import api_view

@csrf_exempt
def student_list(request):
    if request.method == 'POST':
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            # Process each student data
            for student_data in data:
                name = student_data.get('Student Name')
                college = student_data.get('College')
                branch = student_data.get('Branch')

                # Fetch the existing student profile
                existing_student_profile = StudentProfile.objects.filter(name=name, college=college, branch=branch).first()

                # if existing_student_profile:
                #     # print(f"Found existing profile for {name}.")
                # else:
                    # print(f"No existing profile found for {name}.")

                # Prepare the data to be updated or created
                update_data = {
                    'cgpa': student_data.get('CGPA', existing_student_profile.cgpa if existing_student_profile else None),
                    'skills': student_data.get('Skills', existing_student_profile.skills if existing_student_profile else None),
                    'otherskills': student_data.get('Add other technical skills', existing_student_profile.otherskills if existing_student_profile else None),
                    'entranceTest': student_data.get('Entrance Test', existing_student_profile.entranceTest if existing_student_profile else None),
                    'python': student_data.get('Python', existing_student_profile.python if existing_student_profile else None),
                    'sql': student_data.get('SQL', existing_student_profile.sql if existing_student_profile else None),
                    'dsa': student_data.get('DSA', existing_student_profile.dsa if existing_student_profile else None),
                    'aptitude': student_data.get('Apt', existing_student_profile.aptitude if existing_student_profile else None),
                    'resumeLink': student_data.get('Upload Resume link without email and phone no', existing_student_profile.resumeLink if existing_student_profile else None),
                    'communicationVideo': student_data.get('Upload less than 1 minute communication video', existing_student_profile.communicationVideo if existing_student_profile else None),
                    'hackerrankLink': student_data.get('SQL Hackerrank Link', existing_student_profile.hackerrankLink if existing_student_profile else None),
                    'leetcodeLink': student_data.get('Leetcode Link', existing_student_profile.leetcodeLink if existing_student_profile else None),
                    'githubLink': student_data.get('Github Link', existing_student_profile.githubLink if existing_student_profile else None),
                    'profileimage': student_data.get('Upload recent photo(JPG Format, less than 10MB)', existing_student_profile.profileimage if existing_student_profile else None),
                    'financialaid': student_data.get('Financial aid text', existing_student_profile.financialaid if existing_student_profile else None),
                    'contact': student_data.get('Contact No', existing_student_profile.contact if existing_student_profile else None),
                    'placed': student_data.get('Placed', existing_student_profile.placed if existing_student_profile else None),
                    'emailid': student_data.get('Email_ID',existing_student_profile.emailid if existing_student_profile else None)
                }

                # print(f"Updating profile with data: {update_data}")

                # Update or create the student profile
                student_profile, created = StudentProfile.objects.update_or_create(
                    name=name,
                    college=college,
                    branch=branch,
                    defaults=update_data
                )

                # if created:
                #     # print(f"Student {name} added successfully.")
                # else:
                    # print(f"Student {name} updated successfully.")

            return JsonResponse({'message': 'Data processed successfully'}, status=201)

        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'JSON decode error: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'GET':
        placed_filter = request.GET.get('placed')  # Extract placed filter from query parameters
        queryset = StudentProfile.objects.all()
        
        if placed_filter is not None:
            if placed_filter.lower() == 'yes':
                queryset = queryset.filter(placed=True)
            else:
                queryset = queryset.exclude(placed=True)  # Exclude placed students
        
        students = list(queryset.values())  # Convert queryset to list of dicts
        return JsonResponse(students, safe=False)
    
    else:
        return JsonResponse({'error': 'Unsupported HTTP method'}, status=405)


def decimal_to_float_or_str(obj):
    if isinstance(obj, Decimal128):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: decimal_to_float_or_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [decimal_to_float_or_str(v) for v in obj]
    return obj
    
@csrf_exempt
def get_all_students(request):
    if request.method == 'GET':
        try:
            # Fetch all student profiles from the database excluding those that are place
            students = StudentProfile.objects.filter(placed='')
            # Convert the queryset to a list of dictionaries
            student_list = list(students.values(
                'id',
                'profileimage',
                'name',
                'college',
                'branch',
                'contact',
                'emailid',
                'cgpa',
                'skills',
                'otherskills',
                'entranceTest',
                'python',
                'sql',
                'dsa',
                'aptitude',
                'rank',
                'resumeLink',
                'communicationVideo',
                'hackerrankLink',
                'leetcodeLink',
                'githubLink',
                'isSelected',
                'financialaid',
                'placed'
            ))
            # Convert Decimal128 fields to JSON-serializable format
            student_list = decimal_to_float_or_str(student_list)
            # Return the data as JSON
            return JsonResponse(student_list, safe=False, status=200)
        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # Handle unsupported HTTP methods
        return JsonResponse({'error': 'Unsupported HTTP method'}, status=405)  
    
def handle_student_request(request):
    if request.method == 'GET':
        return get_all_students()
    
    else:
        return JsonResponse({'error': 'Unsupported HTTP method'}, status=405)
    

@csrf_exempt
def handle_form_submission(request):
    if request.method == 'POST':
        try:
            # Extract form data
            data = json.loads(request.body)
            role = data['role']
            name = data['name']
            email = data['email']
            designation = data['designation']
            contactNumber = data['contactNumber']
            company = data['company']
            loc = data['loc']
            openings = data['openings']
            employmentType = data['employmentType']
            duration = data['duration']
            hasBond = data['hasBond']
            bondDuration = data['bondDuration']
            packageInLPA = data['packageInLPA']
            comments = data['comments']
            selected_students = data['selectedStudents']

            # Save contact info to the database
            contact_info = ContactInfo(
                role=role,
                name=name,
                email=email,
                designation=designation,
                contactNumber=contactNumber,
                company=company,
                loc=loc,
                openings=openings,
                employmentType=employmentType,
                hasBond=hasBond,
                bondDuration=bondDuration,
                packageInLPA=packageInLPA,
                comments=comments
            )
            contact_info.save()

            # Generate CSV for selected students
            csv_file = io.StringIO()
            writer = csv.writer(csv_file)
            writer.writerow(['Student Name','College','Branch','Contact No', 'Email ID', 'Resume Link'])  # Add headers as needed
            
            for student in selected_students:
                writer.writerow([student['name'],student['college'], student['branch'], student['contact'], student.get('emailid'),student['resumeLink']])  # Ensure email column is included
            
            csv_file.seek(0)
            csv_content = csv_file.getvalue()
            s2=selected_students
            # # print("csv",csv_content)
            role1="Hiring Manager" if role=='hiringManager' else "Volunteer"
            subject = f"Shortlisted Swapnodaya Student's from {role1}"
            body = f"""`

            Please find attached the CSV file with details of the selected students.

            Contact Details:
            - Name: {name}
            - Email: {email}
            - Designation: {designation}
            - Contact Number: {contactNumber}
            - Company: {company}
            - Location: {loc}
            - Openings: {openings}
            - Employment Type: {employmentType}
            - Duration: {duration}
            - Has Bond: {hasBond}
            - Bond Duration: {bondDuration}
            - Package (in LPA): {packageInLPA}
            - Comments: {comments}
            """

            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = ['krupasagar@swapnodaya.com','raghuram@swapnodaya.com','siddharthnitk@gmail.com']
            # recipient_list = ['pavankalyan4292@gmail.com']           
            email_sent = send_session_email(subject, body, from_email, recipient_list, csv_content)

            if email_sent:
                return JsonResponse({'status': 'Email sent successfully'}, status=200)
            else:
                return JsonResponse({'status': 'Failed to send email'}, status=500)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def send_session_email(subject, message, from_email, recipient_list,csv_content):
    # Set up a secure SSL context
    context = ssl.create_default_context(cafile=certifi.where())

    try:
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            
            # Create the email message
            email = EmailMessage(subject, message, from_email, recipient_list)
            try:
                email.attach('students.csv', csv_content, 'text/csv')
            except:
                print("attacement didnt work")
            # Send the email to each recipient in the list
            for recipient in recipient_list:
                server.sendmail(from_email, recipient, email.message().as_string())
        
        return True  # Email sent successfully
    except Exception as e:
        # print(f"Failed to send emails: {e}")
        return False  # Failed to send email


@csrf_exempt
def login_view(request, id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            login = Login(
                id=data.get('id'),  # Accepting id from the POST request
                username=data.get('username'),
                category=data.get('category'),
                email=data.get('email')
            )
            login.save()
            return JsonResponse({'message': 'Login entry created successfully', 'login_id': login.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@api_view(['GET'])
def get_user(request, email, name):
    if request.method == 'GET':
        try:
            
            login = Login.objects.filter(email=email).first()
            if login is None:
                
                uid=Login.objects.all().order_by('-id').first()
                if uid is None:
                    uid = 0
                else:
                    uid = uid.id
                login = Login.objects.create(
                    id = uid+1,
                    username=name,
                    category="g",
                    email=email,
                    timestamp=datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
                )
                login_data = {
                'id': uid+1,
                'username': name,
                'category': "g",
                'email': email
                }
                return HttpResponse(json.dumps(login_data), status=200, content_type='application/json')

            login_data = {
                'id': login.id,
                'username': login.username,
                'category': login.category,
                'email': login.email
            }
            return HttpResponse(json.dumps(login_data), status=200, content_type='application/json')
        except Login.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
@api_view(['POST'])
def guest_login(request):
    try:
        data = json.loads(request.body)
        email = data.get('Email')
        def mailValidator(email):
            pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
            return re.match(pattern, email) is not None
        if not mailValidator(email):
            return HttpResponse(json.dumps({'error': 'Invalid email address'}), status=404, content_type='application/json')
        value = data.get('Password')
        pwd = Switches.objects.filter(Key='Guest_Pwd').first().Value
        if value == pwd:
            login = Login.objects.filter(email=email).first()
            if login is None:
                
                uid=Login.objects.all().order_by('-id').first()
                if uid is None:
                    uid = 0
                else:
                    uid = uid.id
                login = Login.objects.create(
                    id = uid+1,
                    username='Guest',
                    category="g",
                    email=email,
                    timestamp=datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
                )
                login_data = {
                'id': uid+1,
                'username': 'Guest',
                'category': "g",
                'email': email
                }
            login_data = {
                'id': login.id,
                'username': login.username,
                'category': login.category,
                'email': login.email
            }
            return HttpResponse(json.dumps(login_data), status=200, content_type='application/json')
        else:
            return HttpResponse(json.dumps({'error': 'Wrong password'}), status=404, content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=500, content_type='application/json')