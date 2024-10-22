from django.http import HttpResponse
from Exskilencebackend160924.settings import *
from rest_framework.decorators import api_view
from datetime import date, datetime, time, timedelta
from Exskilence.models import *
from Exskilence.filters import *
from Exskilence.ErrorLog import ErrorLog
# from Exskilence.views import rankings
def updateRanks(COURSE):
    try:
        std_days_all = StudentDetails_Days_Questions.objects.all()
        std_all = StudentDetails.objects.all()
        ranks = rankings(filterQueryTodict(std_all))
        new_ranks = []
        if COURSE == "HTMLCSS" or COURSE == "HTML" or COURSE == "CSS":
            COURSE = "HTMLCSS"
        print('COURSE',COURSE)
        STARTTIMES = {
            'HTMLCSS':{
                'Start':datetime.strptime('2024-10-03 00:00:00', "%Y-%m-%d %H:%M:%S"),
                'End':datetime.strptime('2024-10-12 23:59:59', "%Y-%m-%d %H:%M:%S")
            },
            'Java_Script':{
                'Start':datetime.strptime('2024-10-14 00:00:00', "%Y-%m-%d %H:%M:%S"),
                'End':datetime.strptime('2024-11-02 23:59:59', "%Y-%m-%d %H:%M:%S")
            },
            'SQL':{
                'Start':datetime.strptime('2024-11-04 00:00:00', "%Y-%m-%d %H:%M:%S"),
                'End':datetime.strptime('2024-11-13 23:59:59', "%Y-%m-%d %H:%M:%S")
            },
            'Python':{
                'Start':datetime.strptime('2024-11-15 00:00:00', "%Y-%m-%d %H:%M:%S"),
                'End':datetime.strptime('2024-11-24 23:59:59', "%Y-%m-%d %H:%M:%S")
            }
        }
        # for i in std_days_all:
        #     for j in ranks:
        #         if i.Student_id == j['StudentId']:
        #             if i.__dict__.get('End_Course') is None:
        #                 i.End_Course ={
        #                     # COURSE:j['LastTime']
        #                    COURSE: datetime.strptime(str(j['LastTime']).split('.')[0], "%Y-%m-%d %H:%M:%S") 
        #                 }
        #             else:
        #                 i.End_Course.update({ COURSE: datetime.strptime(str(j['LastTime']).split('.')[0], "%Y-%m-%d %H:%M:%S") })
        #             i.save()
        #         else:
        #             if i.__dict__.get('End_Course') is None:
        #                 i.End_Course ={
        #                     COURSE:STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS' and COURSE != 'HTML' and COURSE != 'CSS' and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End')
        #                 }
        #             else:
        #                 i.End_Course.update({
        #                 COURSE:datetime.strptime(str(i.Start_Course.get(COURSE,None)).split('.')[0], "%Y-%m-%d %H:%M:%S") if i.Start_Course.get(COURSE,None) is not None else STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS'  and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End')
        #                     })
        #             i.save()
        
        
        maxscore = filterQueryMaxValueScore(std_days_all,COURSE)
        maxdelay1 = filterQueryMaxdelay(std_days_all,COURSE)
        print(COURSE)
        if COURSE == 'HTMLCSS' or COURSE == 'HTML' or COURSE == 'CSS' :
            COURSE = 'HTMLCSS'
            maxdelay = (STARTTIMES.get(COURSE).get('End')-datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")).total_seconds()/60*60
            # maxdelay = (datetime.strptime(str(maxdelay).split('.')[0], "%Y-%m-%d %H:%M:%S")-STARTTIMES.get(COURSE).get('End')).total_seconds()/60*60
        elif COURSE == 'Java_Script' :
            maxdelay = (STARTTIMES.get(COURSE).get('End')-datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")).total_seconds()/60*60
            # maxdelay = (datetime.strptime(str(maxdelay).split('.')[0], "%Y-%m-%d %H:%M:%S")-STARTTIMES.get(COURSE).get('End')).total_seconds()/60*60
        else:
            maxdelay =  (STARTTIMES.get(COURSE).get('Start')-datetime.strptime(str(maxdelay1).split('.')[0], "%Y-%m-%d %H:%M:%S")).total_seconds()/60*60
            # maxdelay = (datetime.strptime(str(maxdelay).split('.')[0], "%Y-%m-%d %H:%M:%S")-STARTTIMES.get(COURSE).get('Start')).total_seconds()/60*60

        for user in std_days_all:
            if user.Qns_lists.get(COURSE) is None:
                user.Qns_lists.update({COURSE:[]})
                user.Ans_lists.update({COURSE:[]})
                user.Score_lists.update({COURSE:0})
            if len(user.Qns_lists.get(COURSE,[]) ) == len(user.Ans_lists.get(COURSE if COURSE != 'HTMLCSS' else 'HTML',[]) ) and len(user.Qns_lists.get(COURSE,[]) )  > 0:
                if COURSE == 'HTMLCSS' or COURSE == 'HTML' or COURSE == 'CSS':
                    userScore = (float(str(user.Score_lists.get("HTMLScore",0)).split('/')[0])+float(str(user.Score_lists.get("CSSScore",0)).split('/')[0]))
                else:
                    userScore = float(str(user.Score_lists.get(str(COURSE)+'Score',0)).split('/')[0])
                # print(user.Student_id , user.End_Course.get(COURSE))
                userDelay = user.End_Course.get(COURSE) if user.End_Course.get(COURSE) is not None else user.Start_Course.get(COURSE,STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS' and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End'))
                # std_prf = filterQuery(std_all,'StudentId',user.Student_id)
                # if std_prf is not None and len(std_prf) > 0:
                #     if COURSE == 'HTMLCSS' or COURSE == 'HTML' or COURSE == 'CSS' or COURSE == 'Java_Script':
                #         startdate = std_prf[0].get('Course_Time').get(COURSE,STARTTIMES.get(COURSE)).get('End')
                #     else:
                #         startdate = std_prf[0].get('Course_Time').get(COURSE,STARTTIMES.get(COURSE)).get('Start')
                # else:
                #     if COURSE == 'HTMLCSS' or COURSE == 'HTML' or COURSE == 'CSS' or COURSE == 'Java_Script':
                #         startdate = STARTTIMES.get(COURSE).get('End')
                #     else:
                #         startdate = STARTTIMES.get(COURSE).get('Start')
                startdate = STARTTIMES.get(COURSE).get('Start') if COURSE != 'HTMLCSS' and COURSE != 'Java_Script' else STARTTIMES.get(COURSE).get('End')
                delay =(startdate-datetime.strptime(str(userDelay).split('.')[0], "%Y-%m-%d %H:%M:%S")).total_seconds()/60*60
                # delay =(datetime.strptime(str(userDelay).split('.')[0], "%Y-%m-%d %H:%M:%S")-startdate).total_seconds()/60*60
                # print('delay',delay,"Course",COURSE,'maxdelay',maxdelay ,'userdelay',userDelay,'startdate',startdate)
                Scorevalue = (0.8 * (userScore/maxscore))-( (0.2) * (delay/maxdelay))
                new_ranks.append({
                    'StudentId':user.Student_id,
                    'Score':Scorevalue,
                    'Course':COURSE,
                    'DateTime':userDelay,
                    'userScore':userScore,
                    'delay':(datetime.strptime(str(userDelay).split('.')[0], "%Y-%m-%d %H:%M:%S")-startdate).days
                })

        new_ranks = sorted(new_ranks, key=lambda x: x['Score'], reverse=True)
        for i in new_ranks:
            i['Rank'] = new_ranks.index(i)+1
            print(i.get('Rank'),'\t',i.get('StudentId'),'\t',i.get('Score'),'\t',i.get('Course'),'\t',i.get('DateTime'),'\t',i.get('userScore'),'\t',i.get('delay'))
         
        oldranks = Rankings.objects.filter(Course = COURSE).order_by('-Rank')
        new_rankings = []
        if  len(oldranks) > 0:
            for i in oldranks:
                i.delete()
        for i in new_ranks:
            r = Rankings.objects.create(
                StudentId = i.get('StudentId'),
                Rank = i.get('Rank'),
                Course = i.get('Course'),
                Score = i.get('Score'),
                DateTime = i.get('DateTime'),
                Delay = (i.get('delay')),
            ) 
            if r is not None:
                new_rankings.append(  r)
        return new_rankings
    except Exception as e:
        print(e) 
        return  'An error occurred  :'+str(e) 
    

def getRankings(COURSE,SID):
    try:
        userRank = Rankings.objects.filter(Course = COURSE,StudentId = SID).first()
        if userRank is not None:
            return userRank.Rank
        else:
            return 'N/A'
    except Exception as e:
        print(e)
def UpdateTotalRanks ():
    try:
        userRank = Rankings.objects.filter( Course = 'TOTAL') 
        maxDelay = filterQueryMaxdelay(QuestionDetails_Days.objects.all(),'TOTAL')
        print(maxDelay)
        maxvalue = filterQueryMaxValueScore(QuestionDetails_Days.objects.all(),'TOTAL')
        print(maxvalue)
        maxDelay = (datetime.strptime('2024-10-12 23:59:59', "%Y-%m-%d %H:%M:%S")-datetime.strptime(str(maxDelay).split('.')[0], "%Y-%m-%d %H:%M:%S")).total_seconds()/60*60
        # if userRank is not None:
        #     for i in userRank:
        #         i.delete()
    except Exception as e:
        print(e)
def totalRanks (SID):
    try:
        userRank = Rankings.objects.filter(StudentId = SID,Course = 'TOTAL').first()
        if userRank is not None:
            return userRank.Rank
        else:
            return 'N/A'
    except Exception as e:
        print(e)
  
def rankings(allusers):
    try:
        allmainQns = QuestionDetails_Days.objects.all()
        ranks = allusers
        if ranks is None:
            HttpResponse('No data found')
        out ={}
        noDAta = []
        for i in ranks:
         if str(i.get('StudentId'))[2:].startswith("ADMI") or str(i.get('StudentId'))[2:].startswith("TRAI") or str(i.get('StudentId'))[2:].startswith("TEST"):
            continue
         user = filterQuery(allmainQns, 'Student_id',  i.get('StudentId'))
         if user is None:
            noDAta.append(i.get('StudentId'))
            continue
         HTML = filterQueryfromdict(user, 'Subject',  'HTML')
         CSS = filterQueryfromdict(user, 'Subject',  'CSS')
         if HTML is None  or len(HTML) == 0  :
            noDAta.append(i.get('StudentId'))
            print(i.get('StudentId'))
            continue
         HTMLCSSSCORE =0
         HTMLLASTTIME = HTML[0].get('DateAndTime')
         for i1 in HTML:
            # print(i)
            HTMLCSSSCORE += i1.get('Score')
            if i1.get('DateAndTime') > HTMLLASTTIME:
                HTMLLASTTIME = i1.get('DateAndTime')
         for i2 in CSS:
            HTMLCSSSCORE += i2.get('Score')
            if i2.get('DateAndTime') > HTMLLASTTIME:
                HTMLLASTTIME = i2.get('DateAndTime')
         
         out.update({i.get('StudentId'): {
            "HTMLCSS":   HTMLCSSSCORE,
            'HTML_last_Question':   HTMLLASTTIME,

        }
    })
        ranks = sorted(    out.items(),     key=lambda x: (-x[1]['HTMLCSS'], x[1]['HTML_last_Question']))  
        res = []
        for i in ranks:
                res.append({'Rank':ranks.index(i)+1,"StudentId":i [0],"Total":i[1]['HTMLCSS'], "LastTime":i[1]['HTML_last_Question']})
                print({'Rank':ranks.index(i)+1,"StudentId":i [0], "LastTime":i[1]['HTML_last_Question'],"Total":i[1]['HTMLCSS']})
        return res
    except Exception as e:
        print(e)
        return  'An error occurred'+str(e)
    