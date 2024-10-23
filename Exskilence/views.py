import calendar
from decimal import Decimal
import json
import math
import random
import re
from django.http import HttpResponse
from Exskilencebackend160924.settings import *
from rest_framework.decorators import api_view
from datetime import date, datetime, time, timedelta
from Exskilence.models import *
from Exskilencebackend160924.Blob_service import download_blob2, get_blob_service_client, download_list_blob2
import pyodbc
from Exskilence.sqlrun import *
from django.core.cache import cache
from Exskilence.filters import *
from Exskilence.ErrorLog import ErrorLog
from Exskilence.Ranking import *
CONTAINER ="internship"
# Create your views here.
from Exskilence.Attendance import attendance_create_login, attendance_update

@api_view(['GET'])   
def home(request):
    return HttpResponse("Welcome to the Home Page of Exskilence 26" )


@api_view(['POST'])
def fetch(request):
    try:
        data = request.body
        data = json.loads(data)
        if request.method == "POST": 
            user = login_data.objects.get(User_emailID=data.get('Email'))
            if user:
                bodydata = str(request.META) .replace('\'','"')
                if attendance_create_login( user.User_ID) == "First":
                    return HttpResponse(json.dumps({ "StudentId" : str(user.User_ID),"user_category" : user.User_catagory ,'Overview' : True ,'Body' : bodydata}), content_type='application/json')
                else:
                    return HttpResponse(json.dumps({ "StudentId" : str(user.User_ID),"user_category" : user.User_catagory ,'Overview' : False, 'Body' : bodydata}), content_type='application/json')                   
            else:
                return HttpResponse('Error! User does not exist', status=404)
        else :
            return HttpResponse('Error! Invalid Request',status=400)
    except Exception as e:
        ErrorLog(request,e)
        return HttpResponse('Error! User does not exist', status=404)
@api_view(['POST']) 
def logout(request):
    try:
        data = request.body
        data = json.loads(data)
        user = Attendance.objects.filter(SID=data.get('StudentId')).order_by('-Login_time').first()
        if user is not None:
            user.Last_update = datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
            user.Status = "out"
            user.save()

        return HttpResponse(json.dumps({'Logout': 'Success'}), content_type='application/json')
    except Exception as e:
        ErrorLog(request,e)
        print(e)
        return HttpResponse(f"An error occurred: {e}", status=500)
def subScore(user,course):
    try:    
        score = 0
        for i in dict(user).keys():
            if str(i).startswith(course):
                Qnlists = dict(user)[i]
                for j in Qnlists:
                    if str(j)[-4] == 'E':
                        score += 5
                    elif str(j)[-4] == 'M':
                        score += 10
                    elif str(j)[-4] == 'H':
                        score += 15
        return score
    except Exception as e:
        print(e)
        return f"An error occurred: {e}"
@api_view(['POST'])
def get_duration(req):
    try:
        data = json.loads(req.body)
        start = data.get("Start")
        end = data.get("End")
        Startmost = datetime.strptime(start, '%Y-%m-%d')
        Endmost = datetime.strptime(end, '%Y-%m-%d').__add__(timedelta(hours=23,minutes=59))
        spent = Attendance.objects.filter(SID=data.get('StudentId')).filter(Login_time__range=[Startmost, Endmost],Last_update__range=[Startmost, Endmost])  
        Duration = 0 
        if spent:
                for i in spent:
                    Duration = Duration + (i.Last_update - i.Login_time).total_seconds()
        # print(Duration )
        return HttpResponse(json.dumps({"Duration": Duration}), content_type='application/json')
    except Exception as e:
        ErrorLog(req,e)
        return HttpResponse(f"An error occurred: {e}", status=500)

 
