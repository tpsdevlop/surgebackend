    
from datetime import datetime
from django.db.models import QuerySet
def filterQuery(user,key,value):
     if isinstance(user, QuerySet):
        filtered_records = []
        for record in user:
                jdata ={}
                for i in record.__dict__.keys():
                    if i == '_state':
                        continue
                    jdata.update({i:record.__dict__.get(i)})
                if jdata.get(key) == value:
                    filtered_records.append(jdata)
        return  (filtered_records)

def filterQueryandv1v2(user,key,value,key1,value1):
     if isinstance(user, QuerySet):
        filtered_records = []
        for record in user:
                jdata ={}
                for i in record.__dict__.keys():
                    if i == '_state':
                        continue
                    jdata.update({i:record.__dict__.get(i)})
                if jdata.get(key) == value and jdata.get(key1) == value1 or jdata.get(key) == value1 and jdata.get(key1) == value:
                    filtered_records.append(jdata)
        return  (filtered_records)
     
def filterQueryOrderby(user,Sortkey ,order):
     if isinstance(user, QuerySet):
        filtered_records = []
        for record in user:
                jdata ={}
                for i in record.__dict__.keys():
                    if i == '_state':
                        continue
                    jdata.update({i:record.__dict__.get(i)})
                filtered_records.append(jdata)
        filtered_records = sorted(filtered_records, key=lambda k: k[Sortkey] , reverse = order)
        return  (filtered_records)
     
def filterQueryTodict(user ):
     
    if isinstance(user, QuerySet):
        filtered_records = []
        for record in user:
                jdata ={}
                for i in record.__dict__.keys():
                    if i == '_state':
                        continue
                    jdata.update({i:record.__dict__.get(i)})
                
                filtered_records.append(jdata)
        return  (filtered_records)
    
def  filterQueryfromdict(user,key,value):
     filtered_records = []
     for i in user:
        if i.get(key) == value:
           filtered_records.append(i)
     return  (filtered_records)

def filterQueryMaxValueScore (all ,course):
     if isinstance(all, QuerySet):
        maxscore = -1
      
        for record in all:
                for i in record.__dict__.keys():
                    if i != 'Score_lists':
                        continue
                    if i == 'Score_lists':
                        list = record.__dict__.get(i)
                        if course == "HTMLCSS":
                            score = float(str(list.get('HTMLScore',0)).split('/')[0]) + float(str(list.get('CSSScore',0)).split('/')[0])                               
                            if maxscore < score:
                                maxscore = score
                        else:
                            if maxscore < float(str(list.get(str(course)+'Score',0)).split('/')[0]):
                                 maxscore = float(str(list.get(str(course)+'Score',0)).split('/')[0])
        print('maxscore',maxscore)
        return maxscore
     
def filterQueryMaxdelay (all , course):
     if isinstance(all, QuerySet):
        maxdate = None

        for record in all:
                for i in record.__dict__.keys():
                    if i != 'End_Course':
                        continue
                    if i == 'End_Course':
                         list = record.__dict__.get(i)
                         if list.get(course) is not None:

                                   if maxdate is None:
                                        maxdate = datetime.strptime(str(list.get(course)).split('.')[0], "%Y-%m-%d %H:%M:%S")
                                   if maxdate < datetime.strptime(str(list.get(course)).split('.')[0], "%Y-%m-%d %H:%M:%S"):
                                        maxdate = datetime.strptime(str(list.get(course)).split('.')[0], "%Y-%m-%d %H:%M:%S")
                              
        print('maxdate',maxdate)
        return maxdate