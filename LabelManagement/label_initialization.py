#!/usr/bin/python2.7
from congressclient.common import utils
from congressclient.v1 import client
import keystoneclient
import re


#
# Create the Label Tree classifier - "PGAClassifier". 
# Note: We could change the name to LabelClassifer
#
def create_LTreeClassifier (classifier_name_t):

    # Create the Congress policy classifier for Label tree policies
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
# Create datalogs for creating the Label trees 
# using congress policy engine 
#
def initialize (label_definitions_file_t):
  
    # Create the classifier
    classifier_name = "PGAClassification"
    status_ret = create_LTreeClassifier (classifier_name)
    if (status_ret == 1):
        print "\n#" + classifier_name + ": classifier already exists !!!"
    elif (status_ret ==0):
        print "\n#" + classifier_name + ": classifier created successfully !!!"
    else:
        print "\n# Failed to create the " + classifier_name + " classifier"
        return "FAIL"

    # Read label defintions for building the datalogs for label trees 
    ldefs_file_handle = open(label_definitions_file_t, 'r')
    ldef_file_contents = ldefs_file_handle.read()
    ldefs_file_handle.closed
  
    newLinePattern = re.compile(r'\n')
    label_file_data_t1 = re.sub(newLinePattern, ';', ldef_file_contents)

    spacePattern = re.compile(r'\s+')
    label_file_data_t2 = re.sub(spacePattern, ' ', label_file_data_t1)

    label_definitions_t3 = re.findall('\{.*?\}', label_file_data_t2)

    label_definitions = []
    for label_definition in label_definitions_t3:
        label_definition = label_definition.rstrip("}")
        label_definition = label_definition.rstrip(",")
        label_definition = label_definition.rstrip(";")
        label_definition = label_definition.lstrip("{")
        label_definition = label_definition.lstrip(";")
        label_definitions.append(label_definition)

    label_tree_definitions_file = "/etc/neutron/label_hierarchy.conf"
    ltreedefs_file = open(label_tree_definitions_file, 'r')
    ltreedef_file_contents = ltreedefs_file.readlines()
    ltreedefs_file.closed
    for ltreedef in ltreedef_file_contents:
        datalog_msg = ''
        labels = ''
        datalog_head_name = ''
        # Extracting label tree defs for the label tree construction 
        if not re.search ("^#", ltreedef):
            ldef_vals = re.split("@", ltreedef) 
            if (ldef_vals[0]):
                datalog_head_name = ldef_vals[0]
                datalog_head_name = datalog_head_name.strip()
            if (ldef_vals[1]):
                labels = re.split(",", ldef_vals[1]) 
            else: 
                print 'Error: Improper Labl defintion specification'
            
            datalog_head_name = datalog_head_name.strip()
            #print "datalog_head_name:", datalog_head_name
            if (len(labels) > 1):
                for index, label in enumerate(labels):
                    #print index, label
                    if index != 0:
                        datalog_head_name = label
                        datalog_head_name = datalog_head_name.strip()
                    label = label.strip()
                    ldef_contents = ''
                    label_pattern = 'NAME' + '\s*' + ':' + '\s*' + label 
                    label_pattern_t = re.compile(label_pattern, re.IGNORECASE)
                    # For identifying the end of label definition
                    match_flag = 0
                    for label_definition in label_definitions:
                        #label_definition = label_definition.lower()
                        if re.search (label_pattern_t, label_definition.lower()):
                            ldef_contents = label_definition
                            match_flag = 1
                    datalog_msg = transform_label_to_datalog(datalog_head_name, label , ldef_contents)
                    #print datalog_head_name, label , ldef_contents
                    configure_datalog_to_congress(classifier_name, datalog_msg)
            else:
                label = labels[0]
                label = label.strip()
                ldef_contents = ''
                label_pattern = 'NAME' + '\s*' + ':' + '\s*' + label 
                label_pattern_t = re.compile(label_pattern, re.IGNORECASE)

                # For identifying the end of label definition
                match_flag = 0
                for label_definition in label_definitions:
                    #label_definition = label_definition.lower()
                    if re.search (label_pattern_t, label_definition.lower()):
                        ldef_contents = label_definition
                        match_flag = 1
                if match_flag == 0:
                    continue
                datalog_msg = transform_label_to_datalog(datalog_head_name, label , ldef_contents)
                #print datalog_head_name, label , ldef_contents
                configure_datalog_to_congress(classifier_name, datalog_msg)

    return "SUCCESS"

