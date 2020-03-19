import time,json,datetime
import requests
from requests.auth import HTTPBasicAuth
from utility_funcs import *

class test_set:
    def __init__(self):
        self.PoPname = ''
        self.no_of_executions = 1
        self.priority = 5
        self.list = []

class test_set_item:
    def __init__(self):
        # self.testtypename = ''
            ##A-party:
        #Route:
        # self.route_id = 0
        # self.route_ext_id = 0
        #SMS route:
        self.sms_route_id = 0
        # self.sms_route_ext_id = 0
        #SMS template name:
        self.sms_template_name = ''
        #A test node ID:
        # self.atestnodeid = ''
            ##B-party:
        #Test node:
        # self.btestnodeid = ''
        #Destination:
        self.destination_id = 0
        # self.destination_ext_id = 0
        # self.all_test_nodes = True
        #Number:
        # self.phone_number = 0
        #BPLMN:
        # self.bplmn = ''

class test_batch:
    def __init__(self):
        self.test_batch_id = 0
        self.status_id = 500
        self.status = ''
        self.isdone = False
        self.created_time = get_time()
        self.list = []

class test_batch_item:
    def __init__(self):
        self.status_id = 0
        self.status = ''
        self.isdone = False


class client:
    
    def task(self,sms_template_name,sms_route_id,btestnodeid,no_of_executions):
        base_address = 'https://h-184-169-141-83.csg-assure.com/api/'
        #print version:
        response = requests.get(base_address+'version',
                         auth=HTTPBasicAuth('APIadmin', 'PlivoCsg2018'))
        if response.status_code == 200:
            print response.text
        #create test set to send an sms:
        api_test_set = test_set()
        api_test_set.no_of_executions = no_of_executions
        api_test_set_item = test_set_item()
        api_test_set_item.sms_template_name = sms_template_name
        api_test_set_item.sms_route_id = sms_route_id
        api_test_set_item.btestnodeid = btestnodeid
        # api_test_set_item.destination_id = int(btestnodeid)
        api_test_set.list.append(api_test_set_item)
        #POST method to create a new test batch:
        # print make_dict(api_test_set)
        response = requests.post(base_address+'TestBatches', json=make_dict(api_test_set),
                                 auth=HTTPBasicAuth('APIadmin', 'PlivoCsg2018'))
        print response.status_code#, response.text
        if response.status_code == 201:
            # print response.text
            test_batch_id = json.loads(response.text)['TestBatchID']
            print test_batch_id
            start = datetime.datetime.now()
            #Get status of test batch till its done
            while True:
                response = requests.get(base_address+'TestBatches/'+str(test_batch_id), 
                                        auth=HTTPBasicAuth('APIadmin', 'PlivoCsg2018'))
                # print response.status_code
                if response.status_code == 200:
                    test_Batch = test_batch()
                    test_Batch = match(test_Batch,json.loads(response.text))
                    # print json.loads(response.text)["IsDone"]
                    now = datetime.datetime.now()
                    delta =  now - start
                    seconds = divmod(delta.days * 86400 + delta.seconds, 60)[0]*60 + divmod(delta.days * 86400 + delta.seconds, 60)[1]
                    print seconds
                    if (test_Batch.isdone or seconds >= 60):
                        print "Batch done with status:"+test_Batch.status
                        #Batch is done, get results now:
                        response = requests.get(base_address+'TestBatchResults/'+str(test_Batch.test_batch_id),
                                                auth=HTTPBasicAuth('APIadmin', 'PlivoCsg2018'))
                        sms_result = response.text
                        # print "len of sms results:"
                        # print len(json.loads(sms_result)["TestBatchResult1"])
                        return sms_result
                    else:
                        print "Batch executing with status:"+test_Batch.status
                else:
                    print "GET failed"
                    break
                time.sleep(5)
        else:
            print "POST failed"
        return None




