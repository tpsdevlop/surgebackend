
from datetime import datetime, timedelta
from django.http import HttpResponse
from .models import *
from rest_framework import viewsets
from rest_framework.response import Response
import json
from rest_framework.decorators import api_view


def attendance_create_login(data):
    try:
        old = Attendance.objects.filter(SID=data).order_by('-Login_time').first()
        if old is not None:
            oldduration = int((old.Last_update - old.Login_time).total_seconds())
            old.Duration = oldduration
            old.save()
            First = "Second"
        else:
            First = "First"
        Attendance.objects.create(
            SID=data,
            Login_time=datetime.utcnow().__add__(timedelta(hours=5,minutes=30)),
            Last_update=datetime.utcnow().__add__(timedelta(hours=5,minutes=30)),
        )
        return First
    except Exception as e:
        return False
    
def attendance_update(data):
    try:
        old = Attendance.objects.filter(SID=data).order_by('-Login_time').first()
        if old is not None:
            old.Last_update = datetime.utcnow().__add__(timedelta(hours=5,minutes=30))
            old.save()
        else:
            attendance_create_login(data)
        return True
    except Exception as e:
        return False