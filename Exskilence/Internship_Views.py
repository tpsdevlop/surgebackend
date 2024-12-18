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
from Exskilence.Attendance import attendance_update
from Exskilencebackend160924.settings import *
from rest_framework.decorators import api_view
from datetime import date, datetime, time, timedelta
from Exskilence.models import *
from Exskilencebackend160924.Blob_service import download_blob2, get_blob_service_client, download_list_blob2, download_list_json
import pyodbc
from Exskilence.sqlrun import *
from django.core.cache import cache
from Exskilence.filters import *
from Exskilence.ErrorLog import ErrorLog
from Exskilence.Ranking import *
CONTAINER ="internship"
LISTOFJSON = download_list_json('Internship_days_schema/internshipJSONS/',CONTAINER)
@api_view(['GET'])
def updateJsonList(request):    
    try:
        global LISTOFJSON 
        LISTOFJSON = download_list_json('Internship_days_schema/internshipJSONS/',CONTAINER)
        return HttpResponse("success")
    except Exception as e:
        ErrorLog(request,e)
        return HttpResponse(f"An error occurred: {e}", status=500)
@api_view(['POST'])
def Internship_Home(request):
    try:
        req =json.loads(request.body)
        StudentId = req.get('StudentId')
        data= LISTOFJSON.get('InternshipProject')#
        # data=json.loads(download_blob2('Internship_days_schema/internshipJSONS/InternshipProject.json',CONTAINER))
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
            'SubmissionDates':{str(projectName).replace(' ',''):{}},
        })
        tabs ={}
        tabsScores ={}
        for i in data.get('Internship_Overview')[1].get('Project_Web_Pages'):
            webpages= LISTOFJSON.get(str(i))#
            # webpages=json.loads(download_blob2('Internship_days_schema/internshipJSONS/'+ str(i)+'.json',CONTAINER)  )###########      
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
                                        "Score": user.DatabaseScore.get(str(projectName).replace(' ','')).get(str(webpages.get('Tabs')[t])+'_Score','0/'+str(len(webpages.get('Code_Validation').get(webpages.get('Tabs')[t]))))
                                    })
                else:
                    switch = {
                        'HTML': lambda: user.HTMLScore.get(str(projectName).replace(' ', '')).get(i+"_Score",'0/'+str(len(webpages.get('Code_Validation').get('HTML')))),
                        'CSS' : lambda: user.CSSScore.get(str(projectName).replace(' ', '')).get(i+"_Score",'0/'+str(len(webpages.get('Code_Validation').get("CSS")))),
                        'JS'  : lambda: user.JSScore.get(str(projectName).replace(' ', '')).get(i+"_Score",'0/'+str(len(webpages.get('Code_Validation').get('JS')))),
                        'Python':lambda: user.PythonScore.get(str(projectName).replace(' ', '')).get(i+"_Score",'0/'+str(len(webpages.get('Code_Validation').get('Python' )))),
                        'app.py':lambda: user.AppPyScore.get(str(projectName).replace(' ', '')).get(i+"_Score",'0/'+str(len(webpages.get('Code_Validation').get('App_py'))))
                    }
                    result = switch.get(webpages.get('Tabs')[t], lambda: "---")()
                    progress.append({
                                        "Sl_No": t+1,
                                        "Pages": webpages.get('Tabs')[t],
                                        "Score": result
                                    })
                tabsScores.update({str(i)+'_Score':progress})
        dateAndTime = {}
        c =0
        if user.ProjectDateAndTime.get(str(projectName).replace(' ','')) == None or user.ProjectDateAndTime.get(str(projectName).replace(' ','')) == {}:
            for i in data.get('Internship_Overview')[1].get('Project_Web_Pages'):
                user.ProjectDateAndTime.get(str(projectName).replace(' ','')).update({i:{
                    'Start_Time':datetime.utcnow().__add__(timedelta(days=c,hours=5,minutes=30)),
                    'End_Time':datetime.utcnow().__add__(timedelta(days=c,hours=42,minutes=30))
                }})
                c = c+1
            user.save()
        for j in user.ProjectDateAndTime.get(str(projectName).replace(' ','')):
            dateAndTime.update({j:
                                {
                                    'Start_Time':str(user.ProjectDateAndTime.get(str(projectName).replace(' ','')).get(j).get('Start_Time')),
                                    'End_Time':str(user.ProjectDateAndTime.get(str(projectName).replace(' ','')).get(j).get('End_Time'))
                                } 
                                })
            
        Statuses = {
            'Progress':{},
            'Status':{}
        }
        for i in user.ProjectStatus.get(str(projectName).replace(' ','')):
            stat =(user.ProjectStatus.get(str(projectName).replace(' ','')).get(i))
            if stat == 0  :
                Statuses.get('Progress').update({i:'0'})
            elif stat == 2:
                Statuses.get('Progress').update({i:'100'})
            else:
                for page in data.get('Internship_Overview')[1].get('Project_Web_Pages'):
                    keys = user.SubmissionDates.get(str(projectName.replace(' ', ''))).keys()
                    submited = 0
                    if page != 'Database_setup':
                        for tab in webpages.get('Tabs'):
                            key = page+'_'+tab if tab != 'app.py' else page+'_'+'AppPy'
                            if (key in keys):
                                submited = submited +1
                    else:
                        for tab in  webpages.get('Tabs'):
                            key = tab+'_Database'
                            if (key in keys):
                                submited = submited +1

                    if submited == len( webpages.get('Tabs')):
                        Statuses.get('Progress').update({i:'Completed'})
                    else:
                        Statuses.get('Progress').update({i:str((submited/len( webpages.get('Tabs')))*100)})
            dateobj = user.ProjectDateAndTime.get(str(projectName).replace(' ','')).get(i)
            if datetime.utcnow().__add__(timedelta(hours=5,minutes=30)) >= dateobj.get('Start_Time')  :
                Statuses.get('Status').update({i:'Opened'})
            else:
                keys = list(user.ProjectStatus.get(str(projectName).replace(' ','')).keys())
                index = keys.index(i)
                if index-1 < 0:
                    Statuses.get('Status').update({i:"Locked"})
                elif user.ProjectStatus.get(str(projectName).replace(' ','')).get(keys[index-1]) == 2:
                    Statuses.get('Status').update({i:"Opened"})
                else:
                    Statuses.get('Status').update({i:'Locked'})
        out ={
            "Sidebar":data,
            "data":tabs,
            "Status_Data":Statuses,#user.ProjectStatus.get(str(projectName).replace(' ',''),{}),
            "Scores":tabsScores,
            "DateAndTime":dateAndTime
            
        }
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps(out), content_type='application/json')
    except Exception as e:
        attendance_update(data.get('StudentId'))
        ErrorLog(request,e)
        return HttpResponse(f"An error occurred: {e}", status=500)
