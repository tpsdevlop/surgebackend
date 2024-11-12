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
@api_view(['POST'])
def Internship_Home(request):
    try:
        req =json.loads(request.body)
        StudentId = req.get('StudentId')
        data= json.loads(download_blob2('Internship_days_schema/internshipJSONS/InternshipProject.json',CONTAINER))
        projectName = data.get('Internship_Project').get('Project_Name')

        user,created = InternshipsDetails.objects.get_or_create(StudentId=StudentId,defaults = {
            'ProjectName':[projectName],
            'HTMLCode':{str(projectName).replace(' ',''):{}},
            'CSSCode':{str(projectName).replace(' ',''):{}},
            'JSCode':{str(projectName).replace(' ',''):{}},
            'PythonCode':{str(projectName).replace(' ',''):{}},
            'AppPyCode':{str(projectName).replace(' ',''):{}},
            'DatabaseCode':{str(projectName).replace(' ',''):{}}, 
            'HTMLScore':{str(projectName).replace(' ',''):{}},
            'CSSScore':{str(projectName).replace(' ',''):{}},
            'JSScore':{str(projectName).replace(' ',''):{}},
            'PythonScore':{str(projectName).replace(' ',''):{}},
            'AppPyScore':{str(projectName).replace(' ',''):{}},
            'DatabaseScore':{str(projectName).replace(' ',''):{}},
            'InternshipScores':{str(projectName).replace(' ',''):{}},
            'ProjectStatus':{str(projectName).replace(' ',''):{
                i:0 for i in data.get('Internship_Overview')[1].get('Project_Web_Pages')
                }},
        })
        tabs ={}
        tabsScores ={}
        for i in data.get('Internship_Overview')[1].get('Project_Web_Pages'):
            # print( (i))
            webpages= json.loads(download_blob('Concept/course/'+ str(i)+'.json'))            
            if str(i) == 'Database_setup':
                tabs.update({(i):{webpages.get('Tabs')[t]:webpages.get('Table_Names')[t] for t in range(0,len(webpages.get('Tabs')))}})
            else:
                tabs.update({(i):{P : webpages.get('Tabs')for P in data.get('Internship_Tasks' ) if data.get('Internship_Tasks' ).get(P) == i}})
            progress =[]
            for t in range(0,len(webpages.get('Tabs'))):
                if i == "Database_setup":
                     progress.append({
                                        "Tables": t+1,
                                        "Name": webpages.get('Table_Names')[t],
                                        "Score": user.DatabaseScore.get(str(projectName).replace(' ','')).get(str(webpages.get('Table_Names')[t])+'_Score','0/0')
                                    })
                else:
                    switch = {
                        'HTML': lambda: user.HTMLScore.get(str(projectName).replace(' ', '')).get(i,"0/0"),
                        'CSS' : lambda: user.CSSScore.get(str(projectName).replace(' ', '')).get(i,"0/0"),
                        'JS'  : lambda: user.JSScore.get(str(projectName).replace(' ', '')).get(i,"0/0"),
                        'Python':lambda: user.PythonScore.get(str(projectName).replace(' ', '')).get(i,"0/0"),
                        'app.py':lambda: user.AppPyScore.get(str(projectName).replace(' ', '')).get(i,"0/0"),
                    }
                    result = switch.get(webpages.get('Tabs')[t], lambda: "0/0")()
                    progress.append({
                                        "Sl_No": t+1,
                                        "Pages": webpages.get('Tabs')[t],
                                        "Score": result
                                    })
                tabsScores.update({str(i)+'_Score':progress})

        out ={
            "Sidebar":data,
            "data":tabs,
            "Status":user.ProjectStatus.get(str(projectName).replace(' ',''),{}),
            "Scores":tabsScores,
            
        }

        return HttpResponse(json.dumps(out), content_type='application/json')
    except Exception as e:
        print(e)
        ErrorLog(request,e)
        return HttpResponse(f"An error occurred: {e}", status=500)