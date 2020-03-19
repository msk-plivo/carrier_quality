-- SELECT pg_terminate_backend(pg_stat_activity.pid)
-- FROM pg_stat_activity
-- WHERE pg_stat_activity.datname = 'testdb'
-- 	AND pid <> pg_backend_pid();

DROP TABLE eval_results_log; 
DROP TABLE plivo_carrier_to_csg_supplier_mapping;
DROP TABLE csg_test_log;
DROP TABLE run_log CASCADE;
DROP TABLE sms_group_configuration CASCADE;
DROP TABLE unconfigured_sms_groups;
DROP TYPE eval CASCADE;
DROP TYPE oa_criteria;
DROP TYPE del_time;


CREATE TYPE del_time AS (
	aggregate_type VARCHAR (300),
	threshold_value DOUBLE PRECISION
);

CREATE TYPE oa_criteria AS (
	evaluation_type VARCHAR (300),
	success_rate INT
);

CREATE TYPE eval AS (
    no_of_tests INT,
    delivery_rate INT,
	delivery_time del_time,
    oa_R_criteria oa_criteria
);

CREATE TABLE sms_group_configuration(
	mcc INT,
	mnc INT,
	sms_group_name VARCHAR (500),
	sms_group_id INT PRIMARY KEY,
	country VARCHAR (100),
	CSG_destination_id INT,
	CSG_test_node_id INT,
	CSG_test_node_uid VARCHAR (300) NOT NULL,
	evaluation_schedule VARCHAR (300),
	evaluation_criteria eval,
	run_status VARCHAR (300)
);

CREATE TABLE unconfigured_sms_groups(
	mcc INT,
	mnc INT,
	sms_group_name VARCHAR (500),
	sms_group_id INT PRIMARY KEY,
	country VARCHAR (100),
	CSG_destination_id INT,
	CSG_test_node_id INT,
	CSG_test_node_uid VARCHAR (300) NOT NULL
);

CREATE TABLE plivo_carrier_to_csg_supplier_mapping(
	plivo_carrier_name VARCHAR (500),
	plivo_carrier_id BIGINT,
	sms_route_id INT
);

CREATE TABLE run_log(
	id SERIAL PRIMARY KEY,
	sms_group_id INT REFERENCES sms_group_configuration(sms_group_id),
	is_routing_updated BOOLEAN NOT NULL,
	old_route JSON,
	new_route JSON,
	start_timestamp TIMESTAMP,
	end_timestamp TIMESTAMP,
	evaluation_criteria JSON
);

CREATE TABLE csg_test_log(
	id SERIAL PRIMARY KEY,
	sms_group_id INT REFERENCES sms_group_configuration(sms_group_id),
	run_id INT REFERENCES run_log(id),
	carrier_id BIGINT,
	start_timestamp TIMESTAMP,
	end_timestamp TIMESTAMP,
	csg_test_status VARCHAR (500),
	csg_test_result VARCHAR (500),
	csg_result_data JSON
);

CREATE TABLE eval_results_log(
	id SERIAL PRIMARY KEY,
	-- carrier_name VARCHAR (300),
	carrier_id BIGINT,
	run_id INT REFERENCES run_log(id),
	delivery_rate INT,
	delivery_time JSON
);

SELECT * FROM sms_group_configuration;
SELECT * FROM plivo_carrier_to_csg_supplier_mapping;
SELECT * FROM csg_test_log;
SELECT * FROM run_log;
SELECT * FROM eval_results_log;

-- INSERT INTO sms_group_configuration (mcc,mnc,sms_group_name,sms_group_id,country,CSG_destination_id,CSG_test_node_id,CSG_test_node_uid,evaluation_schedule,evaluation_criteria,run_status)
-- VALUES (502,17,'Malaysia - Maxis',24,'MY',290,257,'2adb2062-1e5f-4877-9e21-f7f1860a2909','* * * * *',ROW(5,99,ROW('average',4.3),ROW('[a-z]',90)),'NOT IN PROGRESS');

-- COPY plivo_carrier_to_csg_supplier_mapping FROM '/Users/srikar/Desktop/carrier_quality/database/plivo_to_csg_carrier_mappings.csv' DELIMITER ',' CSV;
-- SELECT * FROM plivo_carrier_to_csg_supplier_mapping;

-- psql --host=carrierqualitydb.cfika3hkjd57.us-east-1.rds.amazonaws.com --port=5432 --username=srikar --dbname=testdb -f ~/Desktop/plivo/carrier-quality/database/sms_group_table.sql
-- \copy sms_group_configuration FROM '/Users/srikar/Desktop/plivo/carrier-quality/database/sms_group_configuration.csv' WITH DELIMITER ',' CSV;
-- \copy plivo_carrier_to_csg_supplier_mapping FROM '/Users/srikar/Desktop/plivo/carrier-quality/database/plivo_to_csg_carrier_mappings.csv' WITH DELIMITER ',' CSV;
-- testdb.cs9sq1tkisyl.us-west-1.rds.amazonaws.com




-- GET:dashboard/sms/carrier_quality/$
-- GET:dashboard/sms/carrier_quality/configuration/$
-- GET:dashboard/sms/carrier_quality/logs/$
-- GET:dashboard/sms/carrier_quality/unconfiguredgroups/$
-- POST:dashboard/sms/carrier_quality/configuration/exportcsv/$
-- POST:dashboard/sms/carrier_quality/logs/exportcsv/$
-- POST:dashboard/sms/carrier_quality/configuration/importcsv/$
-- POST:dashboard/sms/carrier_quality/unconfigured/importcsv/$
-- POST:dashboard/sms/carrier_quality/edit/$
-- POST:dashboard/sms/carrier_quality/configure/$
-- POST:dashboard/sms/carrier_quality/addnew/$
-- POST:dashboard/sms/carrier_quality/logs/fetchrundetails/$