# setInternshipTime TEST
def setInternshipTime():
    try:
        data= LISTOFJSON.get('InternshipProject')#json.loads(download_blob2('Internship_days_schema/internshipJSONS/InternshipProject.json',CONTAINER))
        projectName = data.get('Internship_Project').get('Project_Name')
        user = InternshipsDetails.objects.filter(StudentId ="24MRIT0011").first()
        c =0
        for i in data.get('Internship_Overview')[1].get('Project_Web_Pages'):

            user.ProjectDateAndTime.get(str(projectName).replace(' ','')).update({i:{
                'Start_Time':datetime.utcnow().__add__(timedelta(days=c,hours=5,minutes=30)),
                'End_Time':datetime.utcnow().__add__(timedelta(days=c,hours=42,minutes=30))
            }})
            c = c+1
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
        data= LISTOFJSON.get(str(page))#json.loads(download_blob2('Internship_days_schema/internshipJSONS/'+ str(page)+'.json',CONTAINER))
        user = InternshipsDetails.objects.filter(StudentId=res.get('StudentId')).first()
        if user:
            if page.startswith('Database'):
                jdata = {"Response":  user.DatabaseCode.get(str(projectName).replace(' ', ''),{})}
            else:
                switch = {
                        'HTML': lambda: user.HTMLCode.get(str(projectName).replace(' ', '')).get(page,''),
                        'CSS' : lambda: user.CSSCode.get(str(projectName).replace(' ', '')).get(page,''),
                        'JS'  : lambda: user.JSCode.get(str(projectName).replace(' ', '')).get(page,'' ),
                        'Python':lambda: user.PythonCode.get(str(projectName).replace(' ', '')).get(page,''),
                        'app.py':lambda: user.AppPyCode.get(str(projectName).replace(' ', '')).get(page,'' ),
                    }
                result = {}#switch.get(data.get('Tabs')[page], lambda: "0/0")()
                for i in data.get('Tabs'):
                    if i == 'app.py':
                        result.update({'app_py':switch.get(i, lambda: "0/0")()})
                    else:
                        result.update({i:switch.get(i, lambda: "0/0")()})
                jdata = {"Response":result}
            if user.ProjectStatus.get(str(projectName).replace(' ', '')).get(page,0)<=0:
                user.ProjectStatus.get(str(projectName).replace(' ', '')).update({page:1})
                user.save()
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
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps(data), content_type='application/json') 
    except Exception as e:
            attendance_update(data.get('StudentId'))
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
            oldscore=user.DatabaseScore.get(str(projectName).replace(' ', ''),{}).get(table+'_Score','0/0').split('/')[0]
            user.DatabaseCode.get(str(projectName).replace(' ', ''),{}).update({table:input_string})
            user.DatabaseScore.get(str(projectName).replace(' ', ''),{}).update({table+'_Score':str(len(common_keywords))+'/'+str(len(list))})
            user.InternshipScores.update({str(projectName).replace(' ', ''):user.InternshipScores.get(str(projectName).replace(' ', ''),0)+len(common_keywords)-int(oldscore)})#=user.Score+len(common_keywords)-int(oldscore)
            user.save()
            output = {}
            if len(common_keywords) == len(list):
                output.update({"valid": True,"message": "Database_setup code is valid."})
            else:
                output.update({"valid": False,"message": "Database_setup code is Not valid."})
            score = f'{len(common_keywords) }/{len(list) }'
            output.update({"score": score})
            attendance_update(data.get('StudentId'))
            return HttpResponse(json.dumps(output), content_type='application/json')

        else:
            attendance_update(data.get('StudentId'))
            return HttpResponse('User does not exist', status=404)
    except Exception as e:
            attendance_update(data.get('StudentId'))
            ErrorLog(req,e)
            return HttpResponse(f"An error occurred: {e}", status=500)
    
