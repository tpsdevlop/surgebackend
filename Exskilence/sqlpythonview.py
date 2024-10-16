from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status as http_status
from .models import StudentDetails,StudentDetails_Days_Questions,QuestionDetails_Days
from django.db.models import Sum
from azure.storage.blob import BlobServiceClient
from django.conf import settings
import json
from django.db.models import Q
from  Exskilencebackend160924.Blob_service import *



@api_view(['GET'])
def filter_options(request):
    students = StudentDetails.objects.all()

    years = list(set([f'20{s.StudentId[:2]}' for s in students]))
    colleges = list(set(students.values_list('college_Id', flat=True)))
    branches = list(set(students.values_list('branch', flat=True)))
    courses = list(set([course for s in students for course in s.Courses]))

    return Response({
        'years': years,
        'colleges': colleges,
        'branches': branches,
        'courses': courses
    })

@api_view(['GET'])
def student_list(request):
    year = request.GET.get('year')
    college = request.GET.get('college')
    branch = request.GET.get('branch')
    course = request.GET.get('course')
    
    students = StudentDetails.objects.all()
    
    if year:
        # Convert year to a two-digit format for filtering
        year_prefix = year[-2:]
        students = students.filter(StudentId__startswith=year_prefix)
    if college:
        students = students.filter(college_Id=college)
    if branch:
        students = students.filter(branch=branch)
    if course:
        students = students.filter(Courses__contains=course)
    
    student_data = []
    for student in students:
        student_data.append({
            'StudentId': student.StudentId,
            'firstName': student.firstName,
            'lastName': student.lastName,
            'branch': student.branch,
            'college_Id': student.college_Id,
            'courses': student.Courses.split(',') if isinstance(student.Courses, str) else student.Courses
        })
    
    return JsonResponse(student_data, safe=False)

