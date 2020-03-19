import sys
from api_csg import *
import random

class del_time:
    def __init__(self):
        self.aggregate_type = 'Avg'
        self.threshold_value = 0

class oa_criteria:
    def __init__(self):
        self.evaluation_type = ''
        self.success_rate = 0

class evalu:
    def __init__(self):
        self.no_of_tests = 2
        self.delivery_rate = 0
        self.delivery_time = del_time()
        self.oa_R_criteria = oa_criteria()

class eval_results:
    def __init__(self):
        self.delivery_rate = 0
        self.delivery_time_avg = 0.0
        self.delivery_time_median = 0.0
        self.delivery_time_75_percentile = 0.0
        self.delivery_time_90_percentile = 0.0

class sms_group:
    
    def __init__(self):
        self.mcc = 0
        self.mnc = 0
        self.sms_group_name = ''
        self.sms_group_id = ''
        self.country = ''
        self.CSG_destination_id = 0
        self.CSG_test_node_id = 0
        self.CSG_test_node_uid = ''
        self.evaluation_schedule = ''
        self.evaluation_criteria = evalu()
        self.evaluation_results = {}
        self.run_id = 0
        self.run_status = ''

    def populate_group(self,sms_group_id,conn):
        # trim row for values: 
        self.mcc = fetch_value('mcc',sms_group_id,conn)
        self.mnc = fetch_value('mnc',sms_group_id,conn)
        self.sms_group_name = fetch_value('sms_group_name', sms_group_id, conn)
        self.sms_group_id = fetch_value('sms_group_id', sms_group_id, conn)
        self.country = fetch_value('country', sms_group_id, conn)
        self.CSG_destination_id = fetch_value('CSG_destination_id', sms_group_id, conn)
        self.CSG_test_node_id = fetch_value('CSG_test_node_id', sms_group_id, conn)
        self.CSG_test_node_uid = fetch_value('CSG_test_node_uid', sms_group_id, conn)
        self.evaluation_schedule = fetch_value('evaluation_schedule', sms_group_id, conn)
        self.evaluation_criteria.no_of_tests = int(fetch_value('(evaluation_criteria).no_of_tests', sms_group_id, conn))
        self.evaluation_criteria.delivery_rate = int(fetch_value('(evaluation_criteria).delivery_rate', sms_group_id, conn))
        self.evaluation_criteria.delivery_time.aggregate_type = str(fetch_value('((evaluation_criteria).delivery_time).aggregate_type', sms_group_id, conn))[2:-2]
        self.evaluation_criteria.delivery_time.threshold_value = float(fetch_value('((evaluation_criteria).delivery_time).threshold_value', sms_group_id, conn))
        # self.evaluation_criteria.oa_R_criteria.evaluation_type = fetch_value('((evaluation_criteria).oa_R_criteria).evaluation_type', sms_group_id, conn)
        # self.evaluation_criteria.oa_R_criteria.success_rate = int(fetch_value('((evaluation_criteria).oa_R_criteria).success_rate', sms_group_id, conn))
        self.run_status = fetch_value('run_status', sms_group_id, conn)
    
    def print_group(self):
        print self.mcc, self.mnc, self.sms_group_name, self.sms_group_id, self.country, self.CSG_destination_id, self.CSG_test_node_id, self.CSG_test_node_uid, self.evaluation_schedule, self.evaluation_criteria.no_of_tests, self.evaluation_criteria.delivery_rate, self.evaluation_criteria.delivery_time.aggregate_type, self.evaluation_criteria.delivery_time.threshold_value, self.evaluation_criteria.oa_R_criteria.evaluation_type, self.evaluation_criteria.oa_R_criteria.success_rate, self.run_status

    def fetch_routing(self):
        ###PRODUCTION API:---
        # base_address = "https://ryuk.ovilp.io/api/v1/sms-carrier-profile/1/sms-group/"
        # response = requests.get(base_address+str(self.sms_group_id),
        #                 auth=HTTPBasicAuth('MANZK1NWJIMTUYYWRIY2', 'ZTY2NGNkZTEyODQzMjk2ZmI5YTU0MzJmZjhiYWUy'))
        #----
        ###STAGING API:---
        base_address = "https://ryuk.test.plivo.com/api/v1/sms-carrier-profile/1/sms-group/"
        response = requests.get(base_address+str(self.sms_group_id),
                                auth=HTTPBasicAuth('MAOTVJNMIYMGIXNMQ4NW', 'ODRmOTY0ZmIyYzk1M2I4NDUyMjhjY2ZmODhhNmI3'))
        #----
        response = json.loads(response.text)
        for carrier in response['routing']:
            if response['routing'][carrier]['carrier_id'] not in self.evaluation_results:
                self.evaluation_results[response['routing'][carrier]['carrier_id']] = eval_results()
        print response
        return response

    def post_routing(self,new_route):
            new_route = dict(new_route)
            new_route1 = {}
            for key in new_route:
                new_route1[str(key)[:-8]] = new_route[key]
            new_route = new_route1
            ###PRODUCTION API:---
            # base_address = "https://ryuk.ovilp.io/api/v1/sms-carrier-profile/1/sms-group/"
            # response = requests.get(base_address+str(self.sms_group_id),
            #                 auth=HTTPBasicAuth('MANZK1NWJIMTUYYWRIY2', 'ZTY2NGNkZTEyODQzMjk2ZmI5YTU0MzJmZjhiYWUy'))
            #----
            ###STAGING API:---
            # print dict(routing=dict(new_route))
            base_address = "https://ryuk.test.plivo.com/api/v1/sms-carrier-profile/1/sms-group/"
            response = requests.post(base_address+str(self.sms_group_id)+'/', json=dict(routing=dict(new_route)),
                                     auth=HTTPBasicAuth('MAOTVJNMIYMGIXNMQ4NW', 'ODRmOTY0ZmIyYzk1M2I4NDUyMjhjY2ZmODhhNmI3'))
            #----
            print response.status_code, response.text

    def check_update_routing(self,response,conn):
        new_routing = {}
        is_routing_updated = True
        flag = 0 #flag = 1 if p1 has failed.
        flago = 0 #flago = 1 if replacement for p1 has been found.

        #Make an entry in run_log and pass the run_id:
        cur = conn.cursor()
        evaluation_criteria = {}
        evaluation_criteria["no_of_tests"] = self.evaluation_criteria.no_of_tests
        evaluation_criteria["delivery_rate"] = self.evaluation_criteria.delivery_rate
        evaluation_criteria["delivery_time"] = {}
        evaluation_criteria["delivery_time"]["aggregate_type"] = self.evaluation_criteria.delivery_time.aggregate_type
        evaluation_criteria["delivery_time"]["threshold_value"] = self.evaluation_criteria.delivery_time.threshold_value
        t_s = get_time()
        cur.execute("INSERT INTO run_log (sms_group_id, is_routing_updated, old_route, start_timestamp, evaluation_criteria) VALUES (%s,%s,%s,%s,%s);", [self.sms_group_id, 'False', json.dumps(response['routing']), t_s, json.dumps(evaluation_criteria)])
        cur.execute("COMMIT;")
        cur.execute("SELECT id FROM run_log WHERE start_timestamp=%s AND sms_group_id=%s", [t_s,self.sms_group_id])
        self.run_id = int(str(cur.fetchone())[1:-2])
        cur.close()

        #Check for p1:
        for carrier in response['routing']:
            # print response['routing'][carrier]
            # self.evaluate(response['routing'][carrier], conn)
            if carrier == 'p1_carrier':
                print "Evaluating p1:"+response['routing'][carrier]["carrier_name"]
                if (self.evaluate(response['routing'][carrier],conn)):
                    print "p1 has passed.Doing nothing"
                    break
                    # return new_routing,response['routing'][carrier]
                else:
                    print "p1 failed; testing others"
                    flag = 1
                    break
        #Condition:p1 failed:
        if flag==1 :
            for carrier in response['routing']:
                if carrier != 'p1_carrier':
                    print "Evaluating: "+response['routing'][carrier]['carrier_name']
                    if (self.evaluate(response['routing'][carrier], conn)):
                        p1_carrier = carrier
                        print "New p1:"+p1_carrier
                        flago = 1
                        break
                    else:
                        print carrier+" has failed the evaluation."
        #Condition:p1 failed and is to be replaced by other carrier:
        if flago==1 :
            print 'new_routing is being made...'
            for carrier in response['routing']:
                if carrier != 'p1_carrier' and carrier != p1_carrier:
                    new_routing[carrier] = response['routing'][carrier]  
            new_routing[p1_carrier] = response['routing']["p1_carrier"]
            new_routing["p1_carrier"] = response['routing'][p1_carrier]
            print "new_routing:-------"
            print new_routing 
            print "-------------------"
        #Condition:p1 has not failed or none of the carriers have passed:
        if flag==0 or (flag==1 and flago==0):
            new_routing = response['routing']
            if flag==1:
                print "All of the carriers have failed."
        #POST HERE->
        if(new_routing["p1_carrier"]["carrier_id"]!=response['routing']["p1_carrier"]["carrier_id"]):
            is_routing_updated = True
            self.post_routing(new_routing)
        else:
            is_routing_updated = False
            print "Old routing is the same as new."
        self.set_record_routing(is_routing_updated ,new_routing, response['routing'], self.run_id, conn)

    def evaluate(self, carrier_dict, conn, sms_template_name='SMS MT (GSM)', sms_route_id=0):
        if get_sms_route(carrier_dict,conn)!=None:
            sms_route_id = get_sms_route(carrier_dict, conn)
            print sms_route_id
        else:
            sys.exit("SMSRouteID not found!")
        carrier_tests = []
        client1 = client()
        node_down = False
        carrier_down = False
        unknown = False
        count_node_down = 0
        
        #fetch sms_results:
        count_no_sms_result = 0
        flag = 1
        while flag != 0:
            t_s = get_time()
            sms_results = client1.task(sms_template_name,sms_route_id,self.CSG_test_node_uid,self.evaluation_criteria.no_of_tests)
            if sms_results != None:
                flag = 0
                t_e = get_time()
                sms_results = json.loads(sms_results)
            elif count_no_sms_result == 5:
                sys.exit("Exceeded number of tries, no response from api")
            else:
                count_no_sms_result += 1
                print "Could not get sms_results, retrying..."
        
        #sms_results obtained process them:
        for sms_result in sms_results["TestBatchResult1"]:
            if sms_result != None:
                # print sms_result
                if t_s not in sms_result:
                    sms_result["t_s"] = t_s
                if t_e not in sms_result:
                    sms_result["t_e"] = t_e
                #Handle each test based on Status and Result:
                if sms_result["UITestStatusDisplay"] == "Successful" and sms_result["Result"] == "SMS delivery successful.":
                    carrier_tests.append(sms_result)
                elif sms_result["UITestStatusDisplay"] == "Failed" and sms_result["Result"] == "SMS send failed. See the customer system response in column Error Message for details.":
                    #ROW updation:--
                    row = [None]*8
                    carrier_test = sms_result
                    row[0] = self.sms_group_id
                    row[1] = self.run_id
                    row[2] = carrier_dict["carrier_id"]
                    row[3] = carrier_test["t_s"]
                    row[4] = carrier_test["t_e"]
                    row[5] = carrier_test["UITestStatusDisplay"]
                    row[6] = carrier_test["Result"]
                    row[7] = carrier_test
                    self.set_record_test(row, conn)
                    print row[5]
                    #--
                    carrier_down = True
                elif sms_result["UITestStatusDisplay"] == "Failed" and sms_result["Result"] == "SMS delivery failed.":
                    carrier_tests.append(sms_result)
                elif sms_result["UITestStatusDisplay"] == "Invalid" and sms_result["Result"] == "The B party test node is not connected to IP. SMS not submitted":
                    print sms_result
                    if count_node_down == 3:
                        node_down = True
                    #ROW updation:--
                    row = [None]*8
                    carrier_test = sms_result
                    row[0] = self.sms_group_id
                    row[1] = self.run_id
                    row[2] = carrier_dict["carrier_id"]
                    row[3] = carrier_test["t_s"]
                    row[4] = carrier_test["t_e"]
                    row[5] = carrier_test["UITestStatusDisplay"]
                    row[6] = carrier_test["Result"]
                    row[7] = carrier_test
                    self.set_record_test(row, conn)
                    print row[5]
                    #--
                    count_node_down += 1
                elif sms_result["UITestStatusDisplay"] == "Failed" and sms_result["Result"] == "SMS delivered but with modified content.":
                    carrier_tests.append(sms_result)
                elif sms_result["UITestStatusDisplay"] == "Running" or sms_result["UITestStatusDisplay"] == "Waiting":
                    carrier_tests.append(sms_result)
                else:
                    #ROW updation:--
                    row = [None]*8
                    carrier_test = sms_result
                    row[0] = self.sms_group_id
                    row[1] = self.run_id
                    row[2] = carrier_dict["carrier_id"]
                    row[3] = carrier_test["t_s"]
                    row[4] = carrier_test["t_e"]
                    row[5] = carrier_test["UITestStatusDisplay"]
                    row[6] = carrier_test["Result"]
                    row[7] = carrier_test
                    self.set_record_test(row, conn)
                    print row[5]
                    #--
                    unknown = True
        
        #check number of useful tests:
        if len(carrier_tests) == self.evaluation_criteria.no_of_tests:
            print "Evaluating the results..."
            return self.check_pass(carrier_dict, carrier_tests, conn)
        else:
            print "Run ignored due to insufficent results, check logs."
            #Complete the entry made in run_log table:
            cur = conn.cursor()
            t_e = get_time()
            cur.execute("UPDATE run_log SET end_timestamp = %s WHERE id = %s;",[t_e,str(self.run_id)])
            cur.execute("COMMIT;")
            #Print state of csg_test_log:
            cur.execute("SELECT * FROM csg_test_log;")
            returns = cur.fetchall()
            print "TABLE:csg_test_log:----------"
            print returns
            print "-----------------------------"
            #Print state of csg_run_log:
            cur.execute("SELECT * FROM run_log;")
            returns = cur.fetchall()
            print "TABLE:run_log:----------"
            print returns
            print "-------------------------"
            cur.close()
            #Exit the function according to the case:
            if node_down or unknown:
                sys.exit("Ignore run, as node is down or result is unknown")
            elif carrier_down:
                return False
            else:
                sys.exit("Ignore run")
        
    def check_pass(self, carrier_dict, carrier_tests, conn):
        delivery_count = 0
        delivery_time_sum = 0
        carrier_delivery_times = []
        for carrier_test in carrier_tests:
            row = [None]*8
            if carrier_test["UITestStatusDisplay"] == "Successful":
                delivery_count += 1
                delivery_time_sum += carrier_test["Del. Time (sec)"]
                carrier_delivery_times.append(carrier_test["Del. Time (sec)"])
            elif carrier_test["UITestStatusDisplay"] == "Failed" and carrier_test["Result"] == "SMS delivered but with modified content.":
                delivery_count += 1
                delivery_time_sum += carrier_test["Del. Time (sec)"]
                carrier_delivery_times.append(carrier_test["Del. Time (sec)"])
            else:
                delivery_time_sum += 60
                carrier_delivery_times.append(60)
            #ROW updation:--
            # print self.run_id
            row[0] = self.sms_group_id
            row[1] = self.run_id
            row[2] = carrier_dict["carrier_id"]
            row[3] = carrier_test["t_s"]
            row[4] = carrier_test["t_e"]
            row[5] = carrier_test["UITestStatusDisplay"]
            row[6] = carrier_test["Result"]
            row[7] = carrier_test
            self.set_record_test(row,conn)
            print row[5]
            #--
        #Print log_table_test:--
        cur = conn.cursor()
        sql = "SELECT * FROM csg_test_log;"
        cur.execute(sql)
        rows = cur.fetchall()
        print "Current state of csg_test_log:----"
        print rows
        print "------------------------------------"
        cur.close()
        #--
        #Calculate evaluation parameters:--
        carrier_delivery_times.sort(reverse=True)
        self.evaluation_results[str(carrier_dict['carrier_id'])].delivery_rate = ((delivery_count*1.0)/self.evaluation_criteria.no_of_tests)*100
        self.evaluation_results[str(carrier_dict['carrier_id'])].delivery_time_avg = (delivery_time_sum*1.0)/self.evaluation_criteria.no_of_tests
        self.evaluation_results[str(carrier_dict['carrier_id'])].delivery_time_median = find_aggregate(carrier_delivery_times,self.evaluation_criteria.no_of_tests,'median')
        self.evaluation_results[str(carrier_dict['carrier_id'])].delivery_time_75_percentile = find_aggregate(carrier_delivery_times,self.evaluation_criteria.no_of_tests,'75_percentile')
        self.evaluation_results[str(carrier_dict['carrier_id'])].delivery_time_90_percentile = find_aggregate(carrier_delivery_times,self.evaluation_criteria.no_of_tests,'90_percentile')        
        #--

        #EVALUATION HERE ->
        # print (self.evaluation_criteria.delivery_time.aggregate_type=='average')
        if (self.evaluation_results[carrier_dict['carrier_id']].delivery_rate >= self.evaluation_criteria.delivery_rate):
            if self.evaluation_criteria.delivery_time.aggregate_type == 'average' and self.evaluation_results[carrier_dict['carrier_id']].delivery_time_avg <= self.evaluation_criteria.delivery_time.threshold_value:
                print "Carrier: "+carrier_dict["carrier_name"]+" has passed the evaluation!"
                return True
            elif self.evaluation_criteria.delivery_time.aggregate_type == 'median' and self.evaluation_results[carrier_dict['carrier_id']].delivery_time_median <= self.evaluation_criteria.delivery_time.threshold_value:
                print "Carrier: "+carrier_dict["carrier_name"]+" has passed the evaluation!"
                return True
            elif self.evaluation_criteria.delivery_time.aggregate_type == '75_percentile' and self.evaluation_results[carrier_dict['carrier_id']].delivery_time_75_percentile <= self.evaluation_criteria.delivery_time.threshold_value:
                print "Carrier: "+carrier_dict["carrier_name"]+" has passed the evaluation!"
                return True
            elif self.evaluation_criteria.delivery_time.aggregate_type == '90_percentile' and self.evaluation_results[carrier_dict['carrier_id']].delivery_time_90_percentile <= self.evaluation_criteria.delivery_time.threshold_value:
                print "Carrier: "+carrier_dict["carrier_name"]+" has passed the evaluation!"
                return True
        print "average delivery time for "+carrier_dict["carrier_name"]+" : "+str(self.evaluation_results[carrier_dict['carrier_id']].delivery_time_avg)
        return False

    def set_record_test(self,row,conn):
        cur = conn.cursor()
        cur.execute("INSERT INTO csg_test_log (sms_group_id, run_id, carrier_id, start_timestamp, end_timestamp, csg_test_status, csg_test_result, csg_result_data) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);", [row[0], row[1], row[2], row[3], row[4], row[5], row[6],json.dumps(row[7])])
        cur.execute("COMMIT;")
        cur.close()

    def set_record_routing(self, is_routing_updated, new_routing, old_routing, run_id, conn):
        cur = conn.cursor()
        if is_routing_updated:
            cur.execute("UPDATE run_log SET is_routing_updated = %s, old_route = %s, new_route = %s, end_timestamp = %s WHERE id = %s;",[is_routing_updated,json.dumps(old_routing),json.dumps(new_routing),get_time(),str(self.run_id)])
        else:
            cur.execute("UPDATE run_log SET is_routing_updated = %s, old_route = %s, end_timestamp = %s WHERE id = %s;",[is_routing_updated,json.dumps(old_routing),get_time(),str(self.run_id)])
        cur.execute("COMMIT;")
        for carrier_id in self.evaluation_results:
            temp_dict = {}
            temp_dict["average"] = self.evaluation_results[carrier_id].delivery_time_avg
            temp_dict["median"] = self.evaluation_results[carrier_id].delivery_time_median
            temp_dict["75_percentile"] = self.evaluation_results[carrier_id].delivery_time_75_percentile
            temp_dict["90_percentile"] = self.evaluation_results[carrier_id].delivery_time_90_percentile
            if temp_dict["average"] != 0.0 or self.evaluation_results[carrier_id].delivery_rate != 0:
                cur.execute("INSERT INTO eval_results_log (carrier_id, run_id, delivery_rate, delivery_time) VALUES (%s,%s,%s,%s);",[carrier_id, self.run_id, self.evaluation_results[carrier_id].delivery_rate, json.dumps(temp_dict) ])
        cur.execute("COMMIT;")
        #Print table:run_log
        sql = "SELECT * FROM run_log;"
        cur.execute(sql)
        rows = cur.fetchall()
        print "Table:run_log------"
        for row in rows:
            print row
        print "--------------------"
        #--
        #Print table:eval_results_log
        sql = "SELECT * FROM eval_results_log;"
        cur.execute(sql)
        rows = cur.fetchall()
        print "Table:eval_results_log------"
        for row in rows:
            print row
        print "-----------------------------"
        #--
        cur.close()

