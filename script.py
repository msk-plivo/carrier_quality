import psycopg2
from configparser import ConfigParser
from sms_group import *
from api_csg import *
from utility_funcs import *

# context, event
def script(sms_group_id):
    try:
        progress = "IN PROGRESS"
        nprogress = "NOT IN PROGRESS"

        #Connect to db and get records:
        # sms_group_id = int(context['Records'][0]['Sns']['Message'])
        conn = connect()
        sms_group1 = sms_group()
        sms_group1.populate_group(sms_group_id,conn)
        sms_group1.print_group()
        
        #Check if the sms_group is already involved in a run:
        cur = conn.cursor()
        cur.execute("SELECT run_status FROM sms_group_configuration WHERE sms_group_id = %s;",[sms_group1.sms_group_id])
        status = cur.fetchone()
        cur.close()
        status = str(status)[2:-3]

        if status == nprogress:
            #Change the status of sms_group in the db:
            cur = conn.cursor()
            cur.execute("UPDATE sms_group_configuration SET run_status = %s WHERE sms_group_id = %s;",[progress, sms_group1.sms_group_id])
            cur.execute("COMMIT;")
            cur.execute("SELECT * FROM sms_group_configuration WHERE sms_group_id = %s;",[sms_group1.sms_group_id])
            row = cur.fetchone()
            print row
            
            #Perform evaluation on the carriers of the sms_group and update accordingly:
            # sms_group1.check_update_routing(sms_group1.fetch_routing(), conn)
            sms_group1.fetch_routing()
            new_route = {u'p2_carrier': {u'carrier_name': u'infobip', u'carrier_id': u'27996364767194'}, u'p1_carrier': {u'carrier_name': u'clx', u'carrier_id': u'29755601396636'}}
            sms_group1.post_routing(new_route)
            sms_group1.fetch_routing()

        elif status == progress:
            print "sms_group already involved in a run; Doing nothing"

    except Exception as error:
        print error

    finally:
        #Change the status of sms_group in the db:
        cur = conn.cursor()
        cur.execute("UPDATE sms_group_configuration SET run_status = %s WHERE sms_group_id = %s;", [nprogress, sms_group1.sms_group_id])
        cur.execute("COMMIT;")
        cur.execute("SELECT * FROM sms_group_configuration WHERE sms_group_id = %s;",[sms_group1.sms_group_id])
        row = cur.fetchone()
        cur.close()
        print row

        #Disconnect the db:
        disconnect(conn)

def main():
    # print sys.argv[1]
    script(int(sys.argv[1]))

if __name__ == '__main__':
    main()


