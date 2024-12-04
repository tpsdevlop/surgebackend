# import json
# import random
# import re
# import subprocess
# from rest_framework.decorators import api_view
# from bs4 import BeautifulSoup
# import cssutils
# from django.http import  HttpResponse
# import jsbeautifier


# import json
# import cssutils
# from django.http import HttpResponse

# from Exskilencebackend160924.Blob_service import download_blob, download_list_blob
# from  .models import InternshipDetails

    
# def css_to_tuples(css_code,KEYS):
#     parser = cssutils.CSSParser()
#     if KEYS :
#         tuple_format_css = []

#         for style in KEYS:
#             if "media_query" in style:
#                 media_query = style["media_query"]
#                 rules = style["rules"]
#                 media_rules = [(rule["selector"], [(prop["property"], prop["value"]) for prop in rule["properties"]]) for rule in rules]
#                 tuple_format_css.append((media_query, media_rules))
#             elif "keyframes_name" in style:
#                 keyframes_name = style["keyframes_name"]
#                 keyframes_steps = style["keyframes_steps"]
#                 keyframes = [(step["selector"], [(prop["property"], prop["value"]) for prop in step["properties"]]) for step in keyframes_steps]
#                 tuple_format_css.append((keyframes_name, keyframes))
#             else:
#                     selector = style["selector"]
#                     properties = style["properties"]
#                     prop_list = [(prop["property"], prop["value"]) for prop in properties]
#                     tuple_format_css.append((selector, prop_list))
#         return tuple_format_css
#     else:
#         stylesheet = parser.parseString(css_code)
    
#         css_tuples = []

#         for rule in stylesheet:
#             if rule.type == rule.STYLE_RULE:
#                 selector = rule.selectorText
#                 properties = []
#                 for property in rule.style:
#                     properties.append((property.name, property.value))
#                 css_tuples.append((selector, properties))
#             elif rule.type == rule.MEDIA_RULE:
#                 media_query = rule.media.mediaText.strip()
#                 media_rules = []

#                 for media_rule in rule.cssRules:
#                     if media_rule.type == media_rule.STYLE_RULE:
#                         selector = media_rule.selectorText
#                         properties = [(property.name, property.value) for property in media_rule.style]
#                         media_rules.append((selector, properties))

#                 css_tuples.append((media_query, media_rules))
#             elif rule.type == rule.KEYFRAMES_RULE:
#                 keyframes_name = rule.name.strip()
#                 keyframes_steps = []

#                 for keyframe in rule.cssRules:
#                     if keyframe.type == keyframe.KEYFRAME_RULE:
#                         keyframe_selector = keyframe.keyText.strip()
#                         keyframe_properties = [(property.name, property.value) for property in keyframe.style]
#                         keyframes_steps.append((keyframe_selector, keyframe_properties))

#                 css_tuples.append((keyframes_name, keyframes_steps))

    
#     return css_tuples

# @api_view(['POST'])
# def css_compare(req    ):
#     try:
#         data = req.body
#         res = json.loads(data)
#         css_code = res['data']
#         keys=res['KEYS']
#         css_tuples_a = css_to_tuples("",keys)
#         css_tuples_b = css_to_tuples(css_code,'')
#         common_keywords = [i for i in css_tuples_a if i in css_tuples_b]
#         print(len(common_keywords),len(css_tuples_a))
#         output={}
#         if common_keywords == css_tuples_a:
#            output.update({"valid": True,"message": "CSS code is valid."})
#         else:
#             output.update({"valid": False,"message": "CSS code is Not valid."})
#         score = f'{len(common_keywords) }/{len(css_tuples_a) }'
#         output.update({"score": score,
#                        "Status": addCodeToDb(2,res['Page'],css_code,res['Email'],len(common_keywords))
#                        })
#         return HttpResponse(json.dumps(output), content_type='application/json')
#     except Exception as e:
#         return HttpResponse(f"An error occurred: {e}", status=500)
    
# @api_view(['POST'])
# def js_test(req):
#     try:
#         data = json.loads(req.body)
#         js_code = data['data']         
#         beautified_js1 = jsbeautifier.beautify(js_code)
#         d1 = beautified_js1.split('\n')
#         sam = data['KEYS'] 
#         ans = [a.replace(' ','') for key in sam for a in d1 if str(a.replace(' ','')).__contains__(key.replace(' ',''))]
#         common_keywords = [i for i in sam if any(str(j).__contains__(i.replace(' ','')) for j in ans)]
#         # print(sam,'\n\n\n',ans,'\n\n\n',common_keywords)
#         output = {
#             "valid": len(common_keywords) == len(sam),
#             "message": "JS code is valid." if len(common_keywords) == len(sam) else "JS code is Not valid.",
#             "score": f"{len(common_keywords)}/{len(sam)}",
#             "Status": addCodeToDb(3,data['Page'],js_code,data['Email'],len(common_keywords))
#         }
#         print('output',output)
#         return HttpResponse(json.dumps(output), content_type='application/json')
    
