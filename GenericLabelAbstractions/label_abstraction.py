#!/usr/bin/python
from congressclient.common import utils
from congressclient.v1 import client
import keystoneclient
import re

#
# Global Configurations
#
label_hierarchy_file = "/etc/neutron/label_hierarchy.conf" 


#
# Digest the label tree defintions and create label trees 
#
def create_label_trees_from_tree_definitions (hier_file):

    hierarchy_file = open(hier_file, 'r')
    label_tree_definitions = hierarchy_file.readlines()
    hierarchy_file.closed
    ltree = []

    for label_tree_definition in label_tree_definitions:
        if not re.search ("^#", label_tree_definition):
            
            # Constructing the actual tree definition
            tree_def_complete_all = label_tree_definition.split("@", 1)
            label_tree_definition = tree_def_complete_all[1]

            # Constructing the Label tree name
            vals = []
            #vals = re.split(":", tree_def_complete_all[0])
            label_tree_name = tree_def_complete_all[0]
            label_tree_name = label_tree_name.strip()
            label_tree_definition = label_tree_definition.strip() 
            entries = re.split(",", label_tree_definition)
            if (len(entries) > 1):
                print ("\n#Extracting multi level label trees ")
                print label_tree_definition
                ltree_t = process_for_multi_level_label_tree \
                                (label_tree_definition, label_tree_name)
                ltree.append(ltree_t)       
            else:
                print ("\n#Extracting single level label trees ")
                print label_tree_definition
                ltree_t = process_for_single_level_label_tree \
                                (label_tree_definition, label_tree_name)
                ltree.append(ltree_t)       

            #print ltree_t
    return ltree 


#
# Process single-level tree defintion and create single-level label tree
#
def process_for_single_level_label_tree (ltree_definition_t, label_tree_name_t):

    print ltree_definition_t, label_tree_name_t 
    ltree = {}
    ltree_definition_t = ltree_definition_t.strip()
    table_name = ltree_definition_t 
    policy_name = "PGAClassification" 
    
    policy_rowlist = congress_policy_row_list (policy_name, table_name)
    if policy_rowlist:
        ltree = store_to_single_level_label_tree (policy_rowlist, label_tree_name_t)
    print ltree
    return ltree


#
# Format to the single level tree
#
def store_to_single_level_label_tree(policy_data_rows_t, tree_name_t):
    print "store_to_single_level_label_tree:", policy_data_rows_t, tree_name_t 
    # Initializing the Label tree dict
    label_tree = {}
    label_tree["label_tree"] = {} 
    label_tree["label_tree"]["name"] = tree_name_t
    label_tree["label_tree"]["lastNodeId"] = len(policy_data_rows_t) + 1
    node_list = []
    
    # Create the Parent/Root node:
    node_p = {}
    node_p["nodeId"] = 1 
    node_p["name"] = tree_name_t
    node_p["parent"] = "null"
    node_list.append(node_p)
    
    # Add the child nodes to the Label tree
    for index, row in enumerate(policy_data_rows_t):
        node = {}
        node["nodeId"] = index + 2
        node["name"] = str(row[1])
        node["parent"] = 1 
        node_list.append(node)
    label_tree["label_tree"]["nodeData"] = node_list
    print label_tree
    return label_tree 


#
# Process multi-level tree defintion and create multi-level label tree
#
def process_for_multi_level_label_tree (ltree_definition_t, label_tree_name_t):
    ltree = {}
    ltree_definition_t = ltree_definition_t.strip()
    policy_rowlist = []

    hierarchy_entries = re.split(",", ltree_definition_t)
    for table_name in hierarchy_entries:
        table_name = table_name.strip()
        policy_name = "PGAClassification" 
        
        rowlist = congress_policy_row_list (policy_name, table_name)
        for row_t in rowlist:
            policy_rowlist.append(row_t)
    if policy_rowlist:
        ltree = store_to_multi_level_label_tree (policy_rowlist, label_tree_name_t)
    return ltree


#
# Storing the multi level data into the Label trees
#
def store_to_multi_level_label_tree(policy_data_rows_t, tree_name_t):
   
    print "store_to_multi_level_label_tree:", policy_data_rows_t, tree_name_t
    # Initializing the Label tree dict
    label_tree = {}
    label_tree["label_tree"] = {} 
    #label_tree["label_tree"]["name"] = tree_name_t.lower()
    label_tree["label_tree"]["name"] = tree_name_t
    label_tree["label_tree"]["lastNodeId"] = len(policy_data_rows_t) + 1
    node_list = []

    # Create the Parent/Root node:
    node_p = {}
    node_p["nodeId"] = 1 
    node_p["name"] = tree_name_t.lower()
    node_p["parent"] = "null"
    node_list.append(node_p)
    
    # Means to track the node number for updatting the child nodes
    node_IDs = {}
    node_name = node_p["name"]
    node_IDs[node_name] = node_p["nodeId"] 
    print node_IDs

    # Add the child nodes to the Label tree
    for index, row in enumerate(policy_data_rows_t):
        node = {}
        node["nodeId"] = index + 2
        p_name = str(row[0]).lower()
        print index, row
        #p_name = str(row[0]) 
        p_name = p_name.strip()
        print p_name
        p_nodeId = node_IDs[p_name]
        node["parent"] = p_nodeId 
        
        # keep track of the node ID number for future reference
        node["name"] = str(row[1]).lower()
        node_name = node["name"]
        node_IDs[node_name] = node["nodeId"] 
        
        node_list.append(node)

    label_tree["label_tree"]["nodeData"] = node_list
    #print label_tree
    return label_tree 


