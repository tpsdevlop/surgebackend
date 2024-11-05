import calendar
import json
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse
from cryptography.fernet import Fernet
from datetime import date, datetime, time, timedelta
from Exskilence.models import *
from Exskilence.Attendance import attendance_create_login, attendance_update


key = Fernet.generate_key()
key = b'kOt0aprdFA1-Zj-w6fENiZOf7IVfgnPjv_-usgnBA5s='
cipher_suite = Fernet(key)

def encrypt_message(message: str) -> bytes:
    return cipher_suite.encrypt(message.encode())

def decrypt_message(encrypted_message: bytes) -> str:
    return cipher_suite.decrypt(encrypted_message).decode()


@api_view(['GET'])
def EncodeView(request):
    try :
        data1 = {
    "StudentId":"24MRIT0010"
}
        # data1 = sam
        encrypted_response = encrypt_message(str(data1))
        out = {'data' : str(encrypted_response)[2:-1]}
        return HttpResponse( json.dumps(out), content_type="application/json")
    except Exception as e:
        print(e)
        return HttpResponse(f"An error occurred: {e}")

@api_view(['POST']) 
def DecodeView(request):
    try:
        data = request.body
        data = json.loads(data)    
        enc1 = data['data']
        enc1_bytes = enc1.encode()
        decrypted_data = cipher_suite.decrypt(enc1_bytes).decode()
        # print("decrypted_data1:", decrypted_data)
        # print('********/*********')
        # print('decrypted_data2:',decrypted_data.replace("'", '"')[190:210],decrypted_data.replace("'", '"')[205])
        out =  (decrypted_data.replace("'", '"'))
        # print('********/*********',json.loads(out ).get('Courses'))
        return HttpResponse(json.dumps(out), content_type="application/json")
    except Exception as e:
        print(e)
        return HttpResponse({"error": f"An error occurred: {str(e)}"}, status=400)
    
def decry(data):
    try:
        enc1_bytes = data.encode()
        decrypted_data = cipher_suite.decrypt(enc1_bytes).decode()
        # print('************************************')
        # print("decrypted_data:", (decrypted_data.replace("'", '"')))
        # print('************************************')
        out = {'data':  str(decrypted_data).replace("'", '"')}
        # out = str(decrypted_data)
        out = dict(out)
        return  (out) 
    except Exception as e:
        print(e)
        return (f"An error occurred: {str(e)}")
def encrypt(data):
    try:
        encrypted_response = encrypt_message(str(data))
        # print('************************************')
        # print("encrypted_response:", encrypted_response)
        # print('************************************')
        out = {'data' : str(encrypted_response)[2:-1]}
        return (out)
    except Exception as e:
        print(e)
        return (f"An error occurred: {str(e)}")