#
# Create datalog policy rule 
#
def configure_datalog_to_congress (classifier_name, datalog_msg_t):

    #classifier_name = 'PGAClassification'
    policy_rule = {}
    policy_rule['rule'] = datalog_msg_t
    result_pcreate = congressclient.create_policy_rule (classifier_name, policy_rule)


#
# Transform the gievn label name in to the datalog message
#
def transform_label_to_datalog (datalog_head_name_t, label, label_contents_t):
    #print "\n"
    #print datalog_head_name_t, label 

    start_flag = 0
    end_flag = 0
    condition_flag = 0
    ref_flag = 0
    dtables_flag = 0
    parent_name_flag = 0
    label_details = {}
    datalog_policy = ""
    datalog_table_name = label 

    label_details[label] = {} 
    label_params = re.split(";", label_contents_t)
    for label_param in label_params:

        label_param = label_param.replace(" :", ":")
        #label_param = label_param.lower()
        #print label_param
        label_param = label_param.rstrip(";")
        label_param = label_param.rstrip(",")

        if re.search("name:", label_param.lower()):
            name_exp = re.compile("name:(.*)$", re.IGNORECASE)
            name = name_exp.search(label_param).group(1)
            name.strip()
            spacePattern = re.compile(r'\s+')
            name = re.sub(spacePattern, '', name)
            #if name:
            #label_details[label]['NAME'] = name
            label_details[label]['NAME'] = datalog_head_name_t
            #else:
            #    label_details[label]['NAME'] = ''

        elif re.search("key:", label_param.lower()):
            key_exp = re.compile("key:(.*)$", re.IGNORECASE)
            key = key_exp.search(label_param).group(1)
            key.strip()
            spacePattern = re.compile(r'\s+')
            key = re.sub(spacePattern, '', key)
            if key:
                label_details[label]['KEY'] = key 
            else:
                label_details[label]['KEY'] = ''
        
        elif re.search("ref:", label_param.lower()):
            ref_exp = re.compile("ref:(.*)$", re.IGNORECASE)
            refs = ref_exp.search(label_param).group(1)
            refs.strip()
            spacePattern = re.compile(r'\s+')
            refs = re.sub(spacePattern, '', refs)
            if refs:
                ref_flag = 1
                label_details[label]['REF'] = refs
            else:
                label_details[label]['REF'] = ''

        elif re.search("value:", label_param.lower()):
            val_exp = re.compile("value:(.*)$", re.IGNORECASE)
            vals = val_exp.search(label_param).group(1)
            vals.strip()
            spacePattern = re.compile(r'\s+')
            values = re.sub(spacePattern, '', vals)
            if values:
                label_details[label]['VALUE'] = values 
            else:
                label_details[label]['VALUE'] = ''

        elif re.search("data_source:", label_param.lower()):
            ldef = label_param.replace('"', "")
            dtable_exp = re.compile("data_source:(.*)$", re.IGNORECASE)
            data_sources = dtable_exp.search(label_param).group(1)
            data_sources.strip()
            spacePattern = re.compile(r'\s+')
            dsources = re.sub(spacePattern, '', data_sources)
            if dsources:
                label_details[label]['DATA_SOURCE'] = dsources 
            else:
                label_details[label]['DATA_SOURCE'] = ''

        elif re.search("condition:", label_param.lower()):
            condition_exp = re.compile("condition:(.*)$", re.IGNORECASE)
            conditions = condition_exp.search(label_param).group(1)
            conditions.strip()
            conditions = conditions.replace('""', "")
            spacePattern = re.compile(r'\s+')
            conditions = re.sub(spacePattern, '', conditions)
            if conditions:
                condition_flag = 1
                label_details[label]['CONDITION'] = conditions
            else:
                label_details[label]['CONDITION'] = ''
                
    #print label_details[label] 
    #[DEBUG]: print the label defintion details for debugging
    #print "\n# Extracting the details of Label:" + label
    #for key in label_details[label]:
    #    print key, label_details[label][key]


    # Process the label definition in python dict for datalog message
    if label_details[label]['DATA_SOURCE']:
        
        # Framing the Datalog policy head 
        datalog_head_params = ''
        if label_details[label]['VALUE']:
            head_params_t = label_details[label]['VALUE']
            head_params_list = re.split(",", head_params_t) 
            for head_param in head_params_list:
                head_param = head_param.strip()
                if head_param == "KEY":
                    datalog_head_params = "\"" + label_details[label]['KEY'] + "\""
                else:
                    datalog_head_params += "," +head_param
        datalog_head_params = datalog_head_params.lstrip(",")
        
        # Framing REF
        if ref_flag ==1:
            refs = label_details[label]['REF']
            refs = refs.rstrip(";")
            refs = refs.rstrip(",")
            datalog_refs = ''
            datalog_refs = refs
        else:
            label_details[label]['REF'] = ''


        # Framing Datalog policy body
        dtables = label_details[label]['DATA_SOURCE']
        dtables = dtables.rstrip(";")
        dtables = dtables.rstrip(",")
        datalog_body = ''
        datalog_body = dtables        

        # Introducing conditions into the datalog body
        if label_details[label]['CONDITION'] :
            #Handle the head params to suit the datalog
            head_params = re.split(",", datalog_head_params) 
            for param in head_params:
                if not re.search ("\"\w+\"" , param):
                    str_to_search = param 
                    str_to_replace = param + "=" + param
                    datalog_body = datalog_body.replace(str_to_search, str_to_replace)
            datalog_conditions = label_details[label]['CONDITION']
            symbol = ''
            conditions = re.split(",", datalog_conditions) 
            for condition in conditions:
                cond_splits = re.split('==|!=|<|>|=<|>=|', condition)
                lhs_condition = cond_splits[0]
                rhs_condition = cond_splits[1]
                
                if re.search ("!=", condition):
                    symbol = "!="
                elif re.search ("==", condition):
                    symbol = "="
                elif re.search ("<", condition):
                    symbol = "<"
                elif re.search (">", condition):
                    symbol = ">"
                elif re.search ("<=", condition):
                    symbol = "<="
                elif re.search (">=", condition):
                    symbol = ">="

                # Executing the conditions to the datalog head and body
                if re.search ("\"\w+\"" , rhs_condition):
                    if (symbol == "!="):
                        #[TODO]: Send this to a routine and output the modified string
                        str_to_search = "(" + lhs_condition + ","
                        str_to_replace = "(" + lhs_condition + "=" + lhs_condition + ","
                        datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                        str_to_search = "(" + lhs_condition + ")"
                        str_to_replace = "(" + lhs_condition + "=" + lhs_condition + ")"
                        datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                        str_to_search = "," + lhs_condition + ")"
                        str_to_replace = "," + lhs_condition + "=" + lhs_condition + ")"
                        datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                        str_to_search = "," + lhs_condition + ","
                        str_to_replace = "," + lhs_condition + "=" + lhs_condition + ","
                        datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                        datalog_body = datalog_body + ", not equal (" + lhs_condition + ", " + rhs_condition + ")"
                        
                    elif (symbol == "="):
                        str_to_search = lhs_condition
                        str_to_replace = lhs_condition + symbol + rhs_condition
                        datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                    else:
                        pass
                        #print lhs_condition, rhs_condition, symbol
                else:
                    name_attr = condition
                    name_attr = name_attr.replace('==', "_")

                    # Modify body params of datalog matching the condition
                    str_to_search = "(" + lhs_condition + ","
                    str_to_replace = "(" + lhs_condition + symbol + name_attr + ","
                    datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                    str_to_search = "(" + lhs_condition + ")"
                    str_to_replace = "(" + lhs_condition + symbol + name_attr + ")"
                    datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                    str_to_search = "," + lhs_condition + ")"
                    str_to_replace = "," + lhs_condition + symbol + name_attr + ")"
                    datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                    str_to_search = "," + lhs_condition + ","
                    str_to_replace = "," + lhs_condition + symbol + name_attr + ","
                    datalog_body = datalog_body.replace(str_to_search, str_to_replace)


                    str_to_search = "(" + rhs_condition + ","
                    str_to_replace = "(" + rhs_condition + symbol + name_attr + ","
                    datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                    str_to_search = "(" + rhs_condition + ")"
                    str_to_replace = "(" + rhs_condition + symbol + name_attr + ")"
                    datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                    str_to_search = "," + rhs_condition + ")"
                    str_to_replace = "," + rhs_condition + symbol + name_attr + ")"
                    datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                    str_to_search = "," + rhs_condition + ","
                    str_to_replace = "," + rhs_condition + symbol + name_attr + ","
                    datalog_body = datalog_body.replace(str_to_search, str_to_replace)
                    
                    # Modify head params of datalog matching the condition
                    str_to_search = "," + rhs_condition + ","
                    str_to_replace = "," + name_attr + ","
                    datalog_head_params = datalog_head_params.replace(str_to_search, str_to_replace)
                    
                    str_to_search = "," + rhs_condition
                    str_to_replace = "," + name_attr
                    datalog_head_params = datalog_head_params.replace(str_to_search, str_to_replace)
                    
                    str_to_search = rhs_condition + ","
                    str_to_replace = name_attr + ","
                    datalog_head_params = datalog_head_params.replace(str_to_search, str_to_replace)
                    
                    str_to_search = "," + lhs_condition + ","
                    str_to_replace = "," + name_attr + ","
                    datalog_head_params = datalog_head_params.replace(str_to_search, str_to_replace)
                    
                    str_to_search = "," + lhs_condition
                    str_to_replace = "," + name_attr
                    datalog_head_params = datalog_head_params.replace(str_to_search, str_to_replace)
                    
                    str_to_search = lhs_condition + ","
                    str_to_replace = name_attr + ","
                    datalog_head_params = datalog_head_params.replace(str_to_search, str_to_replace)

        else:
            # For labels without any conditions
            head_params = re.split(",", datalog_head_params) 
            for param in head_params:
                if not re.search ("\"\w+\"" , param):
                    str_to_search = param 
                    str_to_replace = param + "=" + param
                    datalog_body = datalog_body.replace(str_to_search, str_to_replace)

        # Add time to the datalog body
        datalog_body_with_time = datalog_body + ", now(time_t)"

        # Join the head and body of datalog 
        datalog_table_head = ''
        datalog_table_head = datalog_table_name + "(" + datalog_head_params + ", time_t" + ")" + ":- "
        datalog_policy = datalog_table_head + datalog_body_with_time

    print "\n"
    print datalog_policy

    return datalog_policy 

