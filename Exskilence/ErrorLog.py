from datetime import datetime, timedelta
import json
import re

from django.http import HttpResponse
from Exskilence.models import *
from rest_framework.decorators import api_view
import traceback

def ErrorLog(req,e):
    try:
        # print('url:---------',req.build_absolute_uri())
        u_agent = str(req.META.get('HTTP_USER_AGENT'))
        os_info = str(u_agent)[u_agent.find("(")+1:u_agent.find(")")]
        error = {
            "StudentId": json.loads( req.body).get('StudentId'),
            "Error_msg": str(e),
            "Stack_trace": str(traceback.format_exc())+'\nUrl:-'+str(req.build_absolute_uri())+'\nBody:-'+str(json.loads( req.body)),
            "User_agent": u_agent,
            "Operating_sys": os_info ,
        }
        try:
            std   = StudentDetails.objects.get(StudentId=error.get('StudentId'))
        except:
            std = None
        Time  = datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
        ErrorLog = ErrorLogs.objects.create(
            StudentId=error.get('StudentId'),
            Email=std.email if std else json.loads(req.body).get('Email'),
            Name = str(std.firstName)+' '+str(std.lastName) if std else json.loads(req.body).get('Name'),
            Occurred_time = Time,
            Error_msg = error.get('Error_msg'),
            Stack_trace = error.get('Stack_trace'),
            User_agent = error.get('User_agent'),
            Operating_sys = error.get('Operating_sys'),
            )
        return True 
    except Exception as e:
        print(e)
        return False