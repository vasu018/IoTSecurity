#!/usr/bin/python
from sympy import *
import re
from congressclient.common import utils
from congressclient.v1 import client
import keystoneclient
import pprint
#import label_initialization

# Global Configuration files
policy_conf_file = "/etc/neutron/label_policies.conf"
label_definition_file = "/etc/neutron/label_definition.conf"
label_tree_definition_file = "/etc/neutron/label_hierarchy.conf"
label_maps_conf_file = "/etc/neutron/label_maps.conf"


# ********************************************************
#
# Subroutines for Label Composition & Datalog formulation
#
# Description: Accepts the policies from the policies file and 
# generates the equivalent Datalog policies to be pushed to the 
# congress policy engine.
#
# ********************************************************

#
# Accepts the policy from the file and converts it to datalog format
# Input: one policy at at time
#
def frame_datalog_policy (policy_name_t, policy):
    policy_entities = re.split('&|\|', policy)
    symbols = []
    symbols = re.findall (r'[&|]', policy)

    c_policy = ''
    policy_head_params = ''
    for p_entity in range (len(policy_entities)):
        policy_term = policy_entities[p_entity]
        policy_term = policy_term.strip()
        label_details = re.split("[:]", policy_term)
        label_name = label_details[0]
        label_name = label_name.strip()
        head_param = label_name + "_name"
        if p_entity == 0:
            c_policy = c_policy + frame_congress_policy (policy_term)
            policy_head_params = policy_head_params + head_param
        else:
            if (symbols[p_entity - 1] == '&'):
                symbol = ' , '
            c_policy = c_policy + symbol + frame_congress_policy (policy_term)
            policy_head_params = policy_head_params + ", " + head_param 

    #[TODO]: Vasu add the host and VM attached to the policy
    #c_policy should be added with the host and the vm details
    #print c_policy
    c_policy = attach_vms_to_tenants (c_policy)

    policy_head_params = policy_head_params + ", time_t" 
    c_policy = c_policy.strip()
    c_policy = c_policy.lstrip(",")
    c_policy = c_policy.strip()
    c_policy_head = policy_name_t + "(" + policy_head_params+ ")"+ ":- " 
    c_policy = c_policy_head + c_policy + ", now(time_t)"
    #[DEBUG]: For outputting the datalog policy
    print "\n", c_policy
    return c_policy 

def attach_vms_to_tenants (c_policy_t):
    policy = c_policy_t

    policy_congress = policy + ", (nova:servers(id=id, vm=vm)"
    return c_policy_t


#
# Digest the policy file for extracting the actives rules
#
def digest_policies (policy_file):
    policy_tables_file = open(policy_file, 'r')
    policy_table_rows = policy_tables_file.readlines()
    policy_tables_file.closed
    return policy_table_rows


#
# Digest the label maps file and store it in the python dict
#
def digest_label_maps (labels_map_file):
    lmap_file = open(labels_map_file, 'r')
    label_maps = lmap_file.readlines()
    lmap_file.closed
    label_maps_dict = {} 
    datasource_name = ''
    for label in label_maps:
        if re.search ("^#", label):
            continue

        # Remove extra spaces and lines
        spacePattern = re.compile(r'\s+')
        label = re.sub(spacePattern, ' ', label)
        label = label.strip()
        if (label):
            start_endPattern = "^\[\w+\]"
            start_end_pattern_t = re.compile(start_endPattern, re.IGNORECASE)
            if (re.match(start_end_pattern_t, label)):
                ds_pattern = re.compile("^\[(.*)\]", re.IGNORECASE)
                
                datasource_name = ds_pattern.search(label).group(1)

                datasource_name.strip()
            else: 
                label = label.replace(",", "")
                label = label.replace("'", "")
                label_vals = re.split("=", label)
                
                label_name =  label_vals[0]            
                label_name = label_name.strip()
                
                label_ds_dsname = label_vals[1]
                label_ds_dsname = label_ds_dsname.strip()
               
                table_vals = re.split(":", label_ds_dsname)
                table_name = table_vals[0]
                table_name = table_name.strip()
                
                table_param = table_vals[1]
                table_param = table_param.strip()

                label_maps_dict[label_name] = {} 
                label_maps_dict[label_name]['table_name'] = table_name 
                label_maps_dict[label_name]['table_param'] = table_param
                label_maps_dict[label_name]['ds_name'] = datasource_name

    return label_maps_dict 


