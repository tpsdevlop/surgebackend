from datetime import datetime, timedelta
import json
from django.http import HttpResponse
from .models import *
from rest_framework.decorators import api_view
import traceback
from pymongo import MongoClient
 
 
@api_view(['GET'])
def adminflow(request):
    try:
        activeUser = activeUsers()
        Content = ContentCreate()
        error = ErrorLog()
        out = {
            "activeUsers": activeUser,
            "Content": Content,
            "ErrorLog": error
        }
       
        return HttpResponse(json.dumps(out), content_type="application/json")
    except Exception as e:
        print(traceback.format_exc())
        return HttpResponse(json.dumps("failure"), content_type="application/json")
 
def activeUsers():
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
 
 
 
        return response_data
    except Exception as e:
        print(e)
        return  json.dumps("failure")
   
def ContentCreate():
    try:
        client = MongoClient('mongodb+srv://kecoview:FVy5fqqCtQy3KIt6@cluster0.b9wmlid.mongodb.net/')
        db = client['PythonDB']
        content_collection = db['questioninfo']
        content_data = content_collection.find()
        out1 = []
        out2 = []
        for content in content_data:
            if content['Subject'] == 'Python':
                out1.append(content['QuestionId'] )
            if content['Subject'] == 'SQL':
                out2.append(content['QuestionId'])
        print('Python',len(out1),'SQL',len(out2))
 
        out = {'Python':{
            'Test':
               {
                  'Easy_Test':len([out1[i] for i in range(len(out1)) if out1[i][-4] == 'E' and str(out1[i]).startswith('T')]),
                  'Medium_Test':len([out1[i] for i in range(len(out1)) if out1[i][-4] == 'M' and str(out1[i]).startswith('T')]),
                  'Hard_Test':len([out1[i] for i in range(len(out1)) if out1[i][-4] == 'H' and str(out1[i]).startswith('T')])
               },
            'ex':
            {
                  'Easy_ex': len([out1[i] for i in range(len(out1)) if out1[i][-4] == 'E' and str(out1[i]).startswith('Q')]),
                  'Medium_ex': len([out1[i] for i in range(len(out1)) if out1[i][-4] == 'M' and str(out1[i]).startswith('Q')]),
                  'Hard_ex': len([out1[i] for i in range(len(out1)) if out1[i][-4] == 'H' and str(out1[i]).startswith('Q')])
               },
            'Total_Questions':len(out1),
            'Questions':out1
               },
            'SQL':
            {
                'Test':
                {
                    'Easy_Test':len([out2[i] for i in range(len(out2)) if out2[i][-4] == 'E' and str(out2[i]).startswith('T')]),
                    'Medium_Test':len([out2[i] for i in range(len(out2)) if out2[i][-4] == 'M' and str(out2[i]).startswith('T')]),
                    'Hard_Test':len([out2[i] for i in range(len(out2)) if out2[i][-4] == 'H' and str(out2[i]).startswith('T')])
                },
                'ex':
                {
                    'Easy_ex': len([out2[i] for i in range(len(out2)) if out2[i][-4] == 'E' and str(out2[i]).startswith('Q')]),
                    'Medium_ex': len([out2[i] for i in range(len(out2)) if out2[i][-4] == 'M' and str(out2[i]).startswith('Q')]),
                    'Hard_ex': len([out2[i] for i in range(len(out2)) if out2[i][-4] == 'H' and str(out2[i]).startswith('Q')])
                },
                'Total_Questions':len(out2),
                'Questions':out2
            }}
        return  (out)
    except StudentDetails.DoesNotExist:
        return  json.dumps("failure")
 
def ErrorLog():
    try:
        errors = ErrorLogs.objects.all()
        out1 = []
        for error in errors:
            out1.append( {
                "Error_id": error.Error_id,
                "StudentId": error.StudentId,
                "Email": error.Email,
                "Name": error.Name,
                "Occrued_time": str (error.Occrued_time),
                "Error_msg": error.Error_msg,
                "Stack_trace": error.Stack_trace,
                "User_agent": error.User_agent,
                "Operating_sys": error.Operating_sys
            })
        out = {
                'Total_Errors':len(out1),
                'Errors':out1
        }
        return  (out)
    except ErrorLogs.DoesNotExist:
        return   "failure"
 