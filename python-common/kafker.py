#!/usr/bin/env python3 

import csv
import sys
import argparse
import pymongo
from json import dumps, loads
from cassandra.cluster import Cluster
from kafka import KafkaProducer, KafkaConsumer

parser = argparse.ArgumentParser(description='Producer/'
                                 'Consumer for Kafka',
                                 usage='Type "--produce" or "--consume"',
                                 add_help=False)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--produce', action='store_true')
group.add_argument('--consume', action='store_true')
args = parser.parse_args()

sources = 'gdp', 'population'

def feed_kafka(source):
    kafka_producer = KafkaProducer(bootstrap_servers=['kafka:9092'],
#                         key_serializer=lambda x: dumps(x).encode('utf-8'),
                        value_serializer=lambda x: dumps(x).encode('utf-8')
                    )
    topic = source
    csv_file_path = f"sources-data/{source}-dataset.csv"
    with open(csv_file_path, 'r') as csv_file:
        next(csv_file) # skip headline
        csv_data = csv.reader(csv_file, delimiter=';')
        for line in csv_data:
            future = kafka_producer.send(topic, line)
            future.get()
        kafka_producer.flush()
    print(f"Kafka feeded with {source}")

def kafka_to_cassandra():
    cluster = Cluster(['cassandra'])
    session = cluster.connect('gdp')

    kafka_consumer = KafkaConsumer('gdp',
                         consumer_timeout_ms=5000,
                         auto_offset_reset='earliest',
                         bootstrap_servers=['kafka:9092'],
                         value_deserializer=lambda m: loads(m.decode('utf-8'))
                         )
    for msg in kafka_consumer:
        country = msg.value[0]
        gdp = msg.value[1].replace(',', '.') or 0
        gdp = float(gdp)
        sql = 'INSERT INTO data (country, gdp) VALUES (%s, %s)'
        session.execute(sql, (country, gdp))
    print('Cassandra feeded')

def kafka_to_mongo():
    mongo_conn = pymongo.MongoClient('mongo')
    mongo_db = mongo_conn['population']
    mongo_coll = mongo_db['data']

    kafka_consumer = KafkaConsumer('population',
                     consumer_timeout_ms=5000,
                     auto_offset_reset='earliest',
                     bootstrap_servers=['kafka:9092'],
                     value_deserializer=lambda m: loads(m.decode('utf-8'))
                     )
    for msg in kafka_consumer:
        country = msg.value[0]
        population = msg.value[1] or -1
        mongo_coll.save({ 'country': country, 'population': population })
    print('Mongo feeded')

def produce():
    [feed_kafka(source) for source in sources]

def consume():
    kafka_to_cassandra()
    kafka_to_mongo()

def main():
    if args.produce:
        produce()
    elif args.consume:
        consume()


if __name__ == '__main__':
    main()