#   HTML VALIDATION
def alltags(data,allowedtags,BODY):
    try:
        tags = r'<([a-zA-Z0-9]+)(\s*[^>]*)?>'
        ctags = r'</([a-zA-Z0-9]+)(\s*[^>]*)?>'
        self_closing_pattern = r'<([a-zA-Z][a-zA-Z0-9]*)\s*[^>]*\/?>'
        selfClosingTags = [
          "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
          "meta", "param", "source", "track", "wbr"
        ]
        t=re.findall(tags ,  data)
        t2=re.findall(ctags ,  data)
        sct=re.findall(self_closing_pattern ,  data)
        
        filtered_tags = [tag for tag in sct if tag in selfClosingTags    ]
        alltags       = [tag for tag in t if tag not in selfClosingTags  ]
        closing       = [tag for tag in t2 if tag not in selfClosingTags ]
        ot=[]
        ct=[]
        
        for tag in alltags:
            if tag[0] not in selfClosingTags:
                ot.append(tag[0])
        for tag in closing:
            if tag[0] not in selfClosingTags:
                ct.append(tag[0])
        if BODY:
            for tag in ot:
                if tag  in allowedtags:
                    print('Invalid HTML BODY ********** tag',tag)
                    return 0
            for tag in ct:
                if tag  in allowedtags:
                    print('Invalid HTML BODY ********** tag',tag)
                    return 0
            out = (len(ot)-len(ct)) if (len(ot)-len(ct)) > 0 else (len(ot)-len(ct)) * -1
            if out > 0:
                return out
            else:
                return -1                
        else:
            for tag in ot:
                if tag not in allowedtags:
                    print('Invalid HTML ********** tag',tag)
                    return False
            for tag in ct:
                if tag not in allowedtags:
                    print('Invalid HTML ********** tag',tag)
                    return False
        valid = True
        for tag in alltags:
            if tag[0] not in selfClosingTags and tag[0] not in ct:
                valid = False
                print('Invalid HTML ********** tag',tag[0])
                break
            else:
                if tag[0] not in selfClosingTags:
                    ct.remove(tag[0])
                    ot.remove(tag[0])
                    valid = True
        if valid is False:
            print('Invalid HTML')
            print('ot',ot)
            print('ct',ct)
            return False
        if len(ot) != len(ct):
            print('Invalid HTML')
            print('ot',ot)
            print('ct',ct)
            return False
        return True
    except Exception as e:
        print(e)
        return False
