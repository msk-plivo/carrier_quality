import time
import json
import psycopg2
from configparser import ConfigParser

#Utility functions:--
def config(filename='database.ini', section='postgresql'):
     # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} not found in the {1} file'.format(section, filename))

    return db

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
         # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

     # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return conn
    # finally:
    #     if conn is not None:
    #         conn.close()
    #         print('Database connection closed.')

def disconnect(conn):
    if conn is not None:
            conn.close()
            print('Database connection closed.')


def fetch_value(column,sms_group_id,conn):
    cur = conn.cursor()
    cur.execute("SELECT "+column+" FROM sms_group_configuration WHERE sms_group_id="+str(sms_group_id)+";")
    value = cur.fetchone()
    # print str(value)[1:-2]
    cur.close()
    return str(value)[1:-2]

def get_records(conn):
    sql = "SELECT * FROM sms_group_configuration ;"
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    return rows

def match(test_Batch,response):
    test_Batch.test_batch_id = response["TestBatchID"]
    test_Batch.status_id = response["StatusID"]
    test_Batch.isdone = response["IsDone"]
    test_Batch.created_time = response["Created"]
    test_Batch.status = response["Status"]
    test_Batch.list = response["TestBatchItems"]
    return test_Batch

def make_dict(test_set):
    payload = {}
    # payload['PoPName'] = test_set.PoPname
    payload['NoOfExecutions'] = int(test_set.no_of_executions)
    # payload['Priority'] = test_set.priority
    payload["TestSetItems"] = []
    for item in test_set.list:
        payload["TestSetItems"].append(make_dict1(item))
    return payload

def make_dict1(test_set_item):
    item = {}
    # item['testtypename'] = test_set_item.testtypename
    # item['route_id'] = test_set_item.route_id
    # item['route_ext_id'] = test_set_item.route_ext_id
    item["SMSRouteID"] = test_set_item.sms_route_id
    # item['sms_route_ext_id'] = test_set_item.sms_route_ext_id
    item["SMSTemplateName"] = test_set_item.sms_template_name
    # item['atestnodeid'] = test_set_item.atestnodeid
    item['BTestNodeUID'] = test_set_item.btestnodeid.strip('\'')
    # item["DestinationID"] = test_set_item.destination_id
    # item['destination_ext_id'] = test_set_item.destination_ext_id
    # item["AllTestNodes"] = str(test_set_item.all_test_nodes)
    # item['phone_number'] = test_set_item.phone_number
    return item

def find_aggregate(carrier_delivery_times,x,aggregate_type):
    if aggregate_type == 'median':
        if x/2 == 0:
            x = 1
        else:
            x = x/2
    elif aggregate_type == '75_percentile':
        if x/4 == 0:
            x = 1
        else:
            x = x/4
    elif aggregate_type == '90_percentile':
        if x/10 == 0:
            x = 1
        else:
            x = x/10
    return carrier_delivery_times[x-1]

def get_sms_route(carrier_dict, conn):
        cur = conn.cursor()
        cur.execute("SELECT sms_route_id FROM plivo_carrier_to_csg_supplier_mapping WHERE plivo_carrier_id=%s;", [
                    carrier_dict["carrier_id"]])
        sms_route_id = str(cur.fetchone())[1:-2]
        cur.close()
        # if(sms_route_id != None):
            # print "sms_route_id:"+sms_route_id
        return sms_route_id

#Export to csv:
def export(tablename, conn, filename='resultfile'):
    query = "SELECT * FROM "+str(tablename)
    cur = conn.cursor()
    outputquery = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)
    with open(filename, 'w') as f:
        cur.copy_expert(outputquery, f)
    cur.close()

def get_time():
    localtime = time.asctime(time.localtime(time.time()))
    return localtime
#--