@api_view(['POST'])
def getcourse(req):
    try:
        data = json.loads(req.body)
        data = data.get('data')
        data = decry(data)
        # print('****DECRY: ',data)
        # print('****DECRY: ',data.get('data'))
        data =  json.loads(data.get('data'))
        print('idddddddddddd',data.get('StudentId'))
        user = StudentDetails.objects.get(StudentId=data.get('StudentId'))
        userscore, created = StudentDetails_Days_Questions.objects.get_or_create(
                            Student_id=data.get('StudentId'),
                            defaults={
                                'Start_Course': {}, 
                                'Days_completed': {},  
                                'Qns_lists': {},
                                'Qns_status': {},
                                'Ans_lists': {},
                                'Score_lists': {}   
                            }
                        ) 
        courseinfo ={}
        for i in user.Courses:
            if userscore.Qns_lists.get(i, None) is None:
                courseinfo.update({i: "True"})
            else:
                courseinfo.update({i: "False"})
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
                        "Name":course.get('Description')  ,
                        "Duration":str(getdays(starttime))+" to "+str(getdays(endtime)) ,
                        'Progress':str(round(len(userscore.Ans_lists.get(course.get('SubjectName'),[])if course.get('SubjectName') != "HTMLCSS" else userscore.Ans_lists.get("HTML",[] ))/len(userscore.Qns_lists.get(course.get('SubjectName'),[]))*100))+"%" if len(userscore.Qns_lists.get(course.get('SubjectName'),[])) != 0 else '0%',
                        'Assignment':str(len(userscore.Ans_lists.get(course.get('SubjectName'),[])if course.get('SubjectName') != "HTMLCSS" else userscore.Ans_lists.get("HTML",[] )))+"/"+str(len(userscore.Qns_lists.get(course.get('SubjectName'),[]))),
                        "Status" : 'Opened' if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow().__add__(timedelta(hours=5,minutes=30)) and datetime.strptime(str(endtime), "%Y-%m-%d %H:%M:%S") > datetime.utcnow().__add__(timedelta(hours=5,minutes=30)) else 'Closed',
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
                        "Name":course.get('Description')  ,
                        "Duration":str(getdays(starttime))+" to "+str(getdays(endtime)) ,
                        'Progress': str(round(sum(numAns)/sum(numQns)*100))+'%' if sum(numQns)!= 0 else "0%" ,
                        'Assignment':str(sum(numAns))+"/"+str(sum(numQns)),
                        "Status" : 'Opened' if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow().__add__(timedelta(hours=5,minutes=30)) and datetime.strptime(str(endtime), "%Y-%m-%d %H:%M:%S") > datetime.utcnow().__add__(timedelta(hours=5,minutes=30)) else 'Closed'
                        })
                        if datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S") < datetime.utcnow().__add__(timedelta(hours=5,minutes=30)):
                            intcourse.get('Sub').append(course.get('SubjectName'))
                            intcourse.get('SubScore').append(str(round(float(str(userscore.Score_lists.get(str(course.get('SubjectName'))+'Score')).split('/')[0]),2))+"/"+str(subScore(userscore.Qns_lists,course.get('SubjectName'))))
                            Total_Score = float(Total_Score) + float(intcourse.get('SubScore')[-1].split('/')[0])
                            Total_Score_Outof = int(Total_Score_Outof) + int(intcourse.get('SubScore')[-1].split('/')[1])
                    if Startmost > starttime:
                        Startmost = starttime
            spent = Attendance.objects.filter(SID=data.get('StudentId')).filter(Login_time__range=[Startmost, Endmost],Last_update__range=[Startmost, Endmost])  
            Duration = 0 
            if spent:
                for i in spent:
                    Duration = Duration + (i.Last_update - i.Login_time).total_seconds()
            intcourse.get('Score').append(str(Total_Score)+"/"+str(Total_Score_Outof))
            out.update({"Courses":Enrolled_courses,
                        "Intenship":intcourse,
                        "Prograss":{
                            "Start_date":str(Startmost).split()[0],
                            "End_date":str(Endmost).split()[0],
                            "Duration":Duration
                        },
                        "StudentName":user.firstName})
            user.score =round(float(str(intcourse.get('Score')[0]).split('/')[0]),2)
            user.save()
            attendance_update(data.get('StudentId'))
            out = encrypt(out)
            return HttpResponse(json.dumps(out), content_type='application/json')
        else:
            attendance_update(data.get('StudentId'))
            return HttpResponse('Error! User does not exist', status=404)
    except Exception as e:
        print(e)
        attendance_update(data.get('StudentId'))
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
@api_view(['GET'])
def activeUsevrs(req):
    try:
        start = datetime.utcnow().__add__(timedelta(hours=5,minutes=30))-timedelta(minutes=15,seconds=00)
        end = datetime.utcnow().__add__(timedelta(hours=5,minutes=30))+timedelta(minutes=5,seconds=00)
        users = Attendance.objects.all().order_by('-Last_update').filter( Last_update__range=[start, end]) 
        print(users)
        print(start,end)
        out = []
        for user in users:
            if user is not None:
                print(user.Last_update, user.SID)
                out.append({"user":user.SID,"time":user.Last_update})
        return HttpResponse(json.dumps({'activeUsers':len(out)}), content_type='application/json')
    except Exception as e:
        print(e)
        return HttpResponse(f"An error occurred: {e}", status=500) 
@api_view(['GET'])
def activeUsers(req):
    try:
        start = datetime.utcnow() + timedelta(hours=5, minutes=30) - timedelta(minutes=15)
        end = datetime.utcnow() + timedelta(hours=5, minutes=30) + timedelta(minutes=15)
        users = Attendance.objects.filter(Last_update__range=[start, end]).order_by('-Last_update')
        print(start.time(), end.time())
        user_dict = {}
        for user in users:
            try:
                if user.Status == "out":
                    print(user.SID)
                    continue
                student_details = StudentDetails.objects.get(StudentId=user.SID)
                if user.SID not in user_dict or user.Last_update > user_dict[user.SID]['last_update']:
                    user_dict[user.SID] = {
                        "user": user.SID,
                        "name": f"{student_details.firstName} {student_details.lastName}",
                        "college": student_details.CollegeName,
                        "branch": student_details.branch,
                        "cgpa": student_details.CGPA,
                        "last_update": user.Last_update  # Store as datetime object
                    }
            except StudentDetails.DoesNotExist:
                continue
 
        out = []
        for user_data in user_dict.values():
            user_data['last_update'] = user_data['last_update'].strftime('%Y-%m-%d %H:%M:%S')  # Convert datetime to string for response
            out.append(user_data)
 
        response_data = {
            'activeUsersCount': len(out),
            'activeUsersDetails': out
        }
 
        return HttpResponse(json.dumps(response_data), content_type='application/json')
    except Exception as e:
        print(e)
        return HttpResponse
 