def extract_tag_content(data, tags):
            contents = {}
            for tag in tags:
                pattern = rf"<{tag}.*?>(.*?)</{tag}>"
                match = re.search(pattern, data, re.DOTALL)
                if match:
                    contents[tag] = match.group(1).strip()
            return contents
def HTMLStructure(codedata):
    try:
        ot = codedata.replace(' ','').replace('>',' > '). count('<html')
        ct = codedata.replace(' ','').replace('>',' > '). count('</html >')
        if ot != ct:
            return False
        data = BeautifulSoup((codedata), 'html.parser')
        htmltag =data.html.contents
        htmlvalid = ['head', 'body']
        hot = codedata.replace(' ','').replace('>',' > '). count('<head ')
        hct = codedata.replace(' ','').replace('>',' > '). count('</head >')

        bct = codedata.replace(' ','').replace('>',' > '). count('</body >')
        bot = codedata.replace(' ','').replace('>',' > '). count('<body')

        if hot != hct or hot != 1 or hct != 1:
            return False
        if bot != bct or bot != 1 or bct != 1:
            return False
        for tag in htmltag:
            if tag.name is not None and tag.name not in htmlvalid:
                return False    
        headvalid = data.head.contents
        HTMLdata = extract_tag_content(codedata, htmlvalid)
        htmlstrucHead = ['title', 'meta', 'link', 'style', 'script']
        htmlstrucbbody = ['title', 'meta', 'link', 'style', 'script','head','html']
        Headdatavalid = alltags(HTMLdata.get('head'), htmlstrucHead, False)
        if Headdatavalid == False :
            return False

        for tag in headvalid:
            if tag.name is not None and tag.name not in htmlstrucHead:
                return False
        if not data.body:
            return False
        codebody = data.body.contents
        for tag in codebody:
            if tag.name is not None and tag.name in htmlstrucbbody and tag.name in htmlvalid and tag.name in ['html']:
                return False
        return True
            
    except Exception as e:
        print(e)
        return f"An error occurred: {e}"
  
def jsonToTuple(code):
    tuple_format = []
    for element in code:
        tag = element["tag"]
        attrs = element["attributes"]
        
        if attrs:
            for attr_name, attr_value in attrs.items():
                tuple_format.append((tag, attr_name, attr_value))
        else:
            tuple_format.append((tag, None, None))
    tuple_format=[
                (tag.lower().replace(" ", "").replace(" =", "=").replace("= ", "=").replace(" ,", ",").replace(", ", ","), attr.lower().replace(" ", "").replace(" =", "=").replace("= ", "=").replace(" ,", ",").replace(", ", ",") if isinstance(attr, str) else attr, 
                 [value.lower().replace(" ", "").replace(" =", "=").replace("= ", "=").replace(" ,", ",").replace(", ", ",") if isinstance(value, str) else value for value in (value if isinstance(value, list) else [value])])
                for tag, attr, value in tuple_format
                ]
    tuple_format=[
                        (tag, attr, value) 
                        for tag, attr, values in tuple_format 
                        for value in (values if isinstance(values, list) else [values])
                    ]
    return tuple_format
