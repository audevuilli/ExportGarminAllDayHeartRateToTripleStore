# ExportGarminAllDayHeartRateToTripleStore
This repository contains Linux bash scripts and Python scripts to extract all day heart rate data from [Garmin Connect](https://connect.garmin.com/) and insert those measurements into a triple store.

## Important Note
I started this project to learn Python, RDF and SPARQL, thus please take note of the following:
* The tools in this repository do not currently use the [RDF Data Cube Vocabulary](https://www.w3.org/TR/vocab-data-cube/). This change is planed for a future version.
* The tools also do not currently use any Python RDF functionality, but rather create triples "by hand". This will change in a future version.