@api_view(['POST'])
def getcourse(req):
    try:
        data = json.loads(req.body)
        allusers = StudentDetails.objects.all()
        allusersranks = StudentDetails_Days_Questions.objects.all()
        userscore = None
        for i in allusersranks:
            if i.Student_id == data.get('StudentId'):
                userscore = i
                break
        if userscore is None:
            return HttpResponse('Error! User does not exist', status=404)
        for u in allusers:
            if u.StudentId == data.get('StudentId'):
                user = u
                break
        courseinfo ={}
        for i in user.Courses:
            if userscore.Qns_lists.get(i, None) is None:
                courseinfo.update({i: True})
            else:
                courseinfo.update({i: False})
        Scolist = [str(l).replace("Score","") for l in list(userscore.Score_lists.keys())]
        if Scolist.__contains__("HTML") or Scolist.__contains__("CSS"):
            if Scolist.__contains__("HTML"):
                Scolist.remove("HTML")
            if Scolist.__contains__("CSS"):
                Scolist.remove("CSS")
            Scolist.append("HTMLCSS")
        if len(Scolist)  != len(user.Courses):
            for i in user.Courses:
                if i == "HTMLCSS":
                    if userscore.Score_lists.get("HTMLScore",None) is None:
                        userscore.Score_lists.update({ "HTMLScore":"0/0"})
                    if userscore.Score_lists.get("CSSScore",None) is None:
                        userscore.Score_lists.update({ "CSSScore":"0/0"})
                else:
                    if userscore.Score_lists.get(str(i)+"Score",None) is None:
                        userscore.Score_lists.update({str(i)+"Score":"0/0"})
            userscore.save()
        out = {}
        Rank = {}
        intcourse ={
            "Sub":[],
            "SubScore":[],
            "Score":[],
        }
        Enrolled_courses = []
        Total_Score = 0
        Total_Score_Outof = 0
        Startmost =datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
        Endmost = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
        if user:
            def getdays(date):
                    date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
                    day = int(date.strftime("%d"))
                    month = int(date.strftime("%m"))
                    if 4 <= day <= 20 or 24 <= day <= 30:
                        suffix = "th"
                    else:
                        suffix = ["st", "nd", "rd"][day % 10 - 1]
                    formatted_date =  (f"{day}{suffix} {calendar.month_abbr[month]}")
                    return formatted_date
            courses=CourseDetails.objects.filter().order_by('SubjectId').values()
            timestart = user.Course_Time
            for course in courses:
                if course.get('SubjectName') in user.Courses  :
                    starttime = timestart.get(course.get('SubjectName')).get('Start')
                    endtime = timestart.get(course.get('SubjectName')).get('End')
                    if course.get('SubjectName') == "HTMLCSS":
                        Enrolled_courses.append({
                        "SubjectId":course.get('SubjectId')  ,
                        "SubjectName":course.get('SubjectName') ,
                        "Name":course.get('Discription')  ,
                        "Duration":str(getdays(starttime))+" to "+str(getdays(endtime)) ,
                        'Progress':str(round(len(userscore.Ans_lists.get(course.get('SubjectName'),[])if course.get('SubjectName') != "HTMLCSS" else userscore.Ans_lists.get("HTML",[] ))/len(userscore.Qns_lists.get(course.get('SubjectName'),[]))*100))+"%" if len(userscore.Qns_lists.get(course.get('SubjectName'),[])) != 0 else '0%',
                        'Assignment':str(len(userscore.Ans_lists.get(course.get('SubjectName'),[])if course.get('SubjectName') != "HTMLCSS" else userscore.Ans_lists.get("HTML",[] )))+"/"+str(len(userscore.Qns_lists.get(course.get('SubjectName'),[]))),
                        "Status" : 'Opened' if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow().__add__(timedelta(hours=5,minutes=30)) and datetime.strptime(str(endtime).split(" ")[0], "%Y-%m-%d").__add__(timedelta(hours=23,minutes=59,seconds=59)) > datetime.utcnow().__add__(timedelta(hours=5,minutes=30)) else 'Opened' if datetime.strptime(str(endtime).split(" ")[0], "%Y-%m-%d").__add__(timedelta(hours=23,minutes=59,seconds=59)) < datetime.utcnow().__add__(timedelta(hours=5,minutes=30)) else 'Closed',
                        'CourseInfo':courseinfo.get(course.get('SubjectName'))
                        })
                        if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow().__add__(timedelta(hours=5,minutes=30)):
                            intcourse.get('Sub').append("HTMLCSS")
                            htmldata=userscore.Score_lists.get("HTMLScore").split('/')
                            cssdata=userscore.Score_lists.get("CSSScore").split('/')
                            intcourse.get('SubScore').append(str(round(float((float(htmldata[0])+float(cssdata[0]))/2),2))+"/"+str(subScore(userscore.Qns_lists,"HTMLCSS")))
                            Total_Score = float(Total_Score) + float(intcourse.get('SubScore')[-1].split('/')[0])
                            Total_Score_Outof = int(Total_Score_Outof) + int(intcourse.get('SubScore')[-1].split('/')[1])
 
                    else:
                        courseprogressTotalQns = userscore.Qns_lists
                        numQns = [len(courseprogressTotalQns.get(i)) for i in dict(courseprogressTotalQns).keys() if str(i).startswith(course.get('SubjectName'))]
                        numAns = [len(userscore.Ans_lists.get(i)) for i in dict(userscore.Ans_lists).keys() if str(i).startswith(course.get('SubjectName'))]
                        Enrolled_courses.append({
                        "SubjectId":course.get('SubjectId')  ,
                        "SubjectName":course.get('SubjectName') ,
                        "Name":course.get('Discription')  ,
                        "Duration":str(getdays(starttime))+" to "+str(getdays(endtime)) ,
                        'Progress': str(round(sum(numAns)/sum(numQns)*100))+'%' if sum(numQns)!= 0 else "0%" ,
                        'Assignment':str(sum(numAns))+"/"+str(sum(numQns)),
                        "Status" : 'Opened' if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow().__add__(timedelta(hours=5,minutes=30)) and datetime.strptime(str(endtime).split(" ")[0], "%Y-%m-%d").__add__(timedelta(hours=23,minutes=59,seconds=59)) > datetime.utcnow().__add__(timedelta(hours=5,minutes=30)) else 'Closed'
                        })
                        if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow().__add__(timedelta(hours=5,minutes=30)):
                            intcourse.get('Sub').append(course.get('SubjectName'))
                            intcourse.get('SubScore').append(str(round(float(str(userscore.Score_lists.get(str(course.get('SubjectName'))+'Score')).split('/')[0]),2))+"/"+str(subScore(userscore.Qns_lists,course.get('SubjectName'))))
                            Total_Score = float(Total_Score) + float(intcourse.get('SubScore')[-1].split('/')[0])
                            Total_Score_Outof = int(Total_Score_Outof) + int(intcourse.get('SubScore')[-1].split('/')[1])
                    if Startmost > starttime:
                        Startmost = starttime
                    Rank.update({course.get('SubjectName'):getRankings(course.get('SubjectName'), data.get('StudentId'))})
            spent = Attendance.objects.filter(SID=data.get('StudentId')).filter(Login_time__range=[Startmost, Endmost],Last_update__range=[Startmost, Endmost])  
            Duration = 0
            if spent:
                for i in spent:
                    Duration = Duration + (i.Last_update - i.Login_time).total_seconds()
            intcourse.get('Score').append(str(Total_Score)+"/"+str(Total_Score_Outof))
            Total_Rank = totalRanks( data.get('StudentId'))
            # ranking= rankings(filterQueryTodict(allusers))
            # userrank = [ i.get('Rank') for i in ranking  if i.get('StudentId') == data.get('StudentId') ]
            # print(userrank)
            # Rank.update({'HTMLCSS':userrank[0] if userrank else 'N/A'})
            Rank.update({'Total_Rank':Total_Rank})
            out.update({"Courses":Enrolled_courses,
                        "Intenship":intcourse,
                        "Prograss":{
                            "Start_date":str(Startmost).split()[0].split('-')[2]+"-"+str(Startmost).split()[0].split('-')[1]+"-"+str(Startmost).split()[0].split('-')[0],
                            "End_date":str(Endmost).split()[0].split('-')[2]+"-"+str(Endmost).split()[0].split('-')[1]+"-"+str(Endmost).split()[0].split('-')[0],
                            "Duration":Duration
                        },
                        "Rank": Rank,
                        "StudentName":user.firstName})
            user.score =round(float(str(intcourse.get('Score')[0]).split('/')[0]),2)
            user.save()
            # attendance_update(data.get('StudentId'))
            return HttpResponse(json.dumps(out), content_type='application/json')
        else:
            # attendance_update(data.get('StudentId'))
            return HttpResponse('Error! User does not exist', status=404)
    except Exception as e:
        # ErrorLog(req,e)
        # attendance_update(data.get('StudentId'))
        return HttpResponse(f"An error occurred: {e}", status=500)


# @api_view(['POST'])
# def getcourse(req):
#     try:
#         start_time = datetime.utcnow().__add__(timedelta(hours=5,minutes=30))

#         data = json.loads(req.body)
#         db_start_time =  datetime.utcnow().__add__(timedelta(hours=5,minutes=30))

#         allusers = StudentDetails.objects.all()
#         allusersranks = StudentDetails_Days_Questions.objects.all()

#         db_end_time = datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
#         db_time = (db_end_time - db_start_time).total_seconds()

#         userscore = None
#         for i in allusersranks:
#             if i.Student_id == data.get('StudentId'):
#                 userscore = i
#                 break

#         if userscore is None:
#             return HttpResponse('Error! User does not exist', status=404)

#         user = None
#         for u in allusers:
#             if u.StudentId == data.get('StudentId'):
#                 user = u
#                 break

#         courseinfo = {}
#         for i in user.Courses:
#             if userscore.Qns_lists.get(i, None) is None:
#                 courseinfo.update({i: True})
#             else:
#                 courseinfo.update({i: False})

#         Scolist = [str(l).replace("Score", "") for l in list(userscore.Score_lists.keys())]
#         if "HTML" in Scolist or "CSS" in Scolist:
#             if "HTML" in Scolist:
#                 Scolist.remove("HTML")
#             if "CSS" in Scolist:
#                 Scolist.remove("CSS")
#             Scolist.append("HTMLCSS")

