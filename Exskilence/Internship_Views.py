import calendar
from decimal import Decimal
import json
import math
import random
import re
from bs4 import BeautifulSoup
import cssutils
from django.http import HttpResponse
import jsbeautifier
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
            'InternshipScores':{str(projectName).replace(' ',''):0},
            'ProjectDateAndTime':{str(projectName).replace(' ',''):{}},
            'ProjectStatus':{str(projectName).replace(' ',''):{
                i:0 for i in data.get('Internship_Overview')[1].get('Project_Web_Pages')
                }},
        })
        tabs ={}
        tabsScores ={}
        for i in data.get('Internship_Overview')[1].get('Project_Web_Pages'):
            # print( (i))
            webpages= json.loads(download_blob2('Internship_days_schema/internshipJSONS/'+ str(i)+'.json',CONTAINER)  )          
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
                        'HTML': lambda: user.HTMLScore.get(str(projectName).replace(' ', '')).get(i+"_Score","0/0"),
                        'CSS' : lambda: user.CSSScore.get(str(projectName).replace(' ', '')).get(i+"_Score","0/0"),
                        'JS'  : lambda: user.JSScore.get(str(projectName).replace(' ', '')).get(i+"_Score","0/0"),
                        'Python':lambda: user.PythonScore.get(str(projectName).replace(' ', '')).get(i+"_Score","0/0"),
                        'app.py':lambda: user.AppPyScore.get(str(projectName).replace(' ', '')).get(i+"_Score","0/0"),
                    }
                    result = switch.get(webpages.get('Tabs')[t], lambda: "0/0")()
                    progress.append({
                                        "Sl_No": t+1,
                                        "Pages": webpages.get('Tabs')[t],
                                        "Score": result
                                    })
                tabsScores.update({str(i)+'_Score':progress})
        dateAndTime = {}
        if user.ProjectDateAndTime.get(str(projectName).replace(' ','')) == None or user.ProjectDateAndTime.get(str(projectName).replace(' ','')) == {}:
            print("hello")
            for i in data.get('Internship_Overview')[1].get('Project_Web_Pages'):
                user.ProjectDateAndTime.get(str(projectName).replace(' ','')).update({i:{
                    'Start_Time':datetime.utcnow().__add__(timedelta(hours=5,minutes=30)),
                    'End_Time':datetime.utcnow().__add__(timedelta(hours=42,minutes=30))
                }})
            user.save()
        for j in user.ProjectDateAndTime.get(str(projectName).replace(' ','')):
            dateAndTime.update({j:
                                {
                                    'Start_Time':str(user.ProjectDateAndTime.get(str(projectName).replace(' ','')).get(j).get('Start_Time')),
                                    'End_Time':str(user.ProjectDateAndTime.get(str(projectName).replace(' ','')).get(j).get('End_Time'))
                                } 
                                })
        out ={
            "Sidebar":data,
            "data":tabs,
            "Status":user.ProjectStatus.get(str(projectName).replace(' ',''),{}),
            "Scores":tabsScores,
            "DateAndTime":dateAndTime
            
        }

        return HttpResponse(json.dumps(out), content_type='application/json')
    except Exception as e:
        ErrorLog(request,e)
        return HttpResponse(f"An error occurred: {e}", status=500)
# setInternshipTime TEST
def setInternshipTime():
    try:
        data= json.loads(download_blob2('Internship_days_schema/internshipJSONS/InternshipProject.json',CONTAINER))
        projectName = data.get('Internship_Project').get('Project_Name')
        user = InternshipsDetails.objects.filter(StudentId ="24MRIT0011").first()
 
        for i in data.get('Internship_Overview')[1].get('Project_Web_Pages'):
            user.ProjectDateAndTime.get(str(projectName).replace(' ','')).update({i:{
                'Start_Time':datetime.utcnow().__add__(timedelta(hours=5,minutes=30)),
                'End_Time':datetime.utcnow().__add__(timedelta(hours=42,minutes=30))
            }})
        user.save()
        print(data.get('Internship_Overview')[1].get('Project_Web_Pages'))
        for j in user.ProjectDateAndTime.get(str(projectName).replace(' ','')):
            print(j,str(user.ProjectDateAndTime.get(str(projectName).replace(' ','')).get(j)))
        # print(user.ProjectDateAndTime)
    except Exception as e:
         print(e)
         return HttpResponse(f"An error occurred: {e}", status=500)
 

#   Retrieve pages

