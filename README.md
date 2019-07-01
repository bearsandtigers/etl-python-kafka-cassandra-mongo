# TEST TASK
Imitates some simple ETL pipeline.
`kafker.py --produce` loads data from source-data CSV files into Kafka.
`kafker.py --consume` gets data from Kafka and puts GDP data into Cassandra and population data into MongoDB.
Finally, `result.py` gathers data from both Cassandara and Mongo, calculates GDP per capit and places it into output CSV file inside result directory.

