#THis is currently running as a streamlit app for testing purposes. This needs to be cleaned and integrated with frontend


from dotenv import load_dotenv
load_dotenv() ## load all the environemnt variables



import streamlit as st
import os
import sqlite3

from google import genai
from google.genai import types
## Configure Genai Key


from dotenv import load_dotenv
load_dotenv() ## load all the environemnt variables

import streamlit as st
import os
import sqlite3

from google import genai
from google.genai import types
import sys
## Configure Genai Key

GEMINI_API_KEY=os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

print('Client initialized')
## Function To Load Google Gemini Model and provide queries as response

def get_gemini_response(question,prompt):
    
    response = client.models.generate_content(
    model='gemini-2.0-flash',
    config=types.GenerateContentConfig(
        system_instruction=prompt[0]),
    contents=question
)
    #client.models.generate_content()
    #model=genai.GenerativeModel('gemini-2.0-flash')
    #response=model.generate_content([prompt[0],question])
    return response.text

## Fucntion To retrieve query from the database

def read_sql_query(sql,db):
    conn=sqlite3.connect(db)
    cur=conn.cursor()
    cur.execute(sql)
    rows=cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows

## Define Your Prompt
prompt=[
    """
    You are a Business Analyst specializing in business data analysys. you are asked to perform data analysis on application data which contains
    incident data, change data and system error data. Your goal is to answer queries by application teams, SRE, leadership on questions related to the cause of faults,
    identify if change requests caused any errors, most frequest errors, common incidents. 
    You are also an expert in converting English questions to SQL query on SQLite database!
    The SQL database has the tables incident, change and errorlog. 
    incident table has the following columns - ApplicationID	,ApplicationName	,IncidentNumber	,Severity	,Description	,IncidentTime,ErrorMessage
    change table has the following columns - ApplicationID,ApplicationName	,ChangeNumber	,ScheduledDate	,Description	,ImpactedApplications
    errorlog table has the following columns - DateOfError, TimeOfError, ApplicationId, ApplicationName,ErrorSeverity,ErrorMessage
    You will be asked questions like - How many incidents are present in the database?, Show me critical incidents, Show me incidents for application X,
    Show me errors for application X, Show me errors for application X on date Y, Show me errors for application X on date Y with severity Z
    Example 1 - How many incidents are critical?, 
    the SQL command will be something like this SELECT COUNT(*) FROM incident where Severity="Critical";
    Example 2 - How many incidents were raised yesterday;
    the SQL command will be something like this SELECT COUNT(*) FROM incident where IncidentTime=DATE('now', '-1 day');
    \nExample 2 - Show me number of change reqeusts for which there is an incident logged, 
    the SQL command will be something like this SELECT COUNT(*) FROM change WHERE ApplicationID IN (SELECT ApplicationID FROM incident); 
    also the sql code should not have ``` in beginning or end and sql word in output

    """


]
# Allow reading from standard input for testing purposes

print("Enter your question:")
question = input().strip()
response = get_gemini_response(question, prompt)
#print("Generated SQL Query:", response)
response_text = response
#print(response_text)
response = read_sql_query(response, "WfMar2025_1.db")
#print("The Response is:")

for row in response:
        response_text += str(row) + '\n'

#print(f'res txt is {response_text}')

prompt1=[
    """
    You are an expert in analysing output of SQL queries. You are asked to analyse the output of a SQL query on the SQLite database and provide insights using the data.
    The SQL database has the tables incident, change and errorlog. Summarize the output of the sql in context with the question and provide meaningful answers. 
    show only analysis on the actal query output and tell query does not return data if it does not return any data.

    """


]

response1 = get_gemini_response(response_text, prompt1)
print(response1)