@api_view(['POST'])   
def getPagesjson(req ):
    try:
        res = json.loads(req.body)
        page = res.get('Page')
        projectName = res.get('ProjectName')
        data= json.loads(download_blob2('Internship_days_schema/internshipJSONS/'+ str(page)+'.json',CONTAINER))
        user = InternshipsDetails.objects.filter(StudentId=res.get('StudentId')).first()
        if user:
            if page.startswith('Database'):
                jdata = {"Response":  user.DatabaseCode.get(str(projectName).replace(' ', ''),{})}
            else:
                switch = {
                        'HTML': lambda: user.HTMLCode.get(str(projectName).replace(' ', '')).get(page),
                        'CSS' : lambda: user.CSSCode.get(str(projectName).replace(' ', '')).get(page),
                        'JS'  : lambda: user.JSCode.get(str(projectName).replace(' ', '')).get(page ),
                        'Python':lambda: user.PythonCode.get(str(projectName).replace(' ', '')).get(page ),
                        'app.py':lambda: user.AppPyCode.get(str(projectName).replace(' ', '')).get(page ),
                    }
                result = {}#switch.get(data.get('Tabs')[page], lambda: "0/0")()
                for i in data.get('Tabs'):
                    if i == 'app.py':
                        result.update({'app_py':switch.get(i, lambda: "0/0")()})
                    else:
                        result.update({i:switch.get(i, lambda: "0/0")()})
                jdata = {"Response":result}
        else:
            if page.startswith('Database'):
                jdata = {"Response":  {}}
            else:
                jdata = {"Response":{
                    "HTML":'',
                    "CSS":'',
                    "JS":'',
                    "Python":'',
                    "App_py":''
                }}
 
        
        data.update(jdata)
        return HttpResponse(json.dumps(data), content_type='application/json') 
    except Exception as e:
            ErrorLog(req,e)
            return HttpResponse(f"An error occurred: {e}", status=500) 


#   DATABASE VALIDATION
@api_view(['POST'])
def database_validation(req):
    try:
        data = json.loads(req.body)
        projectName = data.get('ProjectName')
        input_string = data.get('data')
        list = data.get('KEYS')
        table = str(data.get('Table_name'))
        d1 = input_string.split('\n')
        ans = [a.replace(' ','') for key in list for a in d1 if str(a.replace(' ','')).__contains__(key.replace(' ',''))]
        common_keywords = [i for i in list if any(str(j).__contains__(i.replace(' ','')) for j in ans)]
        user = InternshipsDetails.objects.filter(StudentId=data.get('StudentId')).first()
        if user:
            oldscore=user.DatabaseScore.get(str(projectName).replace(' ', ''),{}).get(table+'_Score',0)
            user.DatabaseCode.get(str(projectName).replace(' ', ''),{}).update({table:input_string})
            user.DatabaseScore.get(str(projectName).replace(' ', ''),{}).update({table+'_Score':len(common_keywords)*5})
            user.InternshipScores.update({str(projectName).replace(' ', ''):user.InternshipScores.get(str(projectName).replace(' ', ''),0)+len(common_keywords)*5-int(oldscore)})#=user.Score+len(common_keywords)*5-int(oldscore)
            user.save()
            output = {}
            if len(common_keywords) == len(list):
                output.update({"valid": True,"message": "Database_setup code is valid."})
            else:
                output.update({"valid": False,"message": "Database_setup code is Not valid."})
            score = f'{len(common_keywords) }/{len(list) }'
            output.update({"score": score})
            return HttpResponse(json.dumps(output), content_type='application/json')

        else:
            return HttpResponse('User does not exist', status=404)
    except Exception as e:
            ErrorLog(req,e)
            return HttpResponse(f"An error occurred: {e}", status=500)
    
#   HTML VALIDATION

def jsonToTuple(code):
    tuple_format = []

    for element in code:
       tag = element["tag"]
       attributes = element["attributes"]
       for attr, value in attributes.items():
           tuple_format.append((tag, attr, value))
    return tuple_format
