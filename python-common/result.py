#!/usr/bin/env python3 

import csv
import sys
import pymongo
import operator
from cassandra.cluster import Cluster

def main():
    result_file_path='/result/result.csv'
    result_dict = dict()
    
    mongo_conn = pymongo.MongoClient('mongo')
    mongo_db = mongo_conn['population']
    mongo_coll = mongo_db['data']
    
    cassandra_cluster = Cluster(['cassandra'])
    cassandra_session = cassandra_cluster.connect('gdp')
    
    sql = "SELECT * FROM data"
    cassandra_result = cassandra_session.execute(sql)
    
    print('Calculating')
    for r in cassandra_result:
        country, gdp = r.country, r.gdp
        print(f"{country}, {gdp}")
        try:
            population = mongo_coll.find_one({ 'country': country })
            population = int(population['population'])
        except:
            print('No population data')
            result_dict[country] = 0
            continue
        print('from mongo: ', population)
        if gdp == 0 or population <= 0:
            print(f"No needed data for {country} ({gdp}, {population})")
        result_dict[country] = gdp / population
    
    print('Sorting')    
    sorted_result = sorted(result_dict.items(), key=operator.itemgetter(1))
    sorted_result.reverse()
 
    print('Writing to CSV file')
    with open(result_file_path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for country, gdp_capi in sorted_result:
            writer.writerow((country, gdp_capi))

    print('End')
    
if __name__ == '__main__':
    main()