@api_view(['POST'])
def html_page_validation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            htmlcode = data.get('data')
            keys=data.get('KEYS')
            if not htmlcode:
                output = {"valid": False,"message": "No HTML code provided"}
                sample_elements=(jsonToTuple(keys))
                score = f'0/{len(sample_elements) }'
                data.update({"Score": score,"Result":score})
                attendance_update(data.get('StudentId'))
                return HttpResponse(json.dumps(output), content_type='application/json')
            
            user_soup = BeautifulSoup(htmlcode, 'html.parser')
            def extract_tags_and_attributes(soup):
                elements = soup.find_all(True)
                tag_attr_list = []

                for element in elements:
                    tag = element.name
                    attrs = element.attrs
                    
                    if attrs:
                        for attr_name, attr_value in attrs.items():
                            tag_attr_list.append((tag, attr_name, attr_value))
                    else:
                        tag_attr_list.append((tag, None, None))
                tag_attr_list=[
                (tag.lower().replace(" ", "").replace(" =", "=").replace("= ", "=").replace(" ,", ",").replace(", ", ","), attr.lower().replace(" ", "").replace(" =", "=").replace("= ", "=").replace(" ,", ",").replace(", ", ",") if isinstance(attr, str) else attr, 
                 [value.lower().replace(" ", "").replace(" =", "=").replace("= ", "=").replace(" ,", ",").replace(", ", ",") if isinstance(value, str) else value for value in (value if isinstance(value, list) else [value])])
                for tag, attr, value in tag_attr_list
                ]
                tag_attr_list=[
                        (tag, attr, value) 
                        for tag, attr, values in tag_attr_list 
                        for value in (values if isinstance(values, list) else [values])
                    ]
                return tag_attr_list
            sample_elements=(jsonToTuple(keys))
            if HTMLStructure(htmlcode) == True:
                user_elements = extract_tags_and_attributes(user_soup)
                common_keywords = [i for i in user_elements if i in sample_elements]
                headbodydata = extract_tag_content(htmlcode, ['head', 'body'])
                bodydatavalid = alltags(headbodydata.get('body'), ['title', 'meta', 'link', 'style', 'script','head','html','body'], True)
                if bodydatavalid == False  :
                    common_keywords = []
                    length = 0
                else:
                    length = len(common_keywords) - (0 if bodydatavalid == -1 else bodydatavalid)
            else:
                common_keywords = []
                length = 0
            output = {}
            if length == len(sample_elements):
                output.update({"valid": True,"message": "HTML code is valid."})
            else:
                output.update({"valid": False,"message": "HTML code is Not valid."})

            score = f'{len(common_keywords) }/{len(sample_elements) }'
            output.update({"score": score,
                       "Status": addCodeToDb(1,data.get('Page'),htmlcode,data.get('StudentId'),len(common_keywords),len(sample_elements),data.get('ProjectName'))
                       })
            attendance_update(data.get('StudentId'))
            return HttpResponse(json.dumps(output), content_type='application/json')

        except Exception as e:
            attendance_update(data.get('StudentId'))
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
        tuple_format_css=[(i[0].lower().replace(" ", "").replace(" =", "=").replace("= ", "=").replace(" ,", ",").replace(", ", ","),[(j[0].lower().replace(" ", "").replace(" =", "=").replace("= ", "=").replace(" ,", ",").replace(", ", ","),j[1]) for j in i[1]]) for i in tuple_format_css]
        return tuple_format_css
    else:
        stylesheet = parser.parseString(css_code)
        css_tuples = []

        for rule in stylesheet:
            if rule.type == rule.STYLE_RULE:
                selector = rule.selectorText
                properties = []
                for property in rule.style:
                        if str(property.value).__contains__('#') == True :
                            values = property.value.split()
                            for i in range(len(values)):
                                if str(values[i]).startswith('#') and len(str(values[i]).replace(',','')) == 4:
                                    exc = str(values[i])
                                    if str(values[i]).__contains__(','):

                                        exc2 = '#' + exc[1]+exc[1]+exc[2]+exc[2]+exc[3]+exc[3]+','
                                    else:
                                        exc2 = '#' + exc[1]+exc[1]+exc[2]+exc[2]+exc[3]+exc[3]
                                    values[i] = exc2
                            newvalues = ' '.join(values)
                            properties.append((property.name, newvalues))
                        else:
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
    css_tuples=[(i[0].lower().replace(" ", "").replace(" =", "=").replace("= ", "=").replace(" ,", ",").replace(", ", ","),[(j[0].lower().replace(" ", "").replace(" =", "=").replace("= ", "=").replace(" ,", ",").replace(", ", ","),j[1]) for j in i[1]]) for i in css_tuples]
    
    return css_tuples
def tupletolist(css_tuples,tupleKeys):
 try:
    anskey =[]
    tupleKey =[]
    ansvalue=[]
    tupleValue=[]
    out =[]
    for i in range(len(css_tuples)):
        css_tuples[i]=list(css_tuples[i])
        anskey.append(css_tuples[i][0])
        ansvalue.append(css_tuples[i][1])
    for i in range(len(tupleKeys)):
        tupleKeys[i]=list(tupleKeys[i])
        tupleKey.append(tupleKeys[i][0])
        tupleValue.append(tupleKeys[i][1])
    for i in  anskey:
        if i in tupleKey:
            ansv = ansvalue[anskey.index(i)]
            tuplev = tupleValue[tupleKey.index(i)]
            com = [i1 for i1 in ansv if i1 in tuplev]
            if len(com) == len(tuplev):
                out.append([i,com])
    return out
 except:
    return [i for i in tupleKeys if i in css_tuples]