def transform_label_to_datalog_file (tree_name_t, label, label_file):
    # Digest the label defs file
    ldefs_file = open(label_file, 'r')
    ldef_file_contents = ldefs_file.readlines()
    ldefs_file.closed

    # Now Extract label defintion from the label def conf file
    print label
    
# Create the congress client Instance
def _get_congress_client ():
    #auth_url='%s/v2.0'%(cfg.CONF.keystone_authtoken.auth_uri)
    auth_url='http://16.111.37.119:5000/v2.0'
    auth = keystoneclient.auth.identity.v2.Password(
            auth_url="http://16.111.37.119:5000/v2.0", username="admin",
            password="ccdemo11", tenant_name="admin")
            #auth_url=auth_url,
            #username=cfg.CONF.congress_driver.congress_username,
            #password=cfg.CONF.congress_driver.congress_password,
            #tenant_name=cfg.CONF.congress_driver.congress_tenant)
    session = keystoneclient.session.Session(auth=auth)
    
    return client.Client(session=session,
            auth=None,
            interface='publicURL',
            service_type='policy',
            region_name='RegionOne')

#
# Main Program:
#
if __name__ == "__main__":

    # Create the Datalog messages given the label tree hierarchy conf file
    #create_datalog_policies (label_definition_file)
    
    congressclient = _get_congress_client()

    label_definition_file = "/etc/neutron/label_definition.conf" 
    initialize (label_definition_file)
                    
