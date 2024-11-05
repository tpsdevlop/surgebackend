import datetime
from datetime import date, datetime
import shlex
import subprocess
import time
from django.shortcuts import HttpResponse
import json
from rest_framework.decorators import api_view

@api_view(['POST'])
def execute_python(request):
    if request.method == 'POST':
         data = request.body
         jsondata = json.loads(data)
         code =jsondata.get('Code')
         try:
             output=com(code)
             out={"output" : output[0:-1]}
             return HttpResponse(json.dumps(out), content_type='application/json') 
         except Exception as e:
            return HttpResponse(json.dumps({'Error': str(e)}), status=400)
    else:
        return HttpResponse({'Error': 'Only POST requests are allowed'}, status=405)
    
def com(data):
    try:
        if str(data).__contains__("import subprocess") or str(data).__contains__("import os") or str(data).__contains__("import sys") or str(data).__contains__("import commands"):
            return "Error: Invalid code "
        # command = shlex.split(f'python -c "{data}"')
        # result = subprocess.run(command, capture_output=True, text=True)
        result = subprocess.run(['python', '-c', data], capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        return output
    except Exception as e:
            return 'Error:'+ str(e)+'\n'

@api_view(['POST'])
def run_python(request):
    if request.method == 'POST':
        try:
            current_time=datetime.now()
            jsondata = json.loads(request.body)
            code=jsondata.get('Code')
            callfunc=jsondata.get('CallFunction')
            code_data=str(code+'\n'+callfunc).split('\n')
            result=jsondata.get('Result')
            TestCases=jsondata.get('TestCases')
            bol=True
            main=[]
            i=0
            for tc in TestCases:
                if i==0:
                    tc=tc.get('Testcase')
                    boll=[]
                    for t in tc:
                        for c in code_data:
                            if str(c).replace(' ','').startswith(str(t).replace(' ','')):
                                boll.append({t:code_data.index(c),"val": str(c)})
                                break 
                    unique_in_tc = [item for item in tc if item not in {key for d in boll for key in d.keys()}]
                    for u in unique_in_tc:
                        if str(code).__contains__(u):
                            boll.append({u:True,"val": str(u)})
                    # print('boll',boll)
                    if len(boll)==len(tc):
                        t={"TestCase"+str(i+1) :"Passed"}
                        main.append(t)
                    else:
                        t={"TestCase"+str(i+1) :"Failed"}
                        main.append(t)
                if i>0:
                    tc=tc['Testcase']
                    Values=tc['Value']
                    Output=tc['Output']
                    def slashNreplace(string):
                        if string=='':
                            return string
                        if string[-1]=='\n':
                            string=slashNreplace(string[:-1])
                        return string
                    for val in Values:
                        for b in boll :
                            key=str(b.keys()).split("'")[1]
                            if str(val).replace(' ','').split('=')[0] in str(b.keys()): 
                                newvalue=str(b['val'])[0:str(b['val']).index(key[0])]+val
                                if str(val).startswith(key):
                                    if str(val).replace(' ','').split('=')[0]==code_data[b[key]].replace(' ','').split('=')[0]:
                                        code_data[b[key]]=newvalue
                                    else:
                                        for c in code_data:
                                            if str(c).replace(' ','').split('=')[0]==(str(val).replace(' ','').split('=')[0]):
                                                # print(val,c ,code_data.index(c))
                                                code_data[code_data.index(c)]=newvalue
                                                break
                                                
                    newcode=""
                    for c in code_data:
                        newcode=newcode+str(c)+'\n' 
                    # print(newcode)
                    # print(str(com(newcode)))
                    if str(slashNreplace(str(Output)).lower().replace(' ',''))==slashNreplace(str(com(newcode)).lower().replace(' ','')):
                        t={"TestCase"+str(i+1) :"Passed"}
                    else:
                        t={"TestCase"+str(i+1) :"Failed"}
                        bol=False
                    main.append(t)
                i=i+1
            if bol:
                if slashNreplace(str(result).lower().replace(' ',''))==slashNreplace(str(com(code+'\n'+callfunc)).lower().replace(' ','')) :
                    data={"Result" :"True"}
                else:
                    data=   {"Result" :"False"}
            else:
                data={"Result" :"False"}
                bol=False
            main.append(data)
            Output={'TestCases':main,'Time':[{'Execution_Time':str((datetime.now()-current_time).total_seconds())[0:-2]+" s"}]}
            return HttpResponse(json.dumps(Output), content_type='application/json')
        except Exception as e:  
            return HttpResponse(f"An error occurred: {e}", status=500)
   