#
# Process the datalog format policy to congress compatible policy
#
def frame_congress_policy (policy_term_gen):
    #print "policy_term_gen ====> ", policy_term_gen
    policy_congress = ''
    policy_entities = re.split("[:]", policy_term_gen)
    label_name = policy_entities[0]
    label_name = label_name.strip()

    datasource_name = get_datasource (label_name)
    table_name = get_table_name (label_name)
    head_param = get_table_param (label_name)
    label_value = policy_entities[1]
    label_value = label_value.strip()

    head_param_value = label_name + "_name" 

    # Frame the congress policy
    if table_name == "tenants":
        #print "Table name is : tenants"
        policy_congress = datasource_name + ":" + table_name +"(" + head_param + "=" + head_param_value + ", id=id" + ")" + ", equal (" + head_param_value + "," + "\"" + label_value + "\")"
    #elif table_name == "availability_zones":
    #    pass
    #elif table_name == "hosts":
    #    pass
    else:
        policy_congress = datasource_name + ":" + table_name +"(" + head_param + "=" + head_param_value + ")" + ", equal (" + head_param_value + "," + "\"" + label_value + "\")"
    #[DEBUG]: Print the congress policy
    #print "policy_congress ===>", policy_congress 
    return policy_congress


#
# Get the datasource for the given policy entity
#
def get_datasource (policy_e):
    datasource = label_maps_all[policy_e]['ds_name']
    return datasource


#
# Get the datasource for the given policy entity
#
def get_table_name (policy_e):
    table_name = label_maps_all[policy_e]['table_name']
    return table_name


#
# Get the datasource for the given policy entity
#
def get_table_param (policy_e):
    table_param = label_maps_all[policy_e]['table_param']
    return table_param


#
# Create the policy rule in congress server using the congress client 
#[TODO] Duplicate code: Import from the label_initialization
#
def configure_datalog_to_congress (classifier_name, datalog_msg_t):

    policy_rule = {}
    policy_rule['rule'] = datalog_msg_t
    result_pcreate = congressclient.create_policy_rule (classifier_name, policy_rule)
    return result_pcreate

#
# Create a new label rule classifier, as we wanted to keep these rules 
# separate from the 'classification' rules created using the congress
# Command.
#[TODO] Duplicate code: Import from the label_initialization 
#
def create_LTreeClassifier (classifier_name_t):

    # Create the Congress policy classifier for policies
    policy_name_t = {}
    classifier_name_t = classifier_name_t.strip()
    policy_name_t['name'] = classifier_name_t
    policy_already_exists = 0

    congressclient = _get_congress_client()
    result_plist = congressclient.list_policy ()
    for policy in result_plist['results']:
        if policy['name'] == policy_name_t['name']:
            policy_name_t['id'] =  policy['id']
            policy_already_exists = 1
        
    if policy_already_exists == 1:
        result_delete = congressclient.delete_policy (policy_name_t['id'])
        result_pcreate = congressclient.create_policy (policy_name_t)
        return 1
    elif policy_already_exists == 0:
        result_pcreate = congressclient.create_policy (policy_name_t)
        print result_pcreate
        return 0
    else:
        return -1

#
# Create the congress client Instance
#[TODO] Also import from label_initialization
def _get_congress_client ():
    auth_url='http://16.111.37.119:5000/v2.0'
    auth = keystoneclient.auth.identity.v2.Password(
    auth_url="http://16.111.37.119:5000/v2.0", username="admin",
                password="ccdemo11", tenant_name="admin")
    session = keystoneclient.session.Session(auth=auth)

    return client.Client(session=session,
            auth=None,
            interface='publicURL',
            service_type='policy',
            region_name='RegionOne')


#
# Translate the DNF format to datalog policies and then to congress rules
#
def dnf_to_datalog_to_congress( policy_norm_sym_t, policy_name):

    policies_normalized_t = re.split("\|", policy_norm_sym_t)
    cong_policies = []
    for policy in policies_normalized_t:
        policy = policy.strip()
        if policy:
            policy = policy.replace("(", "") 
            policy = policy.replace(")", "")
            cong_policy = frame_datalog_policy (policy_name, policy)
        cong_policies.append(cong_policy)
    return cong_policies


#
# Policies logical to DNF Conversion
#
def disjunctive_normalize (norm_policies_t):
    norm_policies_expr = sympify(norm_policies_t)
    distjunct_norm_policies = to_dnf(norm_policies_expr)
    return distjunct_norm_policies