@api_view(['GET'])
def student_details_day(request, student_id, course):
    try:
        student_details = StudentDetails_Days_Questions.objects.get(Student_id=student_id)
        student = StudentDetails.objects.get(StudentId=student_id)

        if course not in student.Courses:
            return JsonResponse({"error": "Student is not enrolled in this course"}, status=status.HTTP_400_BAD_REQUEST)

        days_data = {}
        for day, questions in student_details.Qns_lists.items():
            if day.startswith(f'{course}_Day_') and not day.endswith('Day_0'):
                day_num = day.split('_Day_')[1]
                day_key = f"Day{day_num}"
                if day_key not in days_data:
                    days_data[day_key] = {
                        "total_questions": 0,
                        "answered_questions": 0,
                        "question_ids": set(),
                        "overall_score": 0
                    }
                days_data[day_key]["total_questions"] += len(questions)
                days_data[day_key]["question_ids"].update(questions)

                for question_id in questions:
                    difficulty = question_id[-4]
                    if difficulty == 'E':
                        days_data[day_key]["overall_score"] += 5
                    elif difficulty == 'M':
                        days_data[day_key]["overall_score"] += 10
                    elif difficulty == 'H':
                        days_data[day_key]["overall_score"] += 15

        for day, answers in student_details.Ans_lists.items():
            if day.startswith(f'{course}_Day_') and not day.endswith('Day_0'):
                day_num = day.split('_Day_')[1]
                day_key = f"Day{day_num}"
                if day_key in days_data:
                    days_data[day_key]["answered_questions"] += len(answers)

        max_day_completed = student_details.Days_completed.get(course, 0)

        formatted_days = []
        for day, data in days_data.items():
            if data["total_questions"] > 0:
                day_number = int(day[3:])
                question_ids = data["question_ids"]
                day_score = QuestionDetails_Days.objects.filter(
                    Student_id=student_id,
                    Qn__in=question_ids
                ).aggregate(total_score=Sum('Score'))['total_score'] or 0

                formatted_days.append({
                    "day": day,
                    "total_questions": data["total_questions"],
                    "answered_questions": data["answered_questions"],
                    "progress": f"{data['answered_questions']}/{data['total_questions']}",
                    "status": "Completed" if day_number <= max_day_completed else "Incomplete",
                    "score": day_score,
                    "overall_score": data["overall_score"],
                    "obtained_score": f"{day_score}/{data['overall_score']}" if data["overall_score"] > 0 else "0/0"
                })

        formatted_days.sort(key=lambda x: int(x['day'][3:]))

        student_details_data = {
            'Student_id': student_details.Student_id,
            'Name': f"{student.firstName} {student.lastName}",
            'Branch': student.branch,
            'College': student.college_Id,
            'Days': formatted_days,
            'Days_completed': student_details.Days_completed.get(course, 0),
            'Start_Course': student_details.Start_Course.get(course),
        }

        return Response(student_details_data)
    except StudentDetails_Days_Questions.DoesNotExist:
        return JsonResponse({"error": "Student details not found"}, status=status.HTTP_404_NOT_FOUND)
    except StudentDetails.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def getreport(request, student_id, course, day):
    try:
        # Extract the day number from the 'day' parameter
        if day.startswith('day'):
            day_no = day[3:]  # Removes 'day' prefix and gets the number
            day_formatted = f"Day_{day_no}"  # Format to 'Day_X'
        else:
            return JsonResponse({"error": "Invalid day format"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the student details
        student = StudentDetails.objects.filter(StudentId=student_id).first()
        if not student:
            return JsonResponse({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Fetch the student details day
        student_details_day = StudentDetails_Days_Questions.objects.filter(Student_id=student_id).first()
        if not student_details_day:
            return JsonResponse({"error": "Student details not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the question list for the specific course and day
        qn_list_key = f"{course}_{day_formatted}"
        qn_list = student_details_day.Qns_lists.get(qn_list_key, [])
        if not qn_list:
            return JsonResponse({"error": "No questions found for this day"}, status=status.HTTP_404_NOT_FOUND)
        
        # Fetch all question details for this student
        question_details = QuestionDetails_Days.objects.filter(Student_id=student_id, Subject=course)
        
        output = []
        total_score = 0
        total_out_of = 0
        
        for index, q in enumerate(qn_list, start=1): 
            difficulty = q[-4]
            out_of = 15 if difficulty == 'H' else 10 if difficulty == 'M' else 5
            total_out_of += out_of
            q_detail = question_details.filter(Qn=q).first()
            try:
                blob_name = f"Question/{str(q)[1:13]}/{str(q)}.json"
                qndata = download_blob(blob_name)
                json_content_str = qndata.decode('utf-8')
                question_data = json.loads(json_content_str)
                question_name = question_data.get('Qn', 'Unknown')
            except Exception as blob_error:
                print(f"Error fetching question for {q}: {str(blob_error)}")
                question_name = "Unknown"
            
            if q_detail:
                total_score += q_detail.Score
                # Determine the question_status based on the Result
                if isinstance(q_detail.Result, dict):
                    if 'TestCases' in q_detail.Result and 'Result' in q_detail.Result['TestCases']:
                        result = q_detail.Result['TestCases']['Result']
                    elif 'Result' in q_detail.Result:
                        result = q_detail.Result['Result']
                    else:
                        result = None
                else:
                    result = q_detail.Result
 
                if result is True or str(result).lower() == 'true':
                    question_status = 'Correct'
                elif result is False or str(result).lower() == 'false':
                    question_status = 'Incorrect'
                elif result == 'Not attempted':
                    question_status = 'Skipped'
                else:
                    question_status = 'Unknown'
               
                output.append({
                    'Index': index,
                    'Qn': q,
                    'Question_name': question_name,
                    'Attempts': q_detail.Attempts,
                    'Ans': q_detail.Ans,
                    'Score': f"{q_detail.Score}/{out_of}",
                    'Result': q_detail.Result,
                    'Status': question_status
                })
            else:
                output.append({
                    'Index': index,
                    'Qn': q,
                    'Question_name': question_name,
                    'Attempts': 0,
                    'Ans': '',
                    'Score': f"0/{out_of}",
                    'Result': {
                        'Testcase1': 'Not attempted',
                        'Testcase2': 'Not attempted',
                        'Testcase3': 'Not attempted',
                        'Result': 'Not attempted'
                    },
                    'Status': 'Skipped'
                })
        
        output.append({'Score': f"{total_score}/{total_out_of}"})
        return JsonResponse(output, safe=False)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)