#         if len(Scolist) != len(user.Courses):
#             for i in user.Courses:
#                 if i == "HTMLCSS":
#                     if userscore.Score_lists.get("HTMLScore", None) is None:
#                         userscore.Score_lists.update({"HTMLScore": "0/0"})
#                     if userscore.Score_lists.get("CSSScore", None) is None:
#                         userscore.Score_lists.update({"CSSScore": "0/0"})
#                 else:
#                     if userscore.Score_lists.get(str(i) + "Score", None) is None:
#                         userscore.Score_lists.update({str(i) + "Score": "0/0"})
#             db_start_time =  datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
#             userscore.save()
#             db_end_time = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#             db_time = (db_end_time - db_start_time).total_seconds()+db_time

#         out = {}
#         Rank = {}
#         intcourse = {
#             "Sub": [],
#             "SubScore": [],
#             "Score": [],
#         }
#         Enrolled_courses = []
#         Total_Score = 0
#         Total_Score_Outof = 0
#         Startmost = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#         Endmost = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))

#         if user:
#             def getdays(date):
#                 date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
#                 day = int(date.strftime("%d"))
#                 month = int(date.strftime("%m"))
#                 if 4 <= day <= 20 or 24 <= day <= 30:
#                     suffix = "th"
#                 else:
#                     suffix = ["st", "nd", "rd"][day % 10 - 1]
#                 formatted_date = (f"{day}{suffix} {calendar.month_abbr[month]}")
#                 return formatted_date

#             db_start_time =  datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#             courses = CourseDetails.objects.filter().order_by('SubjectId').values()
#             db_end_time = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#             db_time = (db_end_time - db_start_time).total_seconds()+db_time
#             timestart = user.Course_Time
#             for course in courses:
#                 if course.get('SubjectName') in user.Courses:
#                     starttime = timestart.get(course.get('SubjectName')).get('Start')
#                     endtime = timestart.get(course.get('SubjectName')).get('End')

#                     if course.get('SubjectName') == "HTMLCSS":
#                         Enrolled_courses.append({
#                             "SubjectId": course.get('SubjectId'),
#                             "SubjectName": course.get('SubjectName'),
#                             "Name": course.get('Discription'),
#                             "Duration": str(getdays(starttime)) + " to " + str(getdays(endtime)),
#                             'Progress': str(round(len(userscore.Ans_lists.get(course.get('SubjectName'), [])) / len(userscore.Qns_lists.get(course.get('SubjectName'), [])) * 100)) + "%" if len(userscore.Qns_lists.get(course.get('SubjectName'), [])) != 0 else '0%',
#                             'Assignment': str(len(userscore.Ans_lists.get(course.get('SubjectName'), []))) + "/" + str(len(userscore.Qns_lists.get(course.get('SubjectName'), []))),
#                             "Status": 'Opened' if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow() + timedelta(hours=5, minutes=30) and datetime.strptime(str(endtime).split(" ")[0], "%Y-%m-%d").replace(hour=23, minute=59, second=59) > datetime.utcnow() + timedelta(hours=5, minutes=30) else 'Closed',
#                             'CourseInfo': courseinfo.get(course.get('SubjectName'))
#                         })
#                         if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow() + timedelta(hours=5, minutes=30):
#                             intcourse.get('Sub').append("HTMLCSS")
#                             htmldata = userscore.Score_lists.get("HTMLScore").split('/')
#                             cssdata = userscore.Score_lists.get("CSSScore").split('/')
#                             intcourse.get('SubScore').append(str(round(float((float(htmldata[0]) + float(cssdata[0])) / 2), 2)) + "/" + str(subScore(userscore.Qns_lists, "HTMLCSS")))
#                             Total_Score = float(Total_Score) + float(intcourse.get('SubScore')[-1].split('/')[0])
#                             Total_Score_Outof = int(Total_Score_Outof) + int(intcourse.get('SubScore')[-1].split('/')[1])

#                     else:
#                         courseprogressTotalQns = userscore.Qns_lists
#                         numQns = [len(courseprogressTotalQns.get(i)) for i in dict(courseprogressTotalQns).keys() if str(i).startswith(course.get('SubjectName'))]
#                         numAns = [len(userscore.Ans_lists.get(i)) for i in dict(userscore.Ans_lists).keys() if str(i).startswith(course.get('SubjectName'))]
#                         Enrolled_courses.append({
#                             "SubjectId": course.get('SubjectId'),
#                             "SubjectName": course.get('SubjectName'),
#                             "Name": course.get('Discription'),
#                             "Duration": str(getdays(starttime)) + " to " + str(getdays(endtime)),
#                             'Progress': str(round(sum(numAns) / sum(numQns) * 100)) + '%' if sum(numQns) != 0 else "0%",
#                             'Assignment': str(sum(numAns)) + "/" + str(sum(numQns)),
#                             "Status": 'Opened' if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow() + timedelta(hours=5, minutes=30) and datetime.strptime(str(endtime).split(" ")[0], "%Y-%m-%d").replace(hour=23, minute=59, second=59) > datetime.utcnow() + timedelta(hours=5, minutes=30) else 'Closed'
#                         })
#                         if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow() + timedelta(hours=5, minutes=30):
#                             intcourse.get('Sub').append(course.get('SubjectName'))
#                             intcourse.get('SubScore').append(str(round(float(str(userscore.Score_lists.get(str(course.get('SubjectName')) + 'Score')).split('/')[0]), 2)) + "/" + str(subScore(userscore.Qns_lists, course.get('SubjectName'))))
#                             Total_Score = float(Total_Score) + float(intcourse.get('SubScore')[-1].split('/')[0])
#                             Total_Score_Outof = int(Total_Score_Outof) + int(intcourse.get('SubScore')[-1].split('/')[1])
#                     if Startmost > starttime:
#                         Startmost = starttime
#             db_start_time = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#             spent = Attendance.objects.filter(SID=data.get('StudentId')).filter(Login_time__range=[Startmost, Endmost], Last_update__range=[Startmost, Endmost])
#             db_end_time = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#             db_time = (db_end_time - db_start_time).total_seconds()+db_time
#             Duration = 0
#             if spent:
#                 for i in spent:
#                     Duration = Duration + (i.Last_update - i.Login_time).total_seconds()

#             intcourse.get('Score').append(str(Total_Score) + "/" + str(Total_Score_Outof))
#             db_start_time = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#             Total_Rank = getRanks(allusersranks, data.get('StudentId'))
#             ranking = rankings(filterQueryTodict(allusers))
#             db_end_time = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#             db_time = (db_end_time - db_start_time).total_seconds()+db_time
#             userrank = [i.get('Rank') for i in ranking if i.get('StudentId') == data.get('StudentId')]
#             Rank.update({'HTMLCSS': userrank[0] if userrank else 'N/A'})
#             Rank.update({'Total_Rank': Total_Rank})

