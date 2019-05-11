'''
parseGarminFITCSVtoTurtle -- Parse Garmin CSV file (created from a FIT file) into turtle 
                             and insert into triple store

This tools takes as input a CSV file created from a Garmin FIT file via the ANT+ SDK converter
and parses it into turtle and then inserts it into a triple store.
Tested with CSV files created by "FitCSVTool.jar" from FitSDKRelease_20.88.00.zip available
from "https://www.thisisant.com/resources/fit/".

@author:     Robert Henschel
@copyright:  2019. All rights reserved.
@license:    GNU General Public License, version 2
'''

from datetime import datetime, timedelta
import pandas as pd
import argparse
import json
from SPARQLWrapper import SPARQLWrapper, JSON

# Instantiate the parser
parser = argparse.ArgumentParser()

# Required argument
parser.add_argument('input_csv', type=str,
                    help='Input CSV file.')
args = parser.parse_args()

# Extract file stem 
fileStem = str(args.input_csv)
fileStem = fileStem.split(".",1)[0]

# Garmins beginning of time
startDate = datetime.strptime('1989-12-31 00:00:00', '%Y-%m-%d %H:%M:%S')

# Determine local time at file creation
# Read CSV file into Pandas data frame
df = pd.read_csv(str(args.input_csv))

# Restrict data frame to values matching "Data" "Field 2"
df = df[df.Type == "Data"]
df = df[df["Field 2"] == "local_timestamp"]
# There are fit files with more than one line of "DATA"-"local_timestamp", for whatever reason...
# We pick the first one.
localTimestamp = int(df["Value 2"].iloc[0])
localStartTime = startDate + timedelta(seconds=localTimestamp)

# Get time stamp for begin of file
# Read CSV file into Pandas data frame
df = pd.read_csv(str(args.input_csv))

# Restrict data frame to values matching "Data" "Message"
df = df[df.Type == "Data"]
df = df[df["Message"] == "monitoring_info"]
utcTimestamp = int(df["Value 1"].iloc[0])
localTimeDif = utcTimestamp - localTimestamp 
utcStartTime = startDate + timedelta(seconds=utcTimestamp)

# Now parse the actual heart rate data
# Read CSV file into Pandas data frame
df = pd.read_csv(str(args.input_csv))

# Restrict data frame to values matching "Data" "heart_rate"
df = df[df.Type == "Data"]
df = df[df["Field 2"] == "heart_rate"]

#parse into triples and write out
with open(fileStem+".ttl", 'w') as the_file:
    the_file.write('PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> \n\n')
    the_file.write('INSERT DATA {\n\n')
    
    for index, rowdf in df.iterrows():
        # formula for this is from here: https://www.thisisant.com/forum/viewthread/6374
        tempTime = (localTimestamp + (( int(rowdf['Value 1']) - ( localTimestamp & 0xFFFF ) ) & 0xFFFF))-localTimeDif
        rowTime = startDate + timedelta(seconds=tempTime)
        rowDate = str(rowTime).split(" ",1)[0]
        rowTime = str(rowTime).split(" ",1)[1]
        rowValue = rowdf['Value 2']
        if rowValue != 0:
            the_file.write('<http://example.org/#measurement'+rowDate+"T"+rowTime+'FR235> <http://example.org/hasType> <http://example.org/Type/heartRateMeasurement> ;\n')
            the_file.write('    <http://example.org/hasValue> '+str(int(rowValue))+' ;\n')
            the_file.write('    <http://example.org/device> <http://example.org/#GarminFR235> ;\n')
            the_file.write('    <http://example.org/measuredOn> "'+rowDate+"T"+rowTime+'"^^xsd:dateTime .\n')
    the_file.write('}\n\n')
    the_file.close()

# read in turtle file and insert into triple store
with open(fileStem+".ttl", 'r') as file:
    data = file.read()
file.close()
sparql = SPARQLWrapper("http://localhost:3030/TDB/update")
sparql.setQuery(data)
sparql.method = 'POST'
sparql.setReturnFormat(JSON)
results = sparql.query()

    