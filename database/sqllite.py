import sqlite3
import csv

# Define the SQLite database file
db_file = 'WfMar2025_1.db'

# Define the CSV file
change_data = 'Change.csv'
Incident_data = 'Incident.csv'
ErrorLog_data = 'ErrorLog.csv'
# Connect to SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create a table (modify the schema as needed)
cursor.execute('''
CREATE TABLE IF NOT EXISTS change (               
ApplicationID TEXT,
               	ApplicationName TEXT,	ChangeNumber TEXT,	ScheduledDate DATETIME,	Description TEXT,	ImpactedApplications TEXT

               );''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS incident (       
               ApplicationID TEXT,
               	ApplicationName TEXT,	
               IncidentNumber TEXT,
               Severity TEXT,
               Description TEXT,
               IncidentTime DATETIME,
               ErrorMessage TEXT
        
);''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS errorlog (
    DateOfError DATE,
    TimeOfError TIMESTAMP,
    ApplicationId TEXT,
    ApplicationName TEXT,
               ErrorSeverity TEXT,
               ErrorMessage TEXT
)
''')

# Open the CSV file and insert records
with open(ErrorLog_data, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row if the CSV has one
    for row in reader:
        cursor.execute('INSERT INTO errorlog (DateOfError, TimeOfError, ApplicationId, ApplicationName,ErrorSeverity,ErrorMessage) VALUES (?, ?, ?, ?,?,?)', row)

with open(change_data, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row if the CSV has one
    for row in reader:
        cursor.execute('INSERT INTO change (ApplicationID,ApplicationName	,ChangeNumber	,ScheduledDate	,Description	,ImpactedApplications) VALUES (?, ?, ?, ?,?,?)', row)


with open(Incident_data, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row if the CSV has one
    for row in reader:
        cursor.execute('INSERT INTO incident (ApplicationID	,ApplicationName	,IncidentNumber	,Severity	,Description	,IncidentTime,ErrorMessage) VALUES (?, ?, ?, ?,?,?,?)', row)



# Commit changes and close the connection
conn.commit()



conn.close()

print("Records inserted successfully.")