#             out.update({
#                 "Courses": Enrolled_courses,
#                 "Intenship": intcourse,
#                 "Prograss": {
#                     "Start_date": str(Startmost).split()[0].split('-')[2] + "-" + str(Startmost).split()[0].split('-')[1] + "-" + str(Startmost).split()[0].split('-')[0],
#                     "End_date": str(Endmost).split()[0].split('-')[2] + "-" + str(Endmost).split()[0].split('-')[1] + "-" + str(Endmost).split()[0].split('-')[0],
#                     "Duration": Duration
#                 },
#                 "Rank": Rank,
#                 "StudentName": user.firstName
#             })

#             user.score = round(float(str(intcourse.get('Score')[0]).split('/')[0]), 2)
#             db_start_time = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#             user.save()
#             db_end_time = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#             db_time = (db_end_time - db_start_time).total_seconds()+db_time
#             attendance_update(data.get('StudentId'))

#             end_time = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
#             method_time = (end_time - start_time).total_seconds()
#             overall_time = (db_time + method_time) 

#             out.update({
#                 "db_time": db_time,
#                 "method_time": method_time,
#                 "overall_time": overall_time
#             })

#             return HttpResponse(json.dumps(out), content_type='application/json')
#         else:
#             attendance_update(data.get('StudentId'))
#             return HttpResponse('Error! User does not exist', status=404)
#     except Exception as e:
#         return HttpResponse(f"An error occurred: {e}", status=500)
@api_view(['POST'])
def courseInfo(request):
    try:
        data = request.body
        data = json.loads(data)
        json_content = json.loads(download_blob("Concept/course/Info_Json/"+str(data.get('CourseName')).replace(' ','')+".json"))
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps(json_content), content_type='application/json')
    except Exception as e:
        ErrorLog(request,e)
        attendance_update(data.get('StudentId'))
        return HttpResponse('Server Error! Please Try Again Later',status=500)

@api_view(['POST'])
def getdays(req):
    try:
        data =json.loads(req.body)
        blob_data = download_blob2('Internship_days_schema/'+data.get('Course')+'/Days.json',CONTAINER)
        json_content = json.loads(blob_data)
        user ,created = StudentDetails_Days_Questions.objects.get_or_create(Student_id = data.get('StudentId'),
            defaults = {'Start_Course':{data.get('Course'):str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))},
                        'Days_completed':{data.get('Course'):0},
                        'Qns_lists':{ },
                        'Qns_status':{ },
                        'Ans_lists':{ },
                        'Score_lists':{data.get('Course')+'Score':"0/0"}})
        QNans = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId'),Subject = data.get('Course')).all() 
        ScoreList =[]
        if user:
            if user.Start_Course.get(data.get('Course'),0) == 0:
                for day in range(1,json_content.get('Total_Days')+1):
                    qnsdata = download_list_blob2('Internship_days_schema/'+data.get('Course')+'/Day_'+str(day)+'/','',CONTAINER)
                    user.Qns_lists.update({data.get('Course')+'_Day_'+str(day):random.sample([j.get('Qn_name') for j in qnsdata], len(qnsdata))})
                    user.Qns_status.update({data.get('Course')+'_Day_'+str(day):{i:0 for i in user.Qns_lists.get(data.get('Course')+'_Day_'+str(day))}})
                user.Start_Course.update({data.get('Course'):str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))})
                user.Days_completed.update({data.get('Course'):0})
                user.Score_lists.update({data.get('Course')+'Score':"0/0"})
                user.save()
            for i in range(json_content.get('Total_Days')): 
                    dayscore =getDaysScore(data.get('Course'),user,QNans,i+1)
                    ScoreList.append({'Score':dayscore[0],'Qn_Ans':dayscore[1]})            
        daysdata = json_content.get('Days')
        date_obj = datetime.strptime(user.Start_Course.get(data.get('Course'),str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))), "%Y-%m-%d %H:%M:%S.%f")
        for i in daysdata:
            Uqnlist =user.Qns_lists.get(data.get('Course')+'_Day_'+str(i.get('Day_no')).split('-')[1],[]) 
            Uanslist =user.Ans_lists.get(data.get('Course')+'_Day_'+str(i.get('Day_no')).split('-')[1],[])

            if int (str(i.get('Day_no')).split('-')[1]) > user.Days_completed.get(data.get('Course'),0)+1:
                Status ="Locked"
            elif int (str(i.get('Day_no')).split('-')[1]) == user.Days_completed.get(data.get('Course'),0) +1 :
                if len(Uanslist) == 0:
                    Status ="Start"
                else:
                    Status ="In Progress"
            elif len(Uqnlist) == len(Uanslist) :
                Status ="Done"
            elif len(Uqnlist) != len(Uanslist) and int (str(i.get('Day_no')).split('-')[1]) < user.Days_completed.get(data.get('Course'),0)+1:
                Status ="Attempted"
            else:
                Status ="Locked"
            i.update({'Due_date':str(date_obj.__add__(timedelta(hours=24,minutes=00)).strftime("%d-%m-%Y")).split(' ')[0],
                      'Status':Status
                      })
            date_obj = date_obj.__add__(timedelta(hours=24,minutes=00))
        json_content.update({'Days':daysdata})
        date_obj = datetime.strptime(date_obj.__add__(timedelta(hours=24,minutes=00)).strftime("%Y-%m-%d"),"%Y-%m-%d")
        current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        json_content.update({'Days_left' : (date_obj - current_time).days if (date_obj - current_time).days > 0 else 0,
                'Day_User_on' : user.Days_completed.get(data.get('Course'),0),
                'ScoreList':ScoreList 
                })
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps(json_content), content_type='application/json')
    except Exception as e:
        ErrorLog(req ,e) 
        attendance_update(data.get('StudentId'))
        return HttpResponse(f"An error occurred: {e}", status=500)


def getDaysScore(Course,user,Qnslists,day):

    try:
        anslists = user.Ans_lists.get(Course+'_Day_'+str(day),[])
        Qnnams = user.Qns_lists.get(Course+'_Day_'+str(day),[])
        levels = [str(i)[-4] for i in Qnnams]
        
        TotalScore = levels.count('E')*5+levels.count('M')*10+levels.count('H')*15
        score = 0
        if anslists:
            for i in  Qnslists :
                if i.Qn in anslists:
                    score += i.Score
        return [str(score)+'/'+str(TotalScore),str(len(anslists))+'/'+str(len(Qnnams))]
    except Exception as e:  
        return f"An error occurred: {e}"
    
def createStdQnDays(data):
    try:
            user = StudentDetails_Days_Questions.objects.create(
                Student_id = data.get('StudentId'),
                Start_Course = {data.get('Course'):str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))},
                Days_completed = {data.get('Course'):0},
                Qns_lists = { },
                Qns_status = { },
                Ans_lists = { },
                Score_lists = {data.get('Course')+'Score':"0/0"}  )
                
            return user
    except Exception as e:
        return f"An error occurred: {e}"