@api_view(['POST'])
def css_page_validation(req    ):
    try:
        data = req.body
        data = json.loads(data)
        css_code = data.get('data')
        keys=data.get('KEYS')
        css_tuples_a = css_to_tuples("",keys)
        css_tuples_b = css_to_tuples(css_code,'')
        common_keywords = tupletolist(css_tuples_b,css_tuples_a)
        # print(':::::::::::::::::::::::::::::::::::::::::::::::::::'        )
        # for cb in css_tuples_b:
        #     print(cb) 
        # print(':::::::::::::::::::::::::::::::::::::::::::::::::::'        )
        # for ca in common_keywords:
        #     print(ca)
        # print(':::::::::::::::::::::::::::::::::::::::::::::::::::')
        output={}
        if len(common_keywords) == len(css_tuples_a):
           output.update({"valid": True,"message": "CSS code is valid."})
        else:
            output.update({"valid": False,"message": "CSS code is Not valid."})
        score = f'{len(common_keywords) }/{len(css_tuples_a) }'
        output.update({"score": score,
                       "Status": addCodeToDb(2,data.get('Page'),css_code,data.get('StudentId'),len(common_keywords),len(css_tuples_a),data.get('ProjectName'))
                       })
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps(output), content_type='application/json')
    except Exception as e:
        attendance_update(data.get('StudentId'))
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
            "Status": addCodeToDb(3,data.get('Page'),js_code,data.get('StudentId'),len(common_keywords),len(sam),data.get('ProjectName'))
        }
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps(output), content_type='application/json')
    
    except Exception as e:
        attendance_update(data.get('StudentId'))
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
                    "Status": addCodeToDb(4,data.get('Page'),input_string,data.get('StudentId'),len(c_keys),len(list),data.get('ProjectName'))
                    })
        if data.get('File_name')=='app_py':
             output.update({"score": score,
                    "Status": addCodeToDb(5,data.get('Page'),input_string,data.get('StudentId'),len(c_keys),len(list),data.get('ProjectName'))
                    })
        if len(c_keys)>0:
            attendance_update(data.get('StudentId'))
            return HttpResponse(json.dumps(output), content_type='application/json')
        else:
            attendance_update(data.get('StudentId'))
            return HttpResponse(json.dumps({"valid": False,"message":"Method not found","score":'0/'+str(len(list))}), content_type='application/json')
        
    except Exception as e :
        attendance_update(data.get('StudentId'))
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
        attendance_update(json.loads(req.body)['StudentId'])
        return HttpResponse(json.dumps({'path':path}), content_type='application/json') 
    except Exception as e:
            attendance_update(json.loads(req.body)['StudentId'])
            ErrorLog(req,e)
            return HttpResponse(f"An error occurred: {e}", status=500)


