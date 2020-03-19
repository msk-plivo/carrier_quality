import croniter
import datetime
import boto3
import psycopg2
from configparser import ConfigParser

# from script import *


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
        print error
    return conn
    # finally:
    #     if conn is not None:
    #         conn.close()
    #         print('Database connection closed.')


def disconnect(conn):
    if conn is not None:
            conn.close()
            print('Database connection closed.')


def get_time():
    localtime = time.asctime(time.localtime(time.time()))
    return localtime


def handler(context, event):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT sms_group_id, evaluation_schedule FROM sms_group_configuration;")
    rows = cur.fetchall()
    for row in rows:
        # print row[0]
        # script(int(row[0]))
        now = datetime.datetime.now()
        cron1 = croniter.croniter(row[1], now)
        cron2 = croniter.croniter(row[1], now)
        a = now
        b = cron1.get_next(datetime.datetime)
        c = b - a
        d = divmod(c.days * 86400 + c.seconds,
                   60)[0]*60 + divmod(c.days * 86400 + c.seconds, 60)[1]
        e = cron2.get_prev(datetime.datetime)
        f = a - e
        g = divmod(f.days * 86400 + f.seconds,
                   60)[0]*60 + divmod(f.days * 86400 + f.seconds, 60)[1]
        # print d, g
        if d <= 60 or g <= 60:
            # print row[0], d
            try:
                client = boto3.client('sns', region_name='us-east-1')
                response = client.publish(
                    TopicArn='arn:aws:sns:us-east-1:105541789255:carrierqualitysns',
                    Message=str(row[0]),
                )
            # print response
            except Exception as error:
                print error

            else:
                print "Run Triggered with sms_group_id:" + \
                    str(row[0])+"time:"+str(datetime.datetime.now())

        # else:
            # print 'No action taken.'

            # if __name__ == '__main__':
            #     handler()