@api_view(['POST'])
def getQnslist(req):
    try:
        data =json.loads(req.body)
        course = data.get('Course')
        qnsdata = download_list_blob2('Internship_days_schema/'+course+'/Day_'+str(data.get('Day'))+'/','',CONTAINER)
        anslist = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId'),Subject = course).all()
        user,created = StudentDetails_Days_Questions.objects.get_or_create(Student_id = data.get('StudentId'),
            defaults = {'Start_Course':{data.get('Course'):str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))},
                        'Days_completed':{data.get('Course'):0},
                        'Qns_lists':{ },
                        'Qns_status':{ },
                        'Ans_lists':{ },
                        'Score_lists':{data.get('Course')+'Score':"0/0"}})
        Qlist = user.Qns_lists.get(course+'_Day_'+str(data.get('Day')),None)
        if user.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))) is None:
            user.Qns_status.update({data.get('Course')+'_Day_'+str(data.get('Day')):{}})
        if Qlist is None:
            user.Qns_lists.update({data.get('Course')+'_Day_'+str(data.get('Day')):random.sample([j.get('Qn_name') for j in qnsdata], len(qnsdata))})
            user.Qns_status.update({data.get('Course')+'_Day_'+str(data.get('Day')):{}})
            user.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))).update({j:0 for j in user.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day')))})
            user.save()
        Qnslist = []
        def getDayScore1(anslist,QName):
            u = anslist.filter(Qn = QName).first()
            if u:
                return u.Score
            return 0
        def getDayScore(anslist,QName):
            if len(anslist) == 0:
                return 0
            if anslist[0].get('Qn')==QName:
                u = anslist[0]
            else:
                u = None
            if u:
                return  u.get('Score')
            return 0
        for i in qnsdata:
            level = str(i.get("Qn_name"))[-4]
            outof =''
            if level == 'E':
                level = 1
                outof = 5
            elif level == 'M':
                level = 2
                outof = 10
            elif level == 'H':
                level = 3
                outof = 15
            Qnslist.append({"Level":level,
                            "Qn_name":i.get("Qn_name"),
                            "Qn":i.get("Qn"),
                            "Status":user.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))).get(i.get("Qn_name")),
                            # "Score":str(getDayScore(anslist,i.get("Qn_name")))+'/'+str(outof)})
                            "Score":str(getDayScore(filterQuery(anslist,'Qn',i.get("Qn_name")),i.get("Qn_name")))+'/'+str(outof)})
        
        if Qlist:
            arranged_list = sorted(Qnslist, key=lambda x: Qlist.index(x['Qn_name']))
            Qnslist = arranged_list
        out = {}
        dayinfo = getDaysScore(data.get('Course'),user,anslist,data.get('Day'))
        out.update({
            'Qnslist' : Qnslist,
            'Day_Score' : dayinfo[0],
            'Completed' : dayinfo[1],
        })
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps(out), content_type='application/json')
    
    except Exception as e:
        ErrorLog(req ,e)
        attendance_update(data.get('StudentId'))
        return HttpResponse(f"An error occurred: {e}", status=500)
