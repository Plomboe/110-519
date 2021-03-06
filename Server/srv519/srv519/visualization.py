# Load in clean data 
import pandas as pd 
import datetime
from dateutil.relativedelta import relativedelta
import bisect 
import json 
import copy
import numpy as np 
from scipy import stats

MONTHS = {1: 'Jan', 2: 'Feb', 3: 'Mar',
          4: 'Apr', 5: 'May', 6: 'Jun',
          7: 'Jul', 8: 'Aug', 9: 'Sep',
          10: 'Oct', 11: 'Nov', 12: 'Dec'}

def getMonthYear(date, axis):
    date1 = pd.to_datetime(date)
    axis2 = copy.copy(axis)
    bisect.insort(axis2, date1)
    return(axis[axis2.index(date1) - 1])

def user_graph(id, data):
    df = data.copy(deep = True) 
    
    # Axis: current month and go back 12 months -> find highest month 
    df['Event Date'] = pd.to_datetime(df['Event Date'], format = '%m/%d/%Y')  
    most_recent_event = max(df['Event Date'])
    earliest_event = most_recent_event + relativedelta(months =-12)  
    axis = [] 
    i = earliest_event
    delta = relativedelta(months=1)
    while i <= most_recent_event: 
        axis.append(i) 
        i += delta
    
    # Total Event Attendees
    df['Interval'] = df.apply(lambda x: getMonthYear(x['Event Date'], axis), axis = 1)
    df_all = df[(df['Attended'] == 1)].copy(deep = True) 
    df_all = df_all.groupby('Interval')['Event Name'].count() 
    df_all.columns = ['Attendees']

    # Total Events User Attended
    df_attend = df[(df['MemberNum'] == id) & (df['Attended'] == 1)].copy(deep = True) 
    df_attend = df_attend.groupby('Interval')['Event Name'].count() 
    df_attend.columns = ['Events Attended']

    # Total Events User Registered
    df_reg = df[(df['MemberNum'] == id)].copy(deep = True) 
    df_reg = df_reg.groupby('Interval')['Event Name'].count() 
    df_reg.columns = ['Events Registered']
    
    # What quantile does this user belong in? 
    df_other = data.copy(deep = True)
    df_other = df_other.groupby('MemberNum')['Event Name'].count()
    qq_list = df_other.values.flatten()
    percentile = stats.percentileofscore(qq_list, sum(df_attend))
    
    return (axis, df_all, df_attend, df_reg, percentile)    
    
##################

def program_graph(eventid, data): 
    df = data.copy(deep = True) 
    
    # Axis: current month and go back 12 months -> find highest month 
    df['Event Date'] = pd.to_datetime(df['Event Date'], format = '%m/%d/%Y')  
    most_recent_event = max(df['Event Date'])
    earliest_event = most_recent_event + relativedelta(months =-12)  
    axis = [] 
    i = earliest_event
    delta = relativedelta(months=1)
    while i <= most_recent_event: 
        axis.append(i) 
        i += delta
    
    # All events 
    df['Interval'] = df.apply(lambda x: getMonthYear(x['Event Date'], axis), axis = 1)
    df_all = df[(df['Attended'] == 1)].copy(deep = True) 
    df_all = df_all.groupby('Interval')['Event Name'].count() 
    df_all.columns = ['Attendees']
        
    # Total Event Registered
    df_reg = df[(df['EventID'] == eventid)].copy(deep = True) 
    df_reg = df_reg.groupby('Interval')['Event Name'].count() 
    df_reg.columns = ['Number Registered']
    
    # Total Event Attended
    df_attend = df[(df['EventID'] == eventid) & (df['Attended'] == 1)].copy(deep = True) 
    df_attend = df_attend.groupby('Interval')['Event Name'].count() 
    df_attend.columns = ['Number Attended']
       
    df_total = pd.DataFrame({'all': df_all, 'reg': df_reg, 'attend':df_attend}).fillna(0.0)

    # What quantile does this user belong in? 
    #df_other = data.copy(deep = True)
    #df_other = df_other.groupby('EventID')['Event Name'].count()
    #qq_list = df_other.values.flatten()
    #percentile = stats.percentileofscore(qq_list, sum(df_attend))
    #return (axis, df_all, df_attend, df_reg, percentile) 
    return df_total
        
def program_relationship_graph(id1,id2,data): 
    # Find the number of people who attended both events 
    # Find the number of people who registered for both events 
    R1 = data.ix[(data['EventID'] == id1)]['MemberNum'] 
    R2 = data.ix[(data['EventID'] == id2)]['MemberNum']
    registered = len(R2[R2.isin(R1)])
    # Find the number of people who attended both events 
    A1 = data.ix[(data['EventID'] == id1) & (data['Attended'] == 1)]['MemberNum'] 
    A2 = data.ix[(data['EventID'] == id2) & (data['Attended'] == 1)]['MemberNum']
    attended = len(A2[A2.isin(A1)])
    return (attended, registered) 
    
