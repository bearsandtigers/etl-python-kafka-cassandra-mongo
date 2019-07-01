#!/bin/bash
DCP="docker-compose"
$DCP down && \
$DCP up -d && \
sleep 15 && \
$DCP exec cassandra cqlsh -e "CREATE KEYSPACE gdp WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 1 };" && \
$DCP exec cassandra cqlsh -k 'gdp' -e 'CREATE TABLE data(country text PRIMARY KEY, gdp double);'