#
# Subroutine to extract the contents of congress policy rows list 
#
def congress_policy_row_list (policy_name_t, table_name_t):

    row_list_data = []
    prow_result = congress.list_policy_rows (policy_name_t, table_name_t)
    for each_data in prow_result['results']:
        row_data = []
        row_list_data.append(each_data['data'])
    return row_list_data

def create_policy (policy_name, label_tree_definition_t):
    
    hierarchy_entries = re.split(":", label_tree_definition_t)
    for entryIndex, entry in enumerate(hierarchy_entries):
        ds_table = re.split("@", entry)
        datastore_name = ds_table[0]
        policy_table_name = ds_table[1]
        policy_table_name = policy_table_name.strip()
        print policy_table_name, datastore_name
    
        #Creating the rules under the policy
        policy_name = 'PGAClassification'
        policy_rule = {}
        policy_rule['rule'] = policy_table_name + '(\"' + policy_table_name + '\", "RegionOne", time_t) :- ' + datastore_name + ':' + policy_table_name + '(' + 'zoneName=az_name ),' + 'now(time_t)'
        print policy_rule['rule']
        #result_pcreate = congress.create_policy_rule (policy_name, policy_rule)
        #result_pcreate = congress.list_policy ()
        #print result_pcreate['results'][2]['name']
        #print result_pcreate
    return ''

def frame_policy (policy_name, label_def):
    #print policy_name, label_def
    policy_rule_t = ''
    return policy_rule_t 


#
# Create datalogs for creating the Label trees 
# using congress policy engine 
#
def create_datalog_policies (hier_file):
    
    # Create the Congress policy classifier for Label tree policies
    policy_name_t = {}
    policy_name_t['name'] = 'PGAClassification' 
    policy_already_exists = 0

    result_plist = congress.list_policy ()
    for policy in result_plist['results']:
        if policy['name'] == policy_name_t['name']:
            policy_already_exists = 1
            print "\n#" + policy['name'] + " policy classifier already exists"

    if policy_already_exists == 0:
        print "Creating the Policy:", policy_name_t
        result_pcreate = congress.create_policy (policy_name_t)
        print result_pcreate 

    # Creating the policy tables for building Label trees
    hierarchy_file = open(hier_file, 'r')
    label_tree_definitions = hierarchy_file.readlines()
    hierarchy_file.closed
    ltree = []

    for label_tree_definition in label_tree_definitions:

        if not re.search ("^#", label_tree_definition):
            # Constructing the table name for policy compilation
            hierarchy_entries = label_tree_definition.split(":", 1)
            label_tree_definition = hierarchy_entries[1]

            # Constructing the congress policy 
            entries = re.split(":", label_tree_definition)
            if (len(entries) > 1):
                print ("\n#Multi Level Hierachy definition")
                print policy_name_t['name'], label_tree_definition
                policy_rule = create_policy (policy_name_t['name'], label_tree_definition)
                #policy_rule_status = create_policy(policy_table_name, policy_rule)
            else:
                print ("\n#Single Level Hierachy definition")
                print policy_name_t['name'], label_tree_definition
                policy_rule = create_policy (policy_name_t['name'], label_tree_definition)
                #policy_rule_status = create_policy(policy_table_name, policy_rule)

    return label_tree_definition


#
# Main Program:
#
if __name__ == "__main__":

    # Create the congress client Instance
    auth = keystoneclient.auth.identity.v2.Password(
            auth_url="http://16.111.37.119:5000/v2.0", username="admin",
            password="ccdemo11", tenant_name="admin")

    session = keystoneclient.session.Session(auth=auth)
    congress = client.Client(session=session,
                auth=None,
                interface='publicURL',
                service_type='policy',
                region_name='RegionOne')

    
    # API to create the lable trees given the label tree hierarchy conf file
    ltree_op = create_label_trees_from_tree_definitions (label_hierarchy_file)
    #print ltree_op
    # Display the label tree list
    for ltree_each in ltree_op: 
        #print "\n#Label Tree for:", ltree_each['label_tree']['name']
        print (ltree_each)

    # Create the Datalog messages given the label tree hierarchy conf file
    #create_datalog_policies (label_hierarchy_file)