@api_view(['POST']) 
def getQn(req):
    try:
        data = json.loads(req.body)
        course = data.get('Course')
        mainUser ,created = StudentDetails_Days_Questions.objects.get_or_create(Student_id = data.get('StudentId'),
            defaults = {'Start_Course':{data.get('Course'):str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))},
                        'Days_completed':{data.get('Course'):0},
                        'Qns_lists':{ },
                        'Qns_status':{ },
                        'Ans_lists':{ },
                        'Score_lists':{data.get('Course')+'Score':"0/0"}})
        if mainUser.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))) is None:
            mainUser.Qns_status.update({data.get('Course')+'_Day_'+str(data.get('Day')):{}})
        if mainUser.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))).get(data.get('Qn_name'),0) < 1:
            mainUser.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))).update({data.get('Qn_name'):1})
        if mainUser.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day')),None) is None:
            mainUser.Qns_lists.update({data.get('Course')+'_Day_'+str(data.get('Day')):[]})
        if mainUser.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day'))).count(data.get('Qn_name')) < 1:
            mainUser.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day'))).append(data.get('Qn_name'))
        mainUser.save()
        user = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId'),Subject = course,Qn = data.get('Qn_name')).first()
        qnsdata = download_blob2('Internship_days_schema/'+course+'/Day_'+str(data.get('Day'))+'/'+data.get('Qn_name')+'.json',CONTAINER)
        qnsdata = json.loads(qnsdata)
        qnsdata.update({"Qn_name":data.get('Qn_name'),
                        "Qn_No": int(mainUser.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day'))).index(data.get('Qn_name')))+1,})
        if user:
            qnsdata.update({"UserAns":user.Ans })
            qnsdata.update({"UserSubmited":"Yes" })
        else:
            qnsdata.update({"UserAns":'' })
            qnsdata.update({"UserSubmited":'No' })
        out = {}
        if data.get('Course') == 'SQL':
                tabs =  get_tables(qnsdata.get('Table'))
                out.update({"Tables":tabs,"Question":qnsdata})
        else:
                out.update({"Question":qnsdata})
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps(out), content_type='application/json')

    except Exception as e:
        ErrorLog(req ,e) 
        attendance_update(data.get('StudentId'))
        return HttpResponse(f"An error occurred: {e}", status=500)

@api_view(['POST'])
def submit(request)  :
    data = request.body
    jsondata = json.loads(data)
    try:
        result = add_daysQN_db(jsondata)
        # print('result/*/*/')
        attendance_update(jsondata.get('StudentId'))
        # print('attendance_update')
        return HttpResponse(json.dumps( result), content_type='application/json')
    except Exception as e:
        ErrorLog(request,e) 
        attendance_update(jsondata.get('StudentId'))
        return HttpResponse(f"An error occurred: {e}", status=500)

def Scoring_logic(passedcases,data):
    attempt = data.get("Attempt")
    if str(data.get('Qn'))[-4]=="E":
        if attempt == 1:
            score = 5
        elif attempt == 2:
            score = 3
        elif attempt == 3:
            score = 2
        else:
            score = 0
    elif str(data.get('Qn'))[-4]=="M":
        if attempt == 1 or attempt == 2:
            score = 10
        elif attempt == 3:
            score = 8
        elif attempt == 4:
            score = 6
        elif attempt == 5:
            score = 4
        elif attempt == 6:
            score = 2
        else:
            score = 0
    elif str(data.get('Qn'))[-4]=="H":
        if attempt == 1 or attempt == 2 or attempt == 3:
            score = 15
        elif attempt == 4 or attempt == 5:
            score = 12
        elif attempt == 6 :
            score = 10
        elif attempt == 7:
            score = 8
        elif attempt == 8:
            score = 6
        elif attempt == 9:
            score = 4
        elif attempt == 10:
            score = 2
        else:
            score = 0
    # return math.floor(score*passedcases)
    return round(score*passedcases ,2)

def add_daysQN_db(data):
    try:
        res = data.get("Result")
        attempt = data.get("Attempt")
        i = 0 
        passedcases = 0
        totalcases = 0
        result = {}
        if data.get("Subject") == 'HTML' or data.get("Subject") == 'CSS' or data.get("Subject") == 'Java Script':
                requirements = int(str(data.get("Score")).split('/')[0])/int(str(data.get("Score")).split('/')[1])
                score = Scoring_logic(requirements,{ "Attempt":1, "Qn":data.get("Qn") })
                result = res
                attempt = 1
        else:
            for r in res:
                i += 1
                if r.get("TestCase" + str(i)) == 'Passed' or r.get("TestCase" + str(i)) == 'Failed':
                    totalcases += 1
                    if r.get("TestCase" + str(i)) == 'Passed':
                        passedcases += 1
                    result.update(r)
                if r.get("Result") == 'True' or r.get("Result") == 'False':
                    result.update(r)
            if passedcases == totalcases and passedcases ==0:
                score = 0
            else:
                score = Scoring_logic(passedcases/totalcases,data)

        user = QuestionDetails_Days.objects.filter(Student_id=str(data.get("StudentId")),Subject=str(data.get("Subject")),Qn=str(data.get("Qn"))).first()
        mainuser = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        if mainuser is None:
            mainuser = StudentDetails_Days_Questions(
                Student_id=str(data.get("StudentId")),   
                Days_completed = {data.get("Subject"):0},
                Qns_lists = {data.get("Subject")+'_Day_'+str(int(data.get("Day_no"))):[]},
                Qns_status = {data.get("Subject")+'_Day_'+str(int(data.get("Day_no"))):{}},
                Ans_lists = {data.get("Subject")+'_Day_'+str(int(data.get("Day_no"))):[]},
                Score_lists = {data.get("Subject")+'Score':"0/0"},
            )   
            mainuser.save()
        if user is  None:

            q = QuestionDetails_Days(
                Student_id=str(data.get("StudentId")),
                Subject=str(data.get("Subject")),
                Score=score,
                Attempts=attempt,
                DateAndTime=datetime.utcnow().__add__(timedelta(hours=5,minutes=30)),
                Qn = str(data.get("Qn")),
                Ans = str(data.get("Ans")),
                Result = {"TestCases":result}
                )
            q.save()
            if mainuser.Qns_status.get(data.get('Subject')+'_Day_'+str(data.get('Day_no'))) is None:
                mainuser.Qns_status.update({data.get('Subject')+'_Day_'+str(data.get('Day_no')):{}})
            if mainuser.Ans_lists.get(data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))) is None:
                mainuser.Ans_lists.update({data.get("Subject")+'_Day_'+str(int(data.get("Day_no"))):[]}) #mainuser.Ans_lists[data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))]=[]
            if mainuser.Score_lists.get(data.get("Subject")+'Score') is None or mainuser.Score_lists.get(data.get("Subject")+'Score')==[]:
                mainuser.Score_lists.update({data.get("Subject")+'Score':"0/0"}) #mainuser.Score_lists[data.get("Subject")+'Score']=0
            oldscore =  mainuser.Score_lists.get(data.get("Subject")+'Score',"0/0").split('/')[0]
            totaloff =  mainuser.Score_lists.get(data.get("Subject")+'Score',"0/0").split('/')[1]
            if str(data.get("Qn"))[-4]=="E":
                outoff  = 5
            elif str(data.get("Qn"))[-4]=="M":
                outoff  = 10
            else:
                outoff  = 15
            if data.get("Qn") not in mainuser.Ans_lists.get(data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))):
                mainuser.Score_lists.update({data.get("Subject")+'Score':str(float(oldscore)+float(score))+"/"+str(int(totaloff)+int(outoff))}) #if mainuser.Score_lists.get(data.get("Subject")+'Score') is None else mainuser.Score_lists[data.get("Subject")+'Score'] = (mainuser.Score_lists[key] if mainuser.Score_lists.get(key) else 0 )+ score
                mainuser.Ans_lists[data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))].append(data.get("Qn"))
                if result.get("Result") == 'True':
                    mainuser.Qns_status.get(data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))).update({data.get("Qn"):3}) 
                else:
                    mainuser.Qns_status.get(data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))).update({data.get("Qn"):2}) 
                if mainuser.End_Course is None:
                    mainuser.End_Course = {}
                mainuser.End_Course.update({data.get("Subject"):datetime.utcnow().__add__(timedelta(hours=5,minutes=30))})
                mainuser.save()
        
        return {'Result':"Answer has been submitted successfully"}
    except Exception as e:
        return 'An error occurred'+str(e)


@api_view(['POST'])
def nextQn(req):
    try:
        data = json.loads(req.body)
        mainuser = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        qlist = mainuser.Qns_lists[data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))]
        if str(data.get('NextQn')) == 'N':
            nextQn = int(qlist.index(data.get("Qn")))+1
        else:
            nextQn = int(qlist.index(data.get("Qn")))-1
        if nextQn == len(qlist) or nextQn == -1:
            attendance_update(data.get('StudentId'))
            return HttpResponse(json.dumps({"Question":None }), content_type='application/json')
        qnsdata = download_blob2('Internship_days_schema/'+data.get("Subject")+'/Day_'+str(data.get('Day_no'))+'/'+qlist[nextQn]+'.json',CONTAINER)
        qnsdata = json.loads(qnsdata)
        qnsdata.update({"Qn_name":qlist[nextQn],
                        "Qn_No": nextQn+1,})
        user = QuestionDetails_Days.objects.filter(Student_id=str(data.get("StudentId")),Subject=str(data.get("Subject")),Qn=str(qlist[nextQn])).first()
        if user:
            qnsdata.update({"UserAns":user.Ans })
            qnsdata.update({"UserSubmited":"Yes" })
        else:
            qnsdata.update({"UserAns":'' })
            qnsdata.update({"UserSubmited":'No' })
        if mainuser.Qns_status.get(data.get('Subject')+'_Day_'+str(data.get('Day_no'))).get(qlist[nextQn],0) < 1:
            mainuser.Qns_status.get(data.get('Subject')+'_Day_'+str(data.get('Day_no'))).update({qlist[nextQn]:1})
            mainuser.save()
        out = {}
        if data.get('Subject') == 'SQL':
                tabs =  get_tables(qnsdata.get('Table'))
                out.update({"Tables":tabs,"Question":qnsdata})
        else:
                out.update({"Question":qnsdata})
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps(out), content_type='application/json')
    except Exception as e:
        ErrorLog(req ,e) 
        attendance_update(data.get('StudentId'))
        return HttpResponse('An error occurred'+str(e), status=500)
