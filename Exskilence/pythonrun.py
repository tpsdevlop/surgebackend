import datetime
from datetime import date, datetime
import shlex
import subprocess
import time
from django.shortcuts import HttpResponse
import json
from rest_framework.decorators import api_view
from Exskilence.sqlviews import addAttempt

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
    
def coms(data):
    try:
        if str(data).__contains__("import subprocess") or str(data).__contains__("import os") or str(data).__contains__("import sys") or str(data).__contains__("import commands"):
            return "Error: Invalid code "
        # command = shlex.split(f'python -c "{data}"')
        # result = subprocess.run(command, capture_output=True, text=True)
        if str(data).__contains__("reduce"):
            data ="from functools import reduce\n" +data
        result = subprocess.run(['python', '-c', data], capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        return output
    except Exception as e:
            return 'Error:'+ str(e)+'\n'

import io
import sys
# from functools import reduce


def com(data):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    sys.stdout = stdout_capture
    sys.stderr = stderr_capture
    
    local_context = {}
    try:
        if str(data).__contains__("import subprocess") or str(data).__contains__("import os") or str(data).__contains__("import sys") or str(data).__contains__("import commands"):
            return "Error: Invalid code "
        if "reduce" in str(data):
            data = "from functools import reduce\n" + data
        exec(data, local_context)
        output = stdout_capture.getvalue()
        error = stderr_capture.getvalue()
        return output if output else error
    except Exception as e:
        return f'Error========={e}'
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

@api_view(['POST'])
def run_python(request):
    if request.method == 'POST':
        try:
            current_time=datetime.now()
            jsondata = json.loads(request.body)
            code=jsondata.get('Code')
            callfunc=jsondata.get('CallFunction')
            code_data=str(code+'\n'+callfunc).split('\n')
            # print('code_data',code_data)
            result=jsondata.get('Result')
            TestCases=jsondata.get('TestCases')
            Attempt = jsondata.get('Attempt')
            Subject = jsondata.get ('Subject')
            studentId = jsondata.get('studentId')
            Qn = jsondata.get('Qn')
            Day_no = jsondata.get('Day_no')
            bol=True
            main=[]
            i=0
            for tc in TestCases:
                if i==0:
                    tc=tc.get('Testcase')
                    boll=[]
                    for t in tc:
                        for c in code_data:
                            if str(c).replace(' ','').startswith('#') or str(c).replace(' ','').startswith('"""') or str(c).replace(' ','').startswith("'''"):
                                code_data.remove(c)
                                continue
                            if str(c).replace(' ','').startswith(str(t).replace(' ','')):
                                boll.append({t:code_data.index(c),"val": str(c)})
                                break 
                    unique_in_tc = [item for item in tc if item not in {key for d in boll for key in d.keys()}]
                    for u in unique_in_tc:
                        if str(code_data).__contains__(u):
                            boll.append({u:True,"val": str(u)})
                    # print('boll',boll)
                    if len(boll)==len(tc):
                        t={"TestCase"+str(i+1) :"Passed"}
                        main.append(t)
                    else:
                        t={"TestCase"+str(i+1) :"Failed"}
                        bol=False
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
                                                newvalue = str(c)[0:str(c).index(key[0])]+val
                                                code_data[code_data.index(c)]= newvalue
                                                break
                                                
                    newcode=""
                    for c in code_data:
                        newcode=newcode+str(c)+'\n' 
                    # print(newcode)
                    # print(str(com(newcode)))
                    # print(slashNreplace(str(Output)))
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
            addAttempts = addAttempt(studentId,Subject,Qn,Attempt,Day_no)
            Output={'TestCases':main,
                    'Time':[{'Execution_Time':str((datetime.now()-current_time).total_seconds())[0:-2]+" s"}]
                    ,'Attempt':addAttempts
                    }
            return HttpResponse(json.dumps(Output), content_type='application/json')
        except Exception as e:  
            return HttpResponse(f"An error occurred: {e}", status=500)
   