@api_view(['POST'])
def  updateScore(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        codedata = data['Ans']
        score = data['Score']
        data.update({"Score": score if int(str(score).split('/')[0])<=int(str(score).split('/')[1]) else str(score).split('/')[1]+"/"+str(score).split('/')[1],"Result":score})
        output={}
        if int(str(score).split('/')[0]) ==  int(str(score).split('/')[1]):
           output.update({"valid": True,"message": data.get('Subject')+" code is valid."})
        else:
            output.update({"valid": False,"message": data.get('Subject')+" code is Not valid."})
        subject_mapping = {'HTML': 1,'CSS': 2,'JS': 3,'Java_Script':  3,'Python': 4,'app_py': 5,'App_py': 5,'db': 6,'Database_setup':6}
        output.update({"score": score,
                       "Status": addCodeToDb(subject_mapping.get(data.get('Subject'), 0),data.get('Page'),codedata,data.get('StudentId'),int(str(score).split('/')[0]),int(str(score).split('/')[1]),data.get('ProjectName'),data.get('Tabs'))
                       })
        attendance_update(data.get('StudentId'))
        return HttpResponse(json.dumps(output), content_type='application/json')
    except Exception as e:
        data = json.loads(request.body.decode('utf-8'))
        attendance_update(data.get('StudentId'))
        ErrorLog(request,e)
        return HttpResponse(f"An error occurred: {e}", status=500)

def addCodeToDb(type,page,code,id,score,outof,projectName,alltabs):
    try:
        user = InternshipsDetails.objects.filter(StudentId=id).first()
        if user:
            match type:
                case 1: 
                    oldscore =user.HTMLScore.get(str(projectName.replace(' ', ''))).get(page+'_Score','0/0').split('/')[0]
                    user.HTMLCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.HTMLScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':str(score)+'/'+str(outof)})
                    user.SubmissionDates.get(str(projectName.replace(' ', ''))).update({page+'_HTML':datetime.utcnow().__add__(timedelta(hours=5,minutes=30)).strftime("%Y-%m-%d %H:%M:%S")})
                case 2:
                    oldscore =user.CSSScore.get(str(projectName.replace(' ', ''))).get(page+'_Score',   '0/0').split('/')[0]
                    user.CSSCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.CSSScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':str(score)+'/'+str(outof)})
                    user.SubmissionDates.get(str(projectName.replace(' ', ''))).update({page+'_CSS':datetime.utcnow().__add__(timedelta(hours=5,minutes=30)).strftime("%Y-%m-%d %H:%M:%S")})
                case 3:
                    oldscore =user.JSScore.get(str(projectName.replace(' ', ''))).get(page+'_Score','0/0').split('/')[0]
                    user.JSCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.JSScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':str(score)+'/'+str(outof)})
                    user.SubmissionDates.get(str(projectName.replace(' ', ''))).update({page+'_JS':datetime.utcnow().__add__(timedelta(hours=5,minutes=30)).strftime("%Y-%m-%d %H:%M:%S")})
                case 4:
                    oldscore =user.PythonScore.get(str(projectName.replace(' ', ''))).get(page+'_Score','0/0').split('/')[0]
                    user.PythonCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.PythonScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':str(score)+'/'+str(outof)})
                    user.SubmissionDates.get(str(projectName.replace(' ', ''))).update({page+'_Python':datetime.utcnow().__add__(timedelta(hours=5,minutes=30)).strftime("%Y-%m-%d %H:%M:%S")})
                case 5:
                    oldscore =user.AppPyScore.get(str(projectName.replace(' ', ''))).get(page+'_Score','0/0').split('/')[0]
                    user.AppPyCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.AppPyScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':str(score)+'/'+str(outof)})
                    user.SubmissionDates.get(str(projectName.replace(' ', ''))).update({page+'_AppPy':datetime.utcnow().__add__(timedelta(hours=5,minutes=30)).strftime("%Y-%m-%d %H:%M:%S")})
                case 6:
                    oldscore =user.DatabaseScore.get(str(projectName.replace(' ', ''))).get(page+'_Score','0/0').split('/')[0]
                    user.DatabaseCode.get(str(projectName.replace(' ', ''))).update({page:code})
                    user.DatabaseScore.get(str(projectName.replace(' ', ''))).update({page+'_Score':str(score)+'/'+str(outof)})
                    user.SubmissionDates.get(str(projectName.replace(' ', ''))).update({page+'_Database':datetime.utcnow().__add__(timedelta(hours=5,minutes=30)).strftime("%Y-%m-%d %H:%M:%S")})
            user.SubmissionDates.get(str(projectName.replace(' ', ''))).update({page if type!=6 else 'Database':datetime.utcnow().__add__(timedelta(hours=5,minutes=30)).strftime("%Y-%m-%d %H:%M:%S")})
            user.SubmissionDates.get(str(projectName.replace(' ', ''))).update({'DateAndTime':datetime.utcnow().__add__(timedelta(hours=5,minutes=30)).strftime("%Y-%m-%d %H:%M:%S")})
            user.InternshipScores.update({str(projectName.replace(' ', '')):user.InternshipScores.get(str(projectName.replace(' ', '')),0)+int(score)-int(oldscore)})
            keys = user.SubmissionDates.get(str(projectName.replace(' ', ''))).keys()
            submited = 0
            if type!=6:
                   for tab in alltabs:
                       key = page+'_'+tab if tab != 'app.py' else page+'_'+'AppPy'
                       if (key in keys):
                        submited = submited +1

            else:
                for tab in alltabs:
                       key = tab+'_Database'
                       if (key in keys):
                        submited = submited +1

            if submited == len(alltabs):
                user.ProjectStatus.get(str(projectName.replace(' ', ''))).update({
                    page if type!= 6 else 'Database_setup':2
                })
            user.save()
            return ("done")
        else:
            return ('User not found...')
        
    except Exception as e:
            return f"An error occurred: {e}"
    
@api_view(['POST']) 
def get_score(req):
    try:
        data = json.loads(req.body)
        id = data.get('StudentId')
        pagename=data.get('Page_name')
        projectName=data.get('ProjectName')

        user = InternshipsDetails.objects.filter(StudentId=id).first()
        if user:
            if str(pagename).startswith('Database_'):
                user_data = {
                    "Page_name":pagename,
                    "Score":user.InternshipScores.get(str(projectName.replace(' ', '')),0),
                }
                user_data.update(user.DatabaseCode.get(str(projectName.replace(' ', '')),''))
                user_data.update(user.DatabaseScore.get(str(projectName.replace(' ', '')),'')) 
            else:
                user_data = {
                    "Page_name":pagename,
                    "Score":user.InternshipScores.get(str(projectName.replace(' ', '')),0),
                }
                if user.HTMLCode.get(str(projectName.replace(' ', '')),{}).get(pagename,'')!="":
                    user_data.update({
                        "HTML_Code":user.HTMLCode.get(str(projectName.replace(' ', '')),{}).get(pagename,''),
                        "HTML_Score": user.HTMLScore.get(str(projectName.replace(' ', '')),{}).get(str(pagename)+'_Score',0) 
                    })
                if user.CSSCode.get(str(projectName.replace(' ', '')),{}).get(pagename,'')!="":
                    user_data.update({
                        "CSS_Code":user.CSSCode.get(str(projectName.replace(' ', '')),{}).get(pagename,''),
                        "CSS_Score": user.CSSScore.get(str(projectName.replace(' ', '')),{}).get(str(pagename)+'_Score',0)
                        })
                if user.JSCode.get(str(projectName.replace(' ', '')),{}).get(pagename,'')!="":
                    user_data.update({
                        "JS_Code":user.JSCode.get(str(projectName.replace(' ', '')),{}).get(pagename,''),
                        "JS_Score": user.JSScore.get(str(projectName.replace(' ', '')),{}).get(str(pagename)+'_Score',0)
                     })
                if user.PythonCode.get(str(projectName.replace(' ', '')),{}).get(pagename,'')!="":
                    user_data.update({
                        "Python_Code":user.PythonCode.get(str(projectName.replace(' ', '')),{}).get(pagename,''),
                        "Python_Score": user.PythonScore.get(str(projectName.replace(' ', '')),{}).get(str(pagename)+'_Score',0)
                     })
                if user.AppPyCode.get(str(projectName.replace(' ', '')),{}).get(pagename,'')!="":
                    user_data.update({
                        "App_py_Code":user.AppPyCode.get(str(projectName.replace(' ', '')),{}).get(pagename,''),
                        "App_py_Score": user.AppPyScore.get(str(projectName.replace(' ', '')),{}).get(str(pagename)+'_Score',0)
                     })
            return HttpResponse(json.dumps(user_data), content_type='application/json') 
        else:
            return HttpResponse('Error! User does not exist', status=404)
    except Exception as e:
            return HttpResponse(f"An error occurred: {e}", status=500)
    
@api_view(['POST']) 
def  project_score(req):
    try:
        data = json.loads(req.body)
        email = data.get('StudentId')
        projectName=data.get('ProjectName')

        user = InternshipsDetails.objects.filter(StudentId=email).first()
        if user:
            user_data = {
                "Score":user.InternshipScores.get(str(projectName.replace(' ', '')),0),
                "HTML":user.HTMLScore.get(str(projectName.replace(' ', '')),0),
                "CSS":user.CSSScore.get(str(projectName.replace(' ', '')),0),
                "JS":user.JSScore.get(str(projectName.replace(' ', '')),0),
                "Python":user.PythonScore.get(str(projectName.replace(' ', '')),0),
                "App_py":user.AppPyScore.get(str(projectName.replace(' ', '')),0),
                "Database_Score":user.DatabaseScore.get(str(projectName.replace(' ', '')),0)
            }
            return HttpResponse(json.dumps(user_data), content_type='application/json') 
        else:
            return HttpResponse('Error! User does not exist', status=404)
    except Exception as e:
            data = json.loads(req.body.decode('utf-8'))
            attendance_update(data.get('StudentId'))
            ErrorLog(req,e)
            return HttpResponse(f"An error occurred: {e}", status=500)