@api_view(['POST']) 
def daycomplete(req):
    try:
        data = json.loads(req.body)
        mainuser = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        if mainuser is None:
            mainuser = StudentDetails_Days_Questions(Student_id=str(data.get("StudentId")))
            mainuser.Days_completed.update({data.get("Course"):0}) #mainuser.Days_completed[data.get("Course")] = 0
            mainuser.save()
        days_completed = mainuser.Days_completed.get(data.get("Course"),0)
        if days_completed < data.get("Day_no"):
            days_completed = data.get("Day_no")
            mainuser.Days_completed.update({data.get("Course"):days_completed}) #mainuser.Days_completed[data.get("Course")] = days_completed
            mainuser.save()
        if len(mainuser.Qns_lists.get(data.get("Course")+'_Day_'+str(int(data.get("Day_no"))))) == len(mainuser.Ans_lists.get(data.get("Course")+'_Day_'+str(int(data.get("Day_no"))))) and len(mainuser.Qns_lists.get(data.get("Course")+'_Day_'+str(int(data.get("Day_no"))))) > 0:
                print('UPDATING RANKS...')
                updateRanks((data.get('Course')) )
        else:
            print('NOT UPDATING RANKS...')
        # attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps({"Result":"Success"}), content_type='application/json')
    except Exception as e:
        print(e)
        # ErrorLog(req ,e) 
        # attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps({"Result":"Failure"}), content_type='application/json')
@api_view(['POST'])
def updatestatues(req):
    try:
        data = json.loads(req.body)
        mainuser = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        if mainuser is None:
            HttpResponse('No data found')
        # mainuser.Qns_status.update(data.get("Data"))
        # mainuser.save()
        for category, values in mainuser.Qns_status .items():

            for key, value in values.items():
               user = QuestionDetails_Days.objects.filter(Student_id=str(data.get("StudentId")),Qn=str(key)).first()
               if user:
                    if (user.Result.get('TestCases').get('Result',0))=="True":
                        mainuser.Qns_status.get(category).update({key:3})
                    else:
                        mainuser.Qns_status.get(category).update({key:2})
        # mainuser.save()
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps( mainuser.Qns_status ), content_type='application/json')
    except Exception as e:
        ErrorLog(req ,e) 
        attendance_update(data.get('StudentId'))
        return HttpResponse('An error occurred'+str(e))
@api_view(['GET'])
def getSTdDaysdetailes(req):
    try:
        mainuser = StudentDetails_Days_Questions.objects.all().values( )
        if mainuser is None:
            HttpResponse('No data found')
        return HttpResponse(json.dumps( list(mainuser) ), content_type='application/json')    
    except Exception as e:
        return HttpResponse('An error occurred'+str(e))
    
def get_tables(tables):
    try:
                tabs = []
                connection_string = (f'Driver={MSSQL_DRIVER};'f'Server={MSSQL_SERVER_NAME};'f'Database={MSSQL_DATABASE_NAME};'f'UID={MSSQL_USERNAME};'f'PWD={MSSQL_PWD};')    
                conn = pyodbc.connect(connection_string)
                cursor = conn.cursor()
                tables = str(tables).split(',')
                for table in tables:
                    cursor.execute("SELECT * FROM " + table)
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    data = extract_table_rows(rows, columns)
                    
                    tabs.append({"tab_name": table, "data": data})
                return tabs
    except Exception as e:  
        return "Error getting tables: " + str(e)
    

@api_view(['GET'])
def get_bugs(req):
    try:
        bugs = BugDetails.objects.all().values()
        if bugs is None:
            HttpResponse('No data found')
        return HttpResponse(json.dumps( list(bugs) ), content_type='application/json')
    except Exception as e:
        return HttpResponse('An error occurred'+str(e))
# def getRanks(allusersranks ,sid):
#     try:
#         # ranks = StudentDetails_Days_Questions.objects.all()
#         ranks = allusersranks
#         if ranks is None:
#             HttpResponse('No data found')
#         allRanks = []
#         for i in ranks:
#             if str(i.Student_id)[2:].startswith('ADMI') or str(i.Student_id)[2:].startswith('TRAI')  or str(i.Student_id)[2:].startswith('TEST'):
#                 continue
#             total = 0
#             Toff = 0
#             for j in i.Score_lists.keys():
#                 total += float(str(i.Score_lists[j]).split('/')[0])
#                 Toff += float(str(i.Score_lists[j]).split('/')[1])
#             allRanks.append({"StudentId":i.Student_id,"Total":total, "Toff":Toff})   
#         allRanks =  sorted(allRanks, key=lambda x: x["StudentId"], reverse=False)             
#         ranks =   sorted(allRanks, key=lambda x: x["Total"], reverse=True)
#         allRanks =  [i.get('StudentId') for i in ranks]
#         # print(allRanks,allRanks.index(sid))
#         # for i in ranks:
#         #                 print(i)
#         #                 if i.get('StudentId') == sid:
#         #                     break
#         rank = allRanks.index(sid)+1 if sid in allRanks else 'N/A'
#         return rank
#     except Exception as e:
#         print(e)
#         return  'An error occurred'+str(e) 
def getRanksbyCourse(allusersranks,Course):
    try:
        # ranks = StudentDetails_Days_Questions.objects.all()
        ranks = allusersranks
        if ranks is None:
            HttpResponse('No data found')
        allRanks = []
        for i in ranks:
            if str(i.Student_id)[2:].startswith('ADMI') or str(i.Student_id)[2:].startswith('TRAI') or str(i.Student_id)[2:].startswith('TEST'):
                continue
            total = 0
            Toff = 0
            for j in i.Score_lists.keys():
                if Course == 'HTMLCSS':
                    if str(j).startswith('HTML') or str(j).startswith('CSS'):
                        total += float(str(i.Score_lists[j]).split('/')[0])
                        Toff += float(str(i.Score_lists[j]).split('/')[1])
                else:
                    if str(j).startswith(Course):
                        total += float(str(i.Score_lists[j]).split('/')[0])
                        Toff += float(str(i.Score_lists[j]).split('/')[1])
                 
            allRanks.append({"StudentId":i.Student_id,"Total":total, "Toff":Toff})   
        allRanks =  sorted(allRanks, key=lambda x: x["StudentId"], reverse=False)             
        ranks =   sorted(allRanks, key=lambda x: x["Total"], reverse=True)
        return ranks
    except Exception as e:
        print(e)
        return  'An error occurred'+str(e)