#
# Normalize the policies and translate the policies to DNF Format
#
def normalize_policies_to_DNF (policies_before_translate_t):
    
    policies_after_translate = [] 
    for policy_t in policies_before_translate_t:
        policy_t = policy_t.strip()
        policy_t = policy_t.replace(":", "__colan__") 
        
        # Policy expression is translated to DNF
        normalized_policy = disjunctive_normalize(policy_t)
        policies_after_translate.append(normalized_policy)

    return policies_after_translate


#
# Process to translate the And/Or form to &/| forms
#
def translate_AndOr_to_Symbols ( normalized_policies_DNF_t):
    policies_symbol_format = []
    for dnf_policy in normalized_policies_DNF_t:
        entities = re.split('And', str(dnf_policy))
        policy_entry_sym = ''
        for num, entry in enumerate(entities):
            entry = entry.strip()
            if (num == 0 and re.match(r"Or\(", entry) ):
                entry = "("
            else :
                entry = re.sub(r"\),", " )| ", entry)
                # Replace back __colan__ to ':'
                entry = entry.replace(",", " & ") 
                entry = entry.replace("__colan__", ":") 
            policy_entry_sym = policy_entry_sym + entry
        policies_symbol_format.append(policy_entry_sym)
    return policies_symbol_format
    

#
# Main Program:
#
if __name__ == "__main__":

    print ("****************************************")
    print ("*\t Policy Composition Engine !!! *")
    print ("****************************************")

#[STEP1]: Digest the label maps and policies files

    # Digest the label maps in the label_maps.conf file
    label_maps_all = {}
    label_maps_all = digest_label_maps(label_maps_conf_file)
    #[DEBUG]:
    #print label_maps_all


    # Digest the user specified policies in the policy file
    policies_all = []
    policies_all = digest_policies(policy_conf_file)


    # Access the policies from the conf file
    active_policies = [] 
    for policy in policies_all:
        if not re.search ("^#", policy):
            policy = policy.strip()
            if policy:
                active_policies.append(policy)


    #[DEBUG]: Active policies for processing  
    print ("\n# Active policies for processing:")
    for policy_t in active_policies:
        print policy_t


#[STEP2]: Translate the active rules to DNF -> Datalog -> Congress rules

    # Translation: Normal boolean predicate -> DNF form
    policies_dnf_format = normalize_policies_to_DNF (active_policies)
    print policies_dnf_format

    #[DEBUG]: Normalized policies in DNF format
    print "\n# Policies Normalization ..."
    for pol_d in policies_dnf_format:
        print pol_d
    
    # Translation: DNF format -> Symbol format again
    policies_symbol_format = translate_AndOr_to_Symbols (policies_dnf_format)

    #[DEBUG]: Transalted policies in the symbol format
    print "\n# Translated the policies to symbol format ..."
    #for pol_s in policies_symbol_format:
    #    print pol_s
    
    # Policies Translation to datalog policies
    print "\n# DNF to Datalog POlicies conversion .. ...."
    congress_policies = []
    for index, policy_sym in enumerate(policies_symbol_format):
        #print index, policy_sym
        #policy_details = policy_sym.split(":", 1)
        #policy = policy_details[1]
        #policy_name  = policy_details[0]
        #print index, policy_sym, policy_name
        policy_name = "Label_Policy"
        policy_name = policy_name.strip()
        policy_name = policy_name + "_" + str(index+1)
        datalog_policy = dnf_to_datalog_to_congress(policy_sym, policy_name)
        #[DEBUG]: To display the datalog messages
        #print "\n", datalog_policy
        congress_policies.append(datalog_policy)


#[STEP3]: Configure the congress rules using congress client on to server

    # Congress client:
    congressclient = _get_congress_client()

    # Create separate classifier for configuring rules 
    classifier_name = "label_classification"
    status_ret = create_LTreeClassifier(classifier_name)
    if (status_ret == 1):
        print "\n#" + classifier_name + ": classifier already exists !!!"
    elif (status_ret ==0):
        print "\n#" + classifier_name + ": classifier created successfully !!!"
    else:
        print "\n# Failed to create the " + classifier_name + " classifier"
        exit (1)


    # Configure the rules on to congress server 
    print "Configuring datalog policies in congress ..."
    for congress_rules in congress_policies:
        for c_rule in congress_rules:
            #[DEBUG]: Print the congress rules 
            #print "\n", c_rule
            configure_datalog_to_congress(classifier_name, c_rule)

