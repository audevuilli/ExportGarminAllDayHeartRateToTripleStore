#!/usr/bin/env bash

# Test for command line parameters, output help in case the number of parameters does not match
if [ "$#" -ne 3 ]; then
    echo "This is a helper script that executes a workflow to:"
    echo "  - Download data from Garmin Connect,"
    echo "  - Convert the data from FIT to CSV,"
    echo "  - Extract heart rate data from the CSV file and"
    echo "  - Insert the data into a triple store."
    echo " "
    echo "3 required parameters: <Garmin.com userID> <Garmin.com password> <date>"
    echo "Example: ./downloadAndInsertGarminData.sh ExampleUserID ExamplePassword 2019-04-22"
    echo ""
    exit 1
fi

user=$1
password=$2
date=$3

#Test if all required tools exist
if [ ! -f ./downloadGarminAllDayHeartRate.py ]; then
    echo " "
    echo "ERROR: ./downloadGarminAllDayHeartRate.py not found!"
    exit 1
fi
if [ ! -f ./FitCSVTool.jar ]; then
    echo " "
    echo "ERROR: ./FitCSVTool.jar not found!"
    exit 1
fi
if [ ! -f ./parseGarminFITCSVtoTurtle.py ]; then
    echo " "
    echo "ERROR: ./parseGarminFITCSVtoTurtle.py not found!"
    exit 1
fi

# Test if ZIP file already exists
if [ -f ./$date.zip ]; then
    echo " "
    echo "ERROR: $date.zip already exists!"
    exit 1
fi

# Download ZIP file from garmin.com
python ./downloadGarminAllDayHeartRate.py $user $password $date

# Test if download was succesful and file exists
if [ ! -f ./$date.zip ]; then
    echo " "
    echo "ERROR: Download of data from garmin.com failed!"
    exit 1
fi
echo "Download of data from garmin.com succesful."

#Make folder for this date, and copy ZIP archive and tools into the folder
mkdir $date
cp $date.zip $date/
cp FitCSVTool.jar $date/
cp parseGarminFITCSVtoTurtle.py $date/
cd $date

#Unzip the archive
unzip -q $date

#Convert *.fit to CSV using java program from ANT+ SDK
for f in *.fit; do FILENAME=${f%%.*};  java -jar FitCSVTool.jar -b ${FILENAME}.fit ${FILENAME}.csv >>/dev/null;  done;
echo "Converting FIT to CSV complete."

#Extract heart rate data from *.csv files and insert into triple store
for f in *.csv; do FILENAME=${f%%.*};  python ./parseGarminFITCSVtoTurtle.py ${FILENAME}.csv ;  done;
echo "Parsing CSV and inserting TTL file to triple store complete."

#clean up
rm FitCSVTool.jar
rm parseGarminFITCSVtoTurtle.py
rm $date.zip
cd ..
echo "Cleanup complete."