@api_view(['GET'])
def test (req):
    try:
        distinct = {}
        data = StudentDetails.objects.all() 
        if data is not None:
            for i in data:
                if str(i.StudentId)[0:6    ] not in distinct:
                    distinct.update({str(i.StudentId)[0:6]:[int(str(i.StudentId)[6:])]})
                else:
                    distinct[str(i.StudentId)[0:6]].append(int(str(i.StudentId)[6:]))
        for i in distinct:
            distinct[i] = max(distinct[i])
        with open('testdb.json', 'r') as json_file:
        # with open('output1.json', 'r') as json_file:
            data1 = json.load(json_file)
        for i in list(data1):
            cid = i.get('College')[:4]
            if len(i.get('College'))<4:
                cid = i.get('College') + 'X'
            if len(i.get('College') ) >4:
                cid = i.get('College')[:4]
            if distinct.get(str(datetime.utcnow().year)[-2:] + str(cid)) is None:
                distinct.update({str(datetime.utcnow().year)[-2:] + str(cid):0})
            idno =distinct.get(str(datetime.utcnow().year)[-2:] + str(cid))+1
            distinct.update({str(datetime.utcnow().year)[-2:] + str(cid):idno})
            if len(str(idno))==1:
                idno = '000'+str(idno)
            if len(str(idno))==2:
                idno = '00'+str(idno)
            if len(str(idno))==3:
                idno = '0'+str(idno)
            if len(str(idno))==4:
                idno = str(idno)
            if len(str(idno))>4:
                Exception('more than 4 digits')
            sid = str(datetime.utcnow().year)[-2:] + cid+ idno
            u1 = StudentDetails(
                StudentId   = sid,
                firstName   = (i['Student Full Name']).split()[0],
                lastName    = i['Student Full Name'].replace((i['Student Full Name']).split()[0],''),
                college_Id  = i['College'][0:4],
                CollegeName = i['College'],
                Center      = i.get('Center'),
                branch      = i.get('Branch'),
                email       = i.get('Email address'),
                whatsApp_No = i.get('Contact Number'),
                mob_No      = i.get('Contact Number'),
                sem         = i.get('Semester'),
                status      = 'a',
                user_category =  's',
                reg_date    = datetime.utcnow().__add__(timedelta(hours=5,minutes=30)),
                exp_date    = datetime.utcnow().__add__(timedelta(hours=5,minutes=30))+timedelta(days=365),
                score       = 0,
                progress_Id = {},
                Assignments_test = {},
                Courses     = [],
                Course_Time = {},
                CGPA        = i.get('CGPA')
            )
            u1.save()
            l1 = login_data(
                User_ID     = sid,
                User_name   = i['Student Full Name'],
                User_emailID= i.get('Email address'),
                User_catagory = 's'
            )
            l1.save()
            sd1 =StudentDetails_Days_Questions(
                Student_id = sid
            )
            sd1.save()
        
        return HttpResponse('Success' + str(distinct))
    except Exception as e:
        print(e)
        return HttpResponse('An error occurred'+str(e))
from django.db.models import Sum
from django.db.models import Q, Sum
def rankings(allusers):
    try:
        allmainQns = QuestionDetails_Days.objects.all()
        ranks = allusers
        if ranks is None:
            HttpResponse('No data found')
        out ={}
        noDAta = []
        for i in ranks:
         if str(i.get('StudentId'))[2:].startswith("ADMI") or str(i.get('StudentId'))[2:].startswith("TRAI") or str(i.get('StudentId'))[2:].startswith("TEST"):
            continue
        #  user = QuestionDetails_Days.objects.filter(Student_id=i.get('StudentId'))
         user = filterQuery(allmainQns, 'Student_id',  i.get('StudentId'))
         if user is None:
            noDAta.append(i.get('StudentId'))
            continue
        #  HTML = filterQuery(user, 'Subject',  'HTML')
        #  CSS = filterQuery(user, 'Subject',  'CSS')
         HTML = filterQueryfromdict(user, 'Subject',  'HTML')
         CSS = filterQueryfromdict(user, 'Subject',  'CSS')
         if HTML is None or CSS is None or len(HTML) == 0 or len(CSS) == 0:
            noDAta.append(i.get('StudentId'))
            continue
         HTMLCSSSCORE =0
         HTMLLASTTIME = HTML[0].get('DateAndTime')
         for i1 in HTML:
            # print(i)
            HTMLCSSSCORE += i1.get('Score')
            if i1.get('DateAndTime') > HTMLLASTTIME:
                HTMLLASTTIME = i1.get('DateAndTime')
         for i2 in CSS:
            HTMLCSSSCORE += i2.get('Score')
            if i2.get('DateAndTime') > HTMLLASTTIME:
                HTMLLASTTIME = i2.get('DateAndTime')
         
         out.update({i.get('StudentId'): {
            "HTMLCSS":   HTMLCSSSCORE,
            'HTML_last_Question':   HTMLLASTTIME,

        }
    })
        ranks = sorted(    out.items(),     key=lambda x: (-x[1]['HTMLCSS'], x[1]['HTML_last_Question']))  
        res = []
        print('ranks',ranks)
        for i in ranks:
                res.append({'Rank':ranks.index(i)+1,"StudentId":i [0],"Total":i[1]['HTMLCSS'], "LastTime":i[1]['HTML_last_Question']})
                print({'Rank':ranks.index(i)+1,"StudentId":i [0], "LastTime":i[1]['HTML_last_Question'],"Total":i[1]['HTMLCSS']})
        print('out')
        return res
    
    except Exception as e:
        print(e)
        return HttpResponse('An error occurred'+str(e))
    


### TESTING SPACE ####


@api_view(['GET'])
def updateScore(request):
    try:
        all = StudentDetails.objects.all()
        out =[]

        # for updateing QuestionDetails_Days score ####################################################``
        # for i in all:
            
        #     user = QuestionDetails_Days.objects.filter(Student_id = i.StudentId, Subject = 'CSS').all().aggregate(total_score=Sum('Score'))['total_score'] or 0
        #     # print('')
        #     # print(i.StudentId, user)
        #     main = StudentDetails_Days_Questions.objects.get(Student_id = i.StudentId)
            
        #     # print(main.Score_lists.get('CSSScore'))
        #     old = main.Score_lists.get('CSSScore')
        #     main.Score_lists.update({'CSSScore':str(user)+'/'+str(main.Score_lists.get('CSSScore','0/0')).split('/')[1]})
        #     # print(main.Score_lists.get('CSSScore'))
        #     if old != main.Score_lists.get('CSSScore'):
        #         print(i.StudentId,'[old',old,'][new', main.Score_lists.get('CSSScore')+']') 
        #         main.save()
        #     if float(str( main.Score_lists.get('CSSScore')).split('/')[0]) > float(str( main.Score_lists.get('CSSScore')).split('/')[1]):
        #         out.append(i.StudentId+' '+ main.Score_lists.get('CSSScore'))
        #         print(i.StudentId,'[old',old,'][new', main.Score_lists.get('CSSScore')+']') 

        for i in all:
            user = QuestionDetails_Days.objects.filter(Student_id = i.StudentId).all()
            if user is None:
                continue
            for j in user:
                if str(j.Qn)[-4] =='E' and j.Score > 5:
                    print(i.StudentId,'5',str(j.Qn)[-4],j.Score,j.Qn ,' ', j.Subject)
                    j.Score = 5
                    print('NEW',j.Score)
                    j.save()
                    out.append(i.StudentId)
                if str(j.Qn)[-4] =='M' and j.Score > 10:
                    print(i.StudentId,'10',str(j.Qn)[-4],j.Score,j.Qn ,' ', j.Subject)
                    j.Score = 10
                    print('NEW',j.Score)
                    j.save()
                    out.append(i.StudentId)
                if str(j.Qn)[-4] =='H' and j.Score > 15:
                    print(i.StudentId,'15',str(j.Qn)[-4],j.Score,j.Qn ,' ', j.Subject)
                    j.Score = 15
                    print('NEW',j.Score)
                    j.save()
                    out.append(i.StudentId)
                 


        return HttpResponse(json.dumps(out), content_type='application/json')
    except Exception as e:
        print(e) 
        return HttpResponse('An error occurred'+str(e))