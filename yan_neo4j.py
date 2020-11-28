#######yan_neo4j.py#######
import os
import time
from neo4j import *

def initialize_neo4j_session(http_port, bolt_port):
	###
	os.system(u"""
	rm /neo4j-community-3.5.12/conf/neo4j.conf
	echo "dbms.security.auth_enabled=true" > /neo4j-community-3.5.12/conf/neo4j.conf
	echo "dbms.connectors.default_listen_address=0.0.0.0" >> /neo4j-community-3.5.12/conf/neo4j.conf
	echo "dbms.connector.http.enabled=true" >> /neo4j-community-3.5.12/conf/neo4j.conf
	echo "dbms.connector.http.address=0.0.0.0:%s" >> /neo4j-community-3.5.12/conf/neo4j.conf
	echo "dbms.connector.bolt.enabled=true" >> /neo4j-community-3.5.12/conf/neo4j.conf
	echo "dbms.connector.bolt.address=0.0.0.0:%s" >> /neo4j-community-3.5.12/conf/neo4j.conf
	"""%(http_port,bolt_port))
	####
	os.system(u"""
	rm /neo4j-community-3.5.12/data/dbms/auth
	/neo4j-community-3.5.12/bin/neo4j-admin set-initial-password neo4j1
	""")
	####
	os.system(u"""
	/neo4j-community-3.5.12/bin/neo4j start
	""")
	####
	while(True):
		try:
			neo4j_instance = GraphDatabase.driver("bolt://0.0.0.0:%s/"%(bolt_port), auth=('neo4j', 'neo4j1'))
			neo4j_session = neo4j_instance.session()
			neo4j_session.run(u"""
			MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r;
			""")
			break
		except:
			pass
	return neo4j_session

def ingest_knowledge_triplets_to_neo4j(triplets,
	neo4j_session,
	delete_data = True):
	neo4j_session.run(u"""
	MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r;
	""")
	#######
	unique_entities = list({item["entity_id"]: item for item in [{'entity_id': t['subject'], 
		'entity_type': t['subject_type'], 
		'entity_name': t['subject_name']} 
		for t in triplets] \
		+ [{'entity_id': t['object'], 
		'entity_type': t['object_type'], 
		'entity_name': t['object_name']} 
		for t in triplets]}.values())
	for e in unique_entities:
		try:
			neo4j_session.run(u"""
			MERGE (n:%s { value: '%s', id: '%s' });
			"""%(e['entity_type'], e['entity_name'], e['entity_id']))
		except:
			pass
	#####
	for t in triplets:
		try:
			neo4j_session.run(
			u"""
			MATCH (a:%s),(b:%s) WHERE a.id = '%s' AND b.id = '%s' 
			MERGE (a)-[r:%s]->(b);
			"""%(t['subject_type'], t['object_type'], 
				t['subject'], t['object'], 
				t['relation']))
		except:
			pass

'''
from yan_neo4j import * 

neo4j_session = initialize_neo4j_session(http_port = "6779", bolt_port = "7484")

t = [{
'subject':"a",
'subject_type':"b",
'subject_name':"c",
'object':"d",
'object_type':"e",
'object_name':"f",
'relation':"g",
}]
ingest_knowledge_triplets_to_neo4j(t, neo4j_session)

neo4j: http://0.0.0.0:6779/
'''
#######yan_neo4j.py#######