#     except Exception as e:
#         return HttpResponse(f"An error occurred: {e}", status=500)

# def jsonToTuple(code):
#     tuple_format = []

#     for element in code:
#        tag = element["tag"]
#        attributes = element["attributes"]
#        for attr, value in attributes.items():
#            tuple_format.append((tag, attr, value))
#     return tuple_format

# @api_view(['POST'])
# def html_page(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             htmlcode = data.get('data')
#             keys=data.get('KEYS')
#             if not htmlcode:
#                 return HttpResponse("No HTML data provided", status=400)
            
#             user_soup = BeautifulSoup(htmlcode, 'html.parser')
#             def extract_tags_and_attributes(soup):
#                 elements = soup.find_all(True)  
#                 tag_attr_list = []
#                 for element in elements:
#                     tag = element.name
#                     attrs = element.attrs
#                     for attr_name, attr_value in attrs.items():
#                         tag_attr_list.append((tag, attr_name, attr_value))
#                 return tag_attr_list
#             sample_elements=(jsonToTuple(keys))
#             user_elements = extract_tags_and_attributes(user_soup)
#             common_keywords = [i for i in sample_elements if i in user_elements]
#             output = {}
#             print('sample_elements','\n\n','user_elements','\n\n','user_soup')
#             if len(common_keywords) == len(sample_elements):
#                 output.update({"valid": True,"message": "HTML code is valid."})
#             else:
#                 output.update({"valid": False,"message": "HTML code is Not valid."})

#             score = f'{len(common_keywords) }/{len(sample_elements) }'
#             output.update({"score": score,
#                        "Status": addCodeToDb(1,data['Page'],htmlcode,data['Email'],len(common_keywords))
#                        })
#             print('output',output)
#             return HttpResponse(json.dumps(output), content_type='application/json')

#         except Exception as e:
#             return HttpResponse(f"An error occurred: {e}", status=500)
#     else:
#         return HttpResponse("Method Not Allowed", status=405)


# @api_view(['POST'])
# def python_page(req):
#     try:
#         data = json.loads(req.body)
#         input_string = data['data']
#         list = data['KEYS']
#         c_keys=[]
#         for i in data['Regx']:
#             method_match = re.search(rf'{i}', input_string)
#             # print(method_match.group(0))
#             if method_match:
#                 method_definition = method_match.group(0)
#                 print(method_definition)
#                 method = method_definition.replace(' ','').split('\n')
#                 common_keywords = [i for i in list if any(str(m).__contains__(str(i).replace(' ','')) for m in method)]            # result = subprocess.run(['python', '-c', method_definition], capture_output=True, text=True)
#                 for com in common_keywords:
#                     c_keys.append(com)                                                                     # output = result.stdout if result.stdout else result.stderr
#         print(c_keys)
#         output = {}
#         if len(c_keys) == len(list):
#             output.update({"valid": True,"message": "PYTHON code is valid."})
#         else:
#             output.update({"valid": False,"message": "PYTHON code is Not valid."})
#         score = f'{len(c_keys) }/{len(list) }'
#         if data['File_name']=='Python':
#              output.update({"score": score,
#                     "Status": addCodeToDb(4,data['Page'],input_string,data['Email'],len(c_keys))
#                     })
#         if data['File_name']=='app_py':
#              output.update({"score": score,
#                     "Status": addCodeToDb(5,data['Page'],input_string,data['Email'],len(c_keys))
#                     })
#         if len(c_keys)>0:
#             return HttpResponse(json.dumps(output), content_type='application/json')
#         else:
#             return HttpResponse(json.dumps({"valid": False,"message":"Method not found","score":'0/'+str(len(list))}), content_type='application/json')
        
#     except Exception as e :
#         return HttpResponse(f"An error occurred: {e}", status=500)


