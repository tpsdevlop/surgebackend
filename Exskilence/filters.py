    
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