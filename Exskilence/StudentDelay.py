from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from .models import *
from rest_framework import viewsets
from rest_framework.response import Response
import json
from rest_framework.decorators import api_view
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json
from django.http import HttpResponse
@api_view(['GET'])
def send(request, student_id):
    try:
        student_data = StudentDetails.objects.filter(StudentId=student_id).first()
        list_of_course=[]
        if student_data:
            course_time = student_data.Course_Time
            ended_courses = {}
            current_time = datetime.now()
            for course, timings in course_time.items():
                start_time = timings['Start']  
                end_time = timings['End']      
                if end_time < current_time:
                    duration = (end_time - start_time).days
                    ended_courses[course] = {
                        'End Time': end_time,
                        'days': duration
                    }
                    list_of_course.append(course)
            response_data = {
                "StudentId": student_data.StudentId,
                "Ended_Courses": ended_courses,
                "list_of_course":list_of_course
            }
        else:
            response_data = {
                "StudentId": student_id,
                "Ended_Courses": {}
            }
       
        data=no_of_q_ans(response_data)
        return HttpResponse(data, content_type='application/json')
 
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return HttpResponse({'error': 'Invalid date format'}, status=400)
    except Exception as e:
        print(e)
        return HttpResponse({'error': str(e)}, status=500)
 
 
def no_of_q_ans(data):
    student_id=data['StudentId']
    ended_courses=data['Ended_Courses']
    list_of_course=data['list_of_course']
    result={
    }
    days=StudentDetails_Days_Questions.objects.filter(Student_id=student_id).first()
    if days:
        for course in list_of_course:
            total_days = ended_courses.get(course, {}).get('days', 0) +1
            if course=="HTMLCSS":
                if (len(days.Qns_lists[course])==len(days.Ans_lists["HTML"])):
                    ex={
                        "StudentId":student_id,
                        "Course":course,
                        "End_time":ended_courses.get(course, {}).get('End Time', 0)
                    }
                    delay=last_submit(ex)
                    result[course]={
                        'total_days':total_days,
                        'delay':delay,
                    }
                else:
                    delay=compare_w_current(ended_courses[course]['End Time'])
                    result[course]={
                        'total_days':total_days,
                        'delay':delay,
                    }
            if course in days.Qns_lists and course in days.Ans_lists:
                course_len=len(days.Qns_lists[course])
                if (course_len==len(days.Ans_lists[course])):
                    ex={
                        "StudentId":student_id,
                        "Course":course,
                        "End_time":ended_courses.get(course, {}).get('End Time', 0)
                    }
                    delay=last_submit(ex)
                    result[course]={
                        'total_days':total_days,
                        'delay':delay,
                    }
                else:
                    delay=compare_w_current(ended_courses[course]['End Time'])
                    result[course]={
                        'total_days':total_days,
                        'delayexist':delay,
                    }
    return HttpResponse(json.dumps(result), content_type='application/json')
 
def compare_w_current(time):
    current=datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
    current=datetime.strptime(str(current).split(' ')[0],"%Y-%m-%d")
    existing=datetime.strptime(str(time).split(' ')[0], "%Y-%m-%d")
   
    return ((current-existing).days)
 
def last_submit(ex):
    student_id = ex['StudentId']
    all_submissions = QuestionDetails_Days.objects.filter(Student_id=student_id)
    recent_times = []
    course=ex['Course']
    delay=0
    if all_submissions:
        current_course = "HTML" if course == "HTMLCSS" else course
        for submission in all_submissions:
            if submission.Subject == current_course:
                submission_time = submission.DateAndTime
                recent_times.append(submission_time)
    if recent_times:
        recent_time = max(recent_times)
        current=datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
        current=datetime.strptime(str(current).split(' ')[0],"%Y-%m-%d")
        existing=datetime.strptime(str(recent_time).split(' ')[0], "%Y-%m-%d")
        end=ex['End_time']
        end=datetime.strptime(str(end).split(' ')[0], "%Y-%m-%d")
       
        if (end-existing).days>=0:
            delay="N/A"
        elif (end-existing).days<0:
            delay=(existing-end).days
    return delay
 