@api_view(['POST'])
def html_page_validation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            htmlcode = data.get('data')
            keys=data.get('KEYS')
            if not htmlcode:
                return HttpResponse("No HTML data provided", status=400)
            
            user_soup = BeautifulSoup(htmlcode, 'html.parser')
            def extract_tags_and_attributes(soup):
                elements = soup.find_all(True)  
                tag_attr_list = []
                for element in elements:
                    tag = element.name
                    attrs = element.attrs
                    for attr_name, attr_value in attrs.items():
                        tag_attr_list.append((tag, attr_name, attr_value))
                return tag_attr_list
            sample_elements=(jsonToTuple(keys))
            user_elements = extract_tags_and_attributes(user_soup)
            common_keywords = [i for i in sample_elements if i in user_elements]
            output = {}
            if len(common_keywords) == len(sample_elements):
                output.update({"valid": True,"message": "HTML code is valid."})
            else:
                output.update({"valid": False,"message": "HTML code is Not valid."})

            score = f'{len(common_keywords) }/{len(sample_elements) }'
            output.update({"score": score,
                       "Status": addCodeToDb(1,data.get('Page'),htmlcode,data.get('StudentId'),len(common_keywords),data.get('ProjectName'))
                       })
            return HttpResponse(json.dumps(output), content_type='application/json')

        except Exception as e:
            ErrorLog(request,e)
            return HttpResponse(f"An error occurred: {e}", status=500)
    else:
        return HttpResponse("Method Not Allowed", status=405)
    
#   CSS VALIDATION


def css_to_tuples(css_code,KEYS):
    parser = cssutils.CSSParser()
    if KEYS :
        tuple_format_css = []

        for style in KEYS:
            if "media_query" in style:
                media_query = style["media_query"]
                rules = style["rules"]
                media_rules = [(rule["selector"], [(prop["property"], prop["value"]) for prop in rule["properties"]]) for rule in rules]
                tuple_format_css.append((media_query, media_rules))
            elif "keyframes_name" in style:
                keyframes_name = style["keyframes_name"]
                keyframes_steps = style["keyframes_steps"]
                keyframes = [(step["selector"], [(prop["property"], prop["value"]) for prop in step["properties"]]) for step in keyframes_steps]
                tuple_format_css.append((keyframes_name, keyframes))
            else:
                    selector = style["selector"]
                    properties = style["properties"]
                    prop_list = [(prop["property"], prop["value"]) for prop in properties]
                    tuple_format_css.append((selector, prop_list))
        return tuple_format_css
    else:
        stylesheet = parser.parseString(css_code)
    
        css_tuples = []

        for rule in stylesheet:
            if rule.type == rule.STYLE_RULE:
                selector = rule.selectorText
                properties = []
                for property in rule.style:
                    properties.append((property.name, property.value))
                css_tuples.append((selector, properties))
            elif rule.type == rule.MEDIA_RULE:
                media_query = rule.media.mediaText.strip()
                media_rules = []

                for media_rule in rule.cssRules:
                    if media_rule.type == media_rule.STYLE_RULE:
                        selector = media_rule.selectorText
                        properties = [(property.name, property.value) for property in media_rule.style]
                        media_rules.append((selector, properties))

                css_tuples.append((media_query, media_rules))
            elif rule.type == rule.KEYFRAMES_RULE:
                keyframes_name = rule.name.strip()
                keyframes_steps = []

                for keyframe in rule.cssRules:
                    if keyframe.type == keyframe.KEYFRAME_RULE:
                        keyframe_selector = keyframe.keyText.strip()
                        keyframe_properties = [(property.name, property.value) for property in keyframe.style]
                        keyframes_steps.append((keyframe_selector, keyframe_properties))

                css_tuples.append((keyframes_name, keyframes_steps))

    
    return css_tuples

@api_view(['POST'])
def css_page_validation(req    ):
    try:
        data = req.body
        data = json.loads(data)
        css_code = data.get('data')
        keys=data.get('KEYS')
        css_tuples_a = css_to_tuples("",keys)
        css_tuples_b = css_to_tuples(css_code,'')
        common_keywords = [i for i in css_tuples_a if i in css_tuples_b]
        output={}
        if common_keywords == css_tuples_a:
           output.update({"valid": True,"message": "CSS code is valid."})
        else:
            output.update({"valid": False,"message": "CSS code is Not valid."})
        score = f'{len(common_keywords) }/{len(css_tuples_a) }'
        output.update({"score": score,
                       "Status": addCodeToDb(2,data.get('Page'),css_code,data.get('StudentId'),len(common_keywords),data.get('ProjectName'))
                       })
        return HttpResponse(json.dumps(output), content_type='application/json')
    except Exception as e:
        ErrorLog(req,e)
        return HttpResponse(f"An error occurred: {e}", status=500)


#   JS VALIDATION

