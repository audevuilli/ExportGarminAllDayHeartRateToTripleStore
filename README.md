# ExportGarminAllDayHeartRateToTripleStore
This repository contains Linux bash scripts and Python scripts to extract all day heart rate data from [Garmin Connect](https://connect.garmin.com/) and insert those measurements into a triple store.

## Important Note
I started this project to learn Python, RDF and SPARQL, thus please take note of the following:
* The tools in this repository do not currently use the [RDF Data Cube Vocabulary](https://www.w3.org/TR/vocab-data-cube/). This change is planed for a future version.
* The tools also do not currently use any Python RDF functionality, but rather create triples "by hand". This will change in a future version.

## Requirements
* Linux with bash
* Python 3.x (tested with Python 3.7)
  * `pandas`, `json` and `SPARQLWrapper` Python packages
* Garmin Connect account (need to be able to login to [https://connect.garmin.com](https://connect.garmin.com/))
* Watch that syncs all day heart rate data to Garmin Connect
* `FitCSVTool.jar` from the FIT SDK (available from  [https://www.thisisant.com/resources/fit/](https://www.thisisant.com/resources/fit/))
  * Tested with the tool from version `FitSDKRelease_20.88.00.zip`
  * Extract `FitCSVTool.jar` from the ZIP archive and place it into the same directory as the `*.sh` shell scripts
* Java Virtual Machine (JVM) to run the `FitCSVTool.jar`
* A triple store that listens at localhost port 3030.
  * URL for updates: [http://localhost:3030/TDB/update](http://localhost:3030/TDB/update)
  * URL for queries:  [http://localhost:3030/TDB/sparql](http://localhost:3030/TDB/sparql)
  * Tested with Apache Jena Fuseki version 3.10, available from here [https://jena.apache.org/download/](https://jena.apache.org/download/)
    * Launched using: `fuseki-server --loc=/home/<userID>/TDB /TDB`
      * Replace `<userID>` with your Linux userID and make sure `~/TDB` exists

## How to run
* After cloning the GitHub repository or unpacking the archive, you should find the following files in your current working directory:
  * `downloadAndInsertGarminData.sh`
  * `downloadGarminAllDayHeartRate.py`
  * `parseGarminFITCSVtoTurtle.py`
* Now simply execute `downloadAndInsertGarminData.sh` and provide 3 command line arguemnts
  1. Your Garmin Connect user ID  (will not be stored)
  2. Your Garmin Connect password  (will not be stored)
  3. The date you would like to download in the format YYYY-MM-DD
* Example: `./downloadAndInsertGarminData.sh ExampleUserID ExamplePassword 2019-04-21` 
* If all goes well, this is what the command line output will look like:
  ```
  user@vboxub1810:~$ ./downloadAndInsertGarminData.sh userID password 2019-05-10
  Logged in as <Real Name of UserID>
  Download of data from garmin.com succesful.
  Converting FIT to CSV complete.
  Parsing CSV and inserting TTL file to triple store complete.
  Cleanup complete.
  ```


