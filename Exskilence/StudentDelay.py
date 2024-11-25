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
from datetime import timedelta
@api_view(['GET'])
def send(request, student_id):
    try:
        student_data = StudentDetails.objects.filter(StudentId=student_id).first()
        list_of_course=[]
        if student_data:
            course_time = student_data.Course_Time
            ended_courses = {}
            started_courses={}
            current_time = datetime.now()
            for course, timings in course_time.items():
                start_time = timings['Start']  
                end_time = timings['End']    
                if course=="SQL" or course=="Python":
                    if current_time > start_time:
                        duration = (end_time - start_time).days + 1
                        started_courses[course]={
                            'Start Time':start_time,
                            'days':duration
                        }
                if end_time < current_time:
                    duration = (end_time - start_time).days + 1
                    ended_courses[course] = {
                        'End Time': end_time,
                        'days': duration
                    }
                    list_of_course.append(course)
            response_data = {
                "StudentId": student_data.StudentId,
                "Ended_Courses": ended_courses,
                "list_of_course":list_of_course,
                "Started_Courses":started_courses
            }
        else:
            response_data = {
                "StudentId": student_id,
                "Ended_Courses": {}
            }
        data=no_of_q_ans(response_data)
        return HttpResponse(data, content_type='application/json')
 
    except ValueError as ve:
        # print(f"ValueError: {ve}")
        return HttpResponse({'error': 'Invalid date format'}, status=400)
    except Exception as e:
        # print(e)
        return HttpResponse({'error': str(e)}, status=500)
 
 
def no_of_q_ans(data):
    student_id=data['StudentId']
    ended_courses=data['Ended_Courses']
    list_of_course=data['list_of_course']
    started_courses=data['Started_Courses']
    result={
    }
    days=StudentDetails_Days_Questions.objects.filter(Student_id=student_id).first()
    if days:
        for course in list_of_course:
            total_days = ended_courses.get(course, {}).get('days', 0)
            if course=="HTMLCSS":
                if (len(days.Qns_lists.get(course,[]))==len(days.Ans_lists.get("HTML",[])) ):
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
 
            if course=="Java_Script" :
 
                course_len=len(days.Qns_lists.get(course,[]))
                if (course_len==len(days.Ans_lists.get(course,[]))):
                    ex={
                        "StudentId":student_id,
                        "Course":course,
                        "End_time":ended_courses.get(course, {}).get('End Time', 0)
                    }
                    delay=last_submit(ex)
                    result[course]={
                        'total_days':total_days-1,
                        'delay':delay,
                    }
                else:
                    delay=compare_w_current(ended_courses[course]['End Time'])
                    result[course]={
                        'total_days':total_days-1,
                        'delay':delay,
                    }
 
 
        for course in started_courses:
            if course=="Python":
                python_end = [
                    "2024-11-15", "2024-11-16", "2024-11-24", "2024-11-24",
                    "2024-11-25", "2024-11-26", "2024-11-27", "2024-11-28",
                    "2024-11-29", "2024-11-30"
                ]
                python_days=[1,1,8,8,1,1,1,1,1,1]
                last = datetime.strptime(python_end[9], "%Y-%m-%d")
                current=datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
                current=datetime.strptime(str(current).split(' ')[0],"%Y-%m-%d")
                no=0
                for time in python_end:
                    last = datetime.strptime(time, "%Y-%m-%d")
                    if last<current:
                        no+=1
                print('no',no)
                if no>10:
                    no=10
                jam={}
                for i in range(no):
                    d=course+'_Day_'+str(i+1)
                    if d=="Python_Day_3" or d=="Python_Day_4":
                        jam[d]={
                            'total_days':'N/A',
                            'delay':"N/A"
                        }
                        result[d]=jam[d]
                        continue
                   
 
                    current=datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
 
                    current=datetime.strptime(str(current).split(' ')[0],"%Y-%m-%d")
                    # print("current",current)
                    time=started_courses[course]['Start Time']
                    end_time=python_end[i]
                    end_time=datetime.strptime(str(end_time).split(' ')[0], "%Y-%m-%d")
                    existing=datetime.strptime(str(time).split(' ')[0], "%Y-%m-%d")
                    d_days=(current-end_time).days
                    if d == "Python_Day_1" or d == "Python_Day_2":
                         mindays= 6
                         jam[d] = {
                            'total_days': python_days[i],
                            'delay':  d_days - mindays
                        }
                    else:
                        jam[d]={
                            'total_days':python_days[i],
                            'delay':d_days
                        }
                    result[d]=jam[d]
 
                    if d in days.Qns_lists and d in days.Ans_lists:
                        if len(days.Qns_lists[d]) == len(days.Ans_lists[d]):
                            st_time = days.End_Course.get(d,'')
                            end_time = datetime.strptime(python_end[i], "%Y-%m-%d")
                            if str(d).split('_')[-1] == '1' or str(d).split('_')[-1] == '2':
                                if str(st_time).split(' ')[0] >='2024-11-19' and str(st_time).split(' ')[0] <='2024-11-24':
                                    st_time=datetime.strptime(str('2024-11-18'), "%Y-%m-%d")
                                else:
                                    if str(st_time).split(' ')[0] <='2024-11-18'  :
                                        pass
                                    else:
                                        print( int(str(st_time).split(' ')[0].split('-')[-1]),int('2024-11-24'.split('-')[-1]))
                                        updated_time = st_time - timedelta(days=(6))
                                        st_time=updated_time
                                    
                            if end_time<st_time:
                                    print('f')
                                    delays=(st_time-end_time).days
                                    print(st_time,end_time)
                                    jam[d]['delay'] = delays
                                    result[d]['delay'] = delays
                            else:  
                                delays = "N/A"
                                jam[d]['delay'] = delays
                                result[d]['delay'] = delays
                           
         
            elif course=="SQL":
                start=started_courses[course]['Start Time']
                no=compare_w_current(start)
                if no>10:
                    no=10
                jam={}
                for i in range(no):
                    d=course+'_Day_'+str(i+1)
                    current=datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
 
                    current=datetime.strptime(str(current).split(' ')[0],"%Y-%m-%d")
                    time=started_courses[course]['Start Time']
                    existing=datetime.strptime(str(time).split(' ')[0], "%Y-%m-%d")
                    d_days=(current-existing).days
                    jam[d]={
                        "delay": d_days-(i),
                        "total_days":1
                    }
                    result[d]=jam[d]
               
                    if d in days.Qns_lists and d in days.Ans_lists:
                        if len(days.Qns_lists[d]) == len(days.Ans_lists[d]):
                            time = days.End_Course[d]
                            updated_time = start + timedelta(days=(i + 1))
                            # print('sdsf', start)
                            if updated_time < time:
                                delays = (time - updated_time).days + 1  
                            else:  
                                delays = 0
                            jam[d]['delay'] = delays
                            result[d]['delay'] = delays
 
    out ={
        "HTMLCSS":result.get("HTMLCSS",{}),
        "Java_Script":result.get("Java_Script",{}),
    }
    for key in result.keys():
         if key!="HTMLCSS" and key!="Java_Script":
             out.update( {key:result.get(key,0)} )
    return HttpResponse(json.dumps(out), content_type='application/json')
 
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
       
        if (end-existing).days>0:
            delay="N/A"
        elif (end-existing).days<0:
            delay=(existing-end).days
    return delay