# # import numpy as np 
# @api_view(['POST'])   
# def json_for_validation(req ):
#     try:
#         res = json.loads(req.body)
#         page = res['Page']
#         user = InternshipDetails.objects.filter(email=res['Email']).first()
#         if user:
#             print(page+'_Score',user.Python_Score.get(page+'_Score',''))
#             if page.startswith('Database'):
#                 jdata = {"Response":{
#                 "Table1":user.Database_Code.get("Table1",''),
#                 "Table2":user.Database_Code.get("Table2",''),
#                 "Table3":user.Database_Code.get("Table3",''),
#                 "Table4":user.Database_Code.get("Table4",'')
#                 }}
#             else:
#                 jdata = {"Response":{
#                 "HTML":{page :user.HTML_Code.get(page,'')},
#                 "CSS":{page :user.CSS_Code.get(page,'')},
#                 "JS":{page :user.JS_Code.get(page,'')},
#                 "Python":{page :user.Python_Code.get(page,'')  },
#                 "App_py":{page :user.AppPy_Code.get(page,'') }
#                 }}
#         else:
#             user = InternshipDetails.objects.create({
#                 "email":res['Email'],
#                 "Name":'Name',
#                 "Project_name":'Project_name'
#             })
#             jdata = {"Response":{
#                 "HTML":{page :""},
#                 "CSS":{page :""},
#                 "JS":{page :""},
#                 "Python":{page :""},
#                 "App_py":{page :""}
#             }}
#         # print(jdata)
#         data= json.loads(download_blob('Concept/course/'+page+'.json'))
#         data.update(jdata)
#         # print(data)
#         return HttpResponse(json.dumps(data), content_type='application/json') 
#     except Exception as e:
#             return HttpResponse(f"An error occurred: {e}", status=500) 
    
# @api_view(['POST'])
# def download_files(req):
#     try:
#         print('inn')
#         name=json.loads(req.body)['Name']
#         if name=='download_ZIP_file':
#             path='https://storeholder.blob.core.windows.net/tpdata/Concept/course/FlaskSample.zip'
#         else :
#             # path='http://storeholder.blob.core.windows.net/tpdata/Concept/course/'+name+'.json'
#             path='not a valid input...'
#         return HttpResponse(json.dumps({'path':path}), content_type='application/json') 
#     except Exception as e:
#             print(e)
#             return HttpResponse(f"An error occurred: {e}", status=500) 
    
# def addCodeToDb(type,page,code,id,score):
#     try:
#         user, created = InternshipDetails.objects.get_or_create(email=id,defaults={
#             'Student_id':id,
#             "email":id,
#             "Name":'Name',
#             "Project_name":'Project_name' ,
#             "Score":0,
#             "Database_Code":{},
#             "HTML_Code":{},
#             "CSS_Code":{},
#             "JS_Code":{},
#             "Python_Code":{},
#             "AppPy_Code":{},
#             "HTML_Score":{},
#             "CSS_Score":{},
#             "JS_Score":{},
#             "Python_Score":{},
#             "AppPy_Score":{},

#         }
#                                                        )
#         if user:
#             match type:
#                 case 1: 
#                     oldscore =user.HTML_Score.get(page+'_Score',0)
#                     user.HTML_Code[page]=code
#                     user.HTML_Score[page+'_Score']=score*5
                    
#                 case 2:
#                     oldscore =user.CSS_Score.get(page+'_Score',0)
#                     user.CSS_Code[page]=code
#                     user.CSS_Score[page+'_Score']=score*5
#                 case 3:
#                     oldscore =user.JS_Score.get(page+'_Score',0)
#                     user.JS_Code[page]=code
#                     user.JS_Score[page+'_Score']=score*5
#                 case 4:
#                     oldscore =user.Python_Score.get(page+'_Score',0)
#                     user.Python_Code[page]=code
#                     user.Python_Score[page+'_Score']=score*5
#                 case 5:
#                     oldscore =user.AppPy_Score.get(page+'_Score',0)
#                     user.AppPy_Code[page]=code
#                     user.AppPy_Score[page+'_Score']=score*5
#             user.Score=user.Score+int(score*5)-int(oldscore)
#             user.save()
#             return ("done")
#         else:
#             return ('User not found...')
        
#     except Exception as e:
#             print(e)
#             return HttpResponse(f"An error occurred: {e}", status=500) 

# @api_view(['GET'])
# def get_list_json(req,index):
#     try:
#         print('index',index)
#         if index == '1':
#             data= json.loads(download_blob('Concept/course/samplelist.json'))
#         else:
#             data= json.loads(download_blob('Concept/course/InternshipIndexPage.json'))
#         print(data)
#         return HttpResponse(json.dumps(data), content_type='application/json') 
#     except Exception as e:
#             return HttpResponse(f"An error occurred: {e}", status=500)  

   
# @api_view(['POST']) 
# def get_score(req):
#     try:
#         data = json.loads(req.body)
#         email = data.get('Email')
#         pagename=data.get('Page_name')

#         user = InternshipDetails.objects.filter(email=email).first()
#         if user:
#             if str(pagename).startswith('Database_'):
#                 user_data = {
#                     "Page_name":pagename,
#                     "Score":user.Score,
#                     "Table1":user.Database_Code.get("Table1",''),
#                     "Table2":user.Database_Code.get("Table2",''),
#                     "Table3":user.Database_Code.get("Table3",''),
#                     "Table4":user.Database_Code.get("Table4",''),
#                     "Table1_Score":user.Database_Score.get("Table1_Score",''),
#                     "Table2_Score":user.Database_Score.get("Table2_Score",''),
#                     "Table3_Score":user.Database_Score.get("Table3_Score",''),
#                     "Table4_Score":user.Database_Score.get("Table4_Score",''),
#                 }
#             else:
#                 user_data = {
#                     "Page_name":pagename,
#                     "Score":user.Score,
#                     "HTML_Code":user.HTML_Code.get(pagename,''),
#                     "CSS_Code":user.CSS_Code.get(pagename,'') ,
#                     "JS_Code":user.JS_Code.get(pagename,'') ,
#                     "Python_Code":user.Python_Code.get(pagename,'') ,
#                     "App_py_Code":user.AppPy_Code.get(pagename,'') ,
#                     "HTML_Score": user.HTML_Score.get(pagename + '_Score','') ,
#                     "CSS_Score": user.CSS_Score.get(pagename + '_Score','') ,
#                     "JS_Score": user.JS_Score.get(pagename + '_Score','') ,
#                     "Python_Score": user.Python_Score.get(pagename + '_Score','') ,
#                     "App_py_Score": user.AppPy_Score.get(pagename + '_Score','') ,
  
#             }
#             return HttpResponse(json.dumps(user_data), content_type='application/json') 
#         else:
#             return HttpResponse('Error! User does not exist', status=404)
#     except Exception as e:
#             return HttpResponse(f"An error occurred: {e}", status=500)
    
# @api_view(['POST']) 
# def  project_score(req):
#     try:
#         data = json.loads(req.body)
#         email = data.get('Email')

#         user = InternshipDetails.objects.filter(email=email).first()
#         if user:
#             user_data = {
#                 "Score":user.Score,
#                 "HTML":user.HTML_Score,
#                 "CSS":user.CSS_Score,
#                 "JS":user.JS_Score,
#                 "Python":user.Python_Score,
#                 "App_py":user.AppPy_Score,
#                 "Database_Score":user.Database_Score
#             }
#             return HttpResponse(json.dumps(user_data), content_type='application/json') 
#         else:
#             return HttpResponse('Error! User does not exist', status=404)
#     except Exception as e:
#             return HttpResponse(f"An error occurred: {e}", status=500)

# @api_view(['POST'])
# def database_validation(req):
#     try:
#         data = json.loads(req.body)
#         input_string = data.get('data')
#         list = data.get('KEYS')
#         table = str(data.get('Table_name'))
#         d1 = input_string.split('\n')
#         ans = [a.replace(' ','') for key in list for a in d1 if str(a.replace(' ','')).__contains__(key.replace(' ',''))]
#         common_keywords = [i for i in list if any(str(j).__contains__(i.replace(' ','')) for j in ans)]
#         user = InternshipDetails.objects.filter(email=data.get('Email')).first()
#         if user:
#             oldscore=user.Database_Score.get(table+'_Score',0)
#             print(oldscore)
#             user.Database_Code[table]=input_string
#             user.Database_Score[table+'_Score']=len(common_keywords)*5
#             user.Score=user.Score+len(common_keywords)*5-int(oldscore)
#             user.save()
#             output = {}
#             if len(common_keywords) == len(list):
#                 output.update({"valid": True,"message": "Database_setup code is valid."})
#             else:
#                 output.update({"valid": False,"message": "Database_setup code is Not valid."})
#             score = f'{len(common_keywords) }/{len(list) }'
#             output.update({"score": score})
#             return HttpResponse(json.dumps(output), content_type='application/json')

#         else:
#             return HttpResponse('User does not exist', status=404)
#     except Exception as e:
#             return HttpResponse(f"An error occurred: {e}", status=500)
    
# @api_view(['POST'])
# def test_questions(req):
#         if req.method == 'POST':
#             try:
#                 data = req.body
#                 data = json.loads(data)
#                 main=[]
#                 print(data.get("Course"))
#                 json_content = download_list_blob("Question/Internship_Qns/"+str(data.get("Course")).replace(' ',''),'')#question/internship_qns/aptitudetest/
#                 random.shuffle(json_content)
#                 main.append(json_content)
#                 updated_json_content = json.dumps(main)
#                 return HttpResponse(updated_json_content, content_type='application/json') 
#             except Exception as e:
#                 return HttpResponse(f"An error occurred: {e}", status=500)  
#         else:
#             return HttpResponse("Method Not Allowed", status=405)