@api_view(['POST'])
def js_page_validation(req):
    try:
        data = json.loads(req.body)
        js_code = data.get('data')     
        beautified_js1 = jsbeautifier.beautify(js_code)
        d1 = beautified_js1.split('\n')
        sam = data.get('KEYS')
        ans = [a.replace(' ','') for key in sam for a in d1 if str(a.replace(' ','')).__contains__(key.replace(' ',''))]
        common_keywords = [i for i in sam if any(str(j).__contains__(i.replace(' ','')) for j in ans)]
        output = {
            "valid": len(common_keywords) == len(sam),
            "message": "JS code is valid." if len(common_keywords) == len(sam) else "JS code is Not valid.",
            "score": f"{len(common_keywords)}/{len(sam)}",
            "Status": addCodeToDb(3,data.get('Page'),js_code,data.get('StudentId'),len(common_keywords),data.get('ProjectName'))
        }
        return HttpResponse(json.dumps(output), content_type='application/json')
    
    except Exception as e:
        ErrorLog(req,e)
        return HttpResponse(f"An error occurred: {e}", status=500)


#   PYTHON VALIDATION


@api_view(['POST'])
def python_page_validation(req):
    try:
        data = json.loads(req.body)
        input_string = data.get('data')
        list = data.get('KEYS')
        c_keys=[]
        for i in data.get('Regx'):
            method_match = re.search(rf'{i}', input_string)
            if method_match:
                method_definition = method_match.group(0)
                method = method_definition.replace(' ','').split('\n')
                common_keywords = [i for i in list if any(str(m).__contains__(str(i).replace(' ','')) for m in method)]            # result = subprocess.run(['python', '-c', method_definition], capture_output=True, text=True)
                for com in common_keywords:
                    c_keys.append(com)                                                                     # output = result.stdout if result.stdout else result.stderr
        output = {}
        if len(c_keys) == len(list):
            output.update({"valid": True,"message": "PYTHON code is valid."})
        else:
            output.update({"valid": False,"message": "PYTHON code is Not valid."})
        score = f'{len(c_keys) }/{len(list) }'
        if data.get('File_name')=='Python':
             output.update({"score": score,
                    "Status": addCodeToDb(4,data.get('Page'),input_string,data.get('StudentId'),len(c_keys),data.get('ProjectName'))
                    })
        if data.get('File_name')=='app_py':
             output.update({"score": score,
                    "Status": addCodeToDb(5,data.get('Page'),input_string,data.get('StudentId'),len(c_keys),data.get('ProjectName'))
                    })
        if len(c_keys)>0:
            return HttpResponse(json.dumps(output), content_type='application/json')
        else:
            return HttpResponse(json.dumps({"valid": False,"message":"Method not found","score":'0/'+str(len(list))}), content_type='application/json')
        
    except Exception as e :
        ErrorLog(req,e)
        return HttpResponse(f"An error occurred: {e}", status=500)



@api_view(['POST'])
def download_ZIP_file(req):
    try:
        name=json.loads(req.body)['Name']
        if name=='download_ZIP_file':
            # path='https://storeholder.blob.core.windows.net/tpdata/Concept/course/FlaskSample.zip'
            path=  'https://storeholder.blob.core.windows.net/internship/Internship_days_schema/internshipJSONS/FlaskSample.zip'
        else :
            path='not a valid input...'
        return HttpResponse(json.dumps({'path':path}), content_type='application/json') 
    except Exception as e:
            print(e)
            return HttpResponse(f"An error occurred: {e}", status=500)













def addCodeToDb(type,page,code,id,score,projectName):
    try:
        user = InternshipsDetails.objects.filter(StudentId=id).first()
        if user:
            match type:
                case 1: 
                    oldscore =user.HTMLScore.get(str(projectName.replace(' ', ''))).get(page+'_Score',0)
                    user.HTMLCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.HTMLScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':score*5})
                case 2:
                    oldscore =user.CSSScore.get(str(projectName.replace(' ', ''))).get(page+'_Score',0)
                    user.CSSCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.CSSScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':score*5})
                case 3:
                    oldscore =user.JSScore.get(str(projectName.replace(' ', ''))).get(page+'_Score',0)
                    user.JSCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.JSScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':score*5})
                case 4:
                    oldscore =user.PythonScore.get(str(projectName.replace(' ', ''))).get(page+'_Score',0)
                    user.PythonCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.PythonScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':score*5})
                case 5:
                    oldscore =user.AppPyScore.get(str(projectName.replace(' ', ''))).get(page+'_Score',0)
                    user.AppPyCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.AppPyScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':score*5})
            user.InternshipScores.update({str(projectName.replace(' ', '')):user.InternshipScores.get(str(projectName.replace(' ', '')),0)+int(score*5)-int(oldscore)})
            user.save()
            return ("done")
        else:
            return ('User not found...')
        
    except Exception as e:
            return HttpResponse(f"An error occurred: {e}", status=500) 