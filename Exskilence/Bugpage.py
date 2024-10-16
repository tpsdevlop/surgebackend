from django.http import JsonResponse
import pytz
from .models import StudentDetails, BugDetails
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status
def get_students_with_bug_details(request):
    bugs = BugDetails.objects.all()
    student_bug_map = {}
    for bug in bugs:
        student_id = bug.Student_id
        if student_id not in student_bug_map:
            student_bug_map[student_id] = {
                'bugs': [],
                'resolved_issues_count': 0,
                'total_issues_count': 0
            }
        student_bug_map[student_id]['bugs'].append(bug)
        student_bug_map[student_id]['total_issues_count'] += 1
        if bug.BugStatus == "Resolved":
            student_bug_map[student_id]['resolved_issues_count'] += 1
    student_ids = student_bug_map.keys()
    students = StudentDetails.objects.filter(StudentId__in=student_ids)
    response_data = []
    for student in students:
        student_id = student.StudentId
        if student_id in student_bug_map:
            bug_data = student_bug_map[student_id]
            latest_bug = max(bug_data['bugs'], key=lambda bug: bug.Reported)
            resolution_score = f"{bug_data['resolved_issues_count']}/{bug_data['total_issues_count']}"
            response_data.append({
                'StudentId': student.StudentId,
                'firstName': student.firstName,
                'college': student.college_Id,
                'branch': student.branch,
                'number_of_issues_reported': bug_data['total_issues_count'],
                'date_of_issue_reported': latest_bug.Reported,
                'issue_type': latest_bug.Issue_type,
                'date_of_issue_resolved': latest_bug.Resolved,
                'status_of_latest_issue': latest_bug.BugStatus,
                'resolution_score': resolution_score
            })
 
    return JsonResponse(response_data, safe=False)
 
@method_decorator(csrf_exempt, name='dispatch')
class BugView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            resolved_date = data.get('Resolved')
            if resolved_date:
                resolved_date = datetime.fromisoformat(resolved_date)
            bug = BugDetails(
                Student_id=data['Student_id'],
                Img_path=data['Img_path'],
                BugDescription=data['BugDescription'],
                Issue_type=data['Issue_type'],
                Reported=datetime.now(),  
                Resolved=resolved_date,
                Comments=data.get('Comments', {})
            )
            bug.save()
            return JsonResponse({'message': 'Bug created successfully', 'bug_id': bug.sl_id}, status=201)
        except KeyError as e:
            return JsonResponse({'error': f"Missing field: {e}"}, status=400)
        except ValueError as e:
            return JsonResponse({'error': f"Invalid data: {e}"}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
 
    def get(self, request):
        student_id = request.GET.get('student_id')
        if student_id:
            bugs = BugDetails.objects.filter(Student_id=student_id).values()
        else:
            bugs = BugDetails.objects.all().values()
 
        bugs_list = list(bugs)
 
        for bug in bugs_list:
            student = StudentDetails.objects.filter(StudentId=bug['Student_id']).first()
            if student:
                bug['studentname'] = f"{student.firstName} {student.lastName}"
                bug['student_id'] = student.StudentId
                bug['email'] = student.email
                bug['mob_No'] = student.mob_No
                bug['college'] = student.college_Id
                bug['branch'] = student.branch
            else:
                bug['studentname'] = 'Unknown'
                bug['student_id'] = bug['Student_id']
                bug['email'] = 'Unknown'
                bug['mob_No'] = 'Unknown'
                bug['college'] = 'Unknown'
                bug['branch'] = 'Unknown'
            bug['comments'] = bug.get('Comments', [])
 
        return JsonResponse(bugs_list, safe=False)
 
    def put(self, request):
        data = json.loads(request.body)
        bug_id = data.get('bug_id')
        comment = data.get('Comment')
 
        try:
            bug = BugDetails.objects.get(sl_id=bug_id)
            if bug.Comments is None:
                bug.Comments = []
            bug.Comments.append(comment)
            bug.save()
            return JsonResponse({'message': 'Comment added successfully'}, status=200)
        except BugDetails.DoesNotExist:
            return JsonResponse({'error': 'Bug not found'}, status=404)
@api_view(['POST'])
def add_student_comment(request):
    try:
        bug_id = request.data.get('bug_id')
        student_id = request.data.get('student_id')
        comment = request.data.get('comment')
       
        # Convert UTC time to IST
        utc_time = timezone.now()
        ist_time = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
       
        if not bug_id or not student_id or not comment:
            return Response({"error": "Bug ID, Student ID, and comment are required"}, status=status.HTTP_400_BAD_REQUEST)
       
        bug = BugDetails.objects.get(sl_id=bug_id)
        if bug.Comments is None:
            bug.Comments = {}
       
        student_comments_count = sum(1 for key in bug.Comments.keys() if key.startswith('stu'))
        next_student_key = f'stu{student_comments_count + 1}'  # e.g., stu1, stu2, etc.
       
        bug.Comments[next_student_key] = {
            "role": "student",
            "comment": comment,
            "timestamp": ist_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        bug.save()
       
        return Response({"message": "Student comment added successfully"}, status=status.HTTP_200_OK)
   
    except BugDetails.DoesNotExist:
        return Response({"error": "Bug not found"}, status=status.HTTP_404_NOT_FOUND)
 
 
@api_view(['POST'])
def add_trainer_comment(request):
    try:
        bug_id = request.data.get('bug_id')
        trainer_id = request.data.get('trainer_id')
        comment = request.data.get('comment')
        utc_time = timezone.now()
        ist_time = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
       
        if not bug_id or not trainer_id or not comment:
            return Response({"error": "Bug ID, Trainer ID, and comment are required"}, status=status.HTTP_400_BAD_REQUEST)
       
        bug = BugDetails.objects.get(sl_id=bug_id)
        if bug.Comments is None:
            bug.Comments = {}
       
        trainer_comments_count = sum(1 for key in bug.Comments.keys() if key.startswith('tra'))
        next_trainer_key = f'tra{trainer_comments_count + 1}'  # e.g., tra1, tra2, etc.
       
        bug.Comments[next_trainer_key] = {
            "role": "trainer",
            "comment": comment,
            "timestamp": ist_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        bug.save()
       
        return Response({"message": "Trainer comment added successfully"}, status=status.HTTP_200_OK)
   
    except BugDetails.DoesNotExist:
        return Response({"error": "Bug not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def resolve_bug(request):
    try:
        sl_id = request.data.get('sl_id')
        trainer_id = request.data.get('trainer_id')
        if not sl_id or not trainer_id:
            return Response({"error": "Bug ID and Trainer ID are required"}, status=status.HTTP_400_BAD_REQUEST)
        bug = BugDetails.objects.get(sl_id=sl_id)
        bug.BugStatus = 'Resolved'
        utc_time = timezone.now()
        ist_time = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
        bug.Resolved = ist_time
        bug.save()
        return Response({"message": "Bug resolved successfully", "resolved_timestamp": ist_time.strftime('%Y-%m-%d %H:%M:%S')}, status=status.HTTP_200_OK)
    except BugDetails.DoesNotExist:
        return Response({"error": "Bug not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)