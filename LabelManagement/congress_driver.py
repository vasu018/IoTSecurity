#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from neutron.common import log
from oslo_config import cfg
from oslo_log import log as logging

from congressclient.common import utils
from congressclient.v1 import client
import re
import keystoneclient

LOG = logging.getLogger(__name__)

congress_driver_opts = [
    cfg.StrOpt('auth_uri',
               default='http://localhost:5000/v2.0',
               help=_("Congress API server address to build label trees")),
    cfg.StrOpt('label_hierarchy',
               default='Ltree@TENANT:keystone@tenants',
               help=_("Label hierarchy list")),
    cfg.StrOpt('label_hierarchy_file',
               default='/etc/neutron/label_hierarchy.conf',
               help=_("Label hierarchy list")),
    cfg.StrOpt('label_definition_file',
               default='/etc/neutron/label_definition.conf',
               help=_("Label Defintions list")),
    cfg.StrOpt('congress_username',
               default='admin',
               help=_("Congress username")),
    cfg.StrOpt('congress_password',
               default='ccdemo11',
               help=_("Congress password")),
    cfg.StrOpt('congress_tenant',
               default='admin',
               help=_("Congress tenant name")),
]
cfg.CONF.register_opts(congress_driver_opts, "congress_driver")

class PolicyGraphCongressDriver(object):

    #
    # Create the Label Tree classifier - "PGAClassifier".
    # Note: We could change the name to LabelClassifer
    #
    def _create_LTreeClassifier (self, classifier_name_t):
        # Create the Congress policy classifier for Label tree policies
        policy_name_t = {}
        classifier_name_t = classifier_name_t.strip()
        policy_name_t['name'] = classifier_name_t
        policy_already_exists = 0

        congressclient = self._get_congress_client()
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
            #print result_pcreate
            return 0
        else:
            return -1


    #
    # Create datalogs for creating the Label trees
    # using congress policy engine
    #
    def _initialize_labels (self, label_definitions_file_t):

        # Create the classifier
        classifier_name = "PGAClassification"
        status_ret = self._create_LTreeClassifier (classifier_name)
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
  
        #print ldef_file_contents
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

        label_tree_definitions_file = cfg.CONF.congress_driver.label_hierarchy_file
        #label_tree_definitions_file = "/etc/neutron/label_hierarchy.conf"
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
                if (len(labels) > 1):
                    for index, label in enumerate(labels):
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
                        datalog_msg = self._transform_label_to_datalog(datalog_head_name, label , ldef_contents)
                        #print datalog_head_name, label , ldef_contents
                        self._configure_datalog_to_congress(classifier_name, datalog_msg)
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
                    datalog_msg = self._transform_label_to_datalog(datalog_head_name, label , ldef_contents)
                    #print datalog_head_name, label , ldef_contents
                    self._configure_datalog_to_congress(classifier_name, datalog_msg)
    
        return "SUCCESS"
       

    #
    # Create datalog policy rule
    #
    def _configure_datalog_to_congress (self, classifier_name, datalog_msg_t):

        #classifier_name = 'PGAClassification'
        policy_rule = {}
        policy_rule['rule'] = datalog_msg_t
        congressclient = self._get_congress_client()
        #result_pcreate = congressclient.create_policy_rule (classifier_name, policy_rule)


    #
    # Transform the gievn label name in to the datalog message
    #
    def _transform_label_to_datalog (self, datalog_head_name_t, label, label_contents_t):
        start_flag = 0
        end_flag = 0
        condition_flag = 0
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
            label_param = label_param.rstrip(";")
            label_param = label_param.rstrip(",")

            if re.search("name:", label_param.lower()):
                name_exp = re.compile("name:(.*)$", re.IGNORECASE)
                name = name_exp.search(label_param).group(1)
                name.strip()
                spacePattern = re.compile(r'\s+')
                name = re.sub(spacePattern, '', name)
                label_details[label]['NAME'] = datalog_head_name_t

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
                        #datalog_head_params = "\"" + label_details[label]['NAME'] + "\""
                        datalog_head_params = "\"" + label_details[label]['KEY'] + "\""
                    else:
                        datalog_head_params += "," +head_param
            datalog_head_params = datalog_head_params.lstrip(",")
        
            # Framing Datalog policy body
            dtables = label_details[label]['DATA_SOURCE']
            #print "DATASOURCES are:", dtables
            dtables = dtables.rstrip(";")
            dtables = dtables.rstrip(",")
            #dtables = re.split(",", dtables) 
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
                            print lhs_condition, rhs_condition, symbol
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
        print datalog_policy
        return datalog_policy

    @log.log
    def initialize(self):
        """
        Initialize congress driver
        TODO(joon): we need to add initialization of congress policies for building label trees
        :return:
        """
        print "###########################Initialize the labels ##################"
        label_definitions_file = cfg.CONF.congress_driver.label_definition_file
        self._initialize_labels(label_definitions_file)

    def _create_label_trees_from_file(self, context, hier_file):
        hierarchy_file = open(hier_file, 'r')
        label_tree_definitions = hierarchy_file.readlines()
        hierarchy_file.closed
        return self._create_label_trees_from_tree_definitions(context, label_tree_definitions)

    #
    # Digest the label tree defintions and create label trees
    #
    def _create_label_trees_from_tree_definitions(self, context, label_tree_definitions):
        ltrees = []

        for label_tree_definition in label_tree_definitions:
            if not re.search ("^#", label_tree_definition):

                # Constructing the actual tree definition
                tree_def_complete_all = label_tree_definition.split("@", 1)
                label_tree_definition = tree_def_complete_all[1]

                # Constructing the Label tree name
                vals = []
                #vals = re.split(":", tree_def_complete_all[0])
                #label_tree_name = vals[1]
                label_tree_name = tree_def_complete_all[0]
                label_tree_name = label_tree_name.strip()
                label_tree_definition = label_tree_definition.strip()

                entries = re.split(",", label_tree_definition)
                if (len(entries) > 1):
                    print ("\n#Extracting multi level label trees ")
                    ltree_t = self._process_for_multi_level_label_tree \
                                    (context, label_tree_definition, label_tree_name)
                    ltrees.append(ltree_t)
                else:
                    print ("\n#Extracting single level label trees ")
                    ltree_t = self._process_for_single_level_label_tree \
                                    (context, label_tree_definition, label_tree_name)
                    ltrees.append(ltree_t)
        return ltrees

    #
    # Process single-level tree defintion and create single-level label tree
    #
    def _process_for_single_level_label_tree(self, context, ltree_definition_t, label_tree_name_t):

        ltree = {}
        ltree_definition_t = ltree_definition_t.strip()
        table_name = ltree_definition_t
        policy_name = "PGAClassification"

        policy_rowlist = self._congress_policy_row_list (context, policy_name, table_name)
        if policy_rowlist:
            ltree = self._store_to_single_level_label_tree (policy_rowlist, label_tree_name_t)
        return ltree


    #
    # Format to the single level tree
    #
    @log.log
    def _store_to_single_level_label_tree(self, policy_data_rows_t, tree_name_t):

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
        return label_tree


    #
    # Process multi-level tree defintion and create multi-level label tree
    #
    def _process_for_multi_level_label_tree (self, context, ltree_definition_t, label_tree_name_t):
        ltree = {}
        ltree_definition_t = ltree_definition_t.strip()
        policy_rowlist = []
        hierarchy_entries = re.split(",", ltree_definition_t)
        for table_name in hierarchy_entries:
            table_name = table_name.strip()
            policy_name = "PGAClassification"

            rowlist = self._congress_policy_row_list (context, policy_name, table_name)
            for row_t in rowlist:
                policy_rowlist.append(row_t)
        if policy_rowlist:
            ltree = self._store_to_multi_level_label_tree (policy_rowlist, label_tree_name_t)
        return ltree


    #
    # Storing the multi level data into the Label trees
    #
    @log.log
    def _store_to_multi_level_label_tree(self, policy_data_rows_t, tree_name_t):

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

        # Add the child nodes to the Label tree
        for index, row in enumerate(policy_data_rows_t):
            print index, row
            node = {}
            node["nodeId"] = index + 2
            p_name = str(row[0]).lower()
            p_name = p_name.strip()
            p_nodeId = node_IDs[p_name]
            node["parent"] = p_nodeId

            # keep track of the node ID number for future reference
            node["name"] = str(row[1]).lower()
            node_name = node["name"]
            node_IDs[node_name] = node["nodeId"]

            node_list.append(node)

        label_tree["label_tree"]["nodeData"] = node_list
        return label_tree

    #
    # Get a congress client
    def _get_congress_client(self):
        auth_url='%s/v2.0'%(cfg.CONF.keystone_authtoken.auth_uri)
#        auth_url='%s/v2.0'%(cfg.CONF.congress_driver.auth_uri)
        auth = keystoneclient.auth.identity.v2.Password(
            auth_url=auth_url,
            username=cfg.CONF.congress_driver.congress_username,
            password=cfg.CONF.congress_driver.congress_password,
            tenant_name=cfg.CONF.congress_driver.congress_tenant)

        session = keystoneclient.session.Session(auth=auth)
        return client.Client(session=session,
                auth=None,
                interface='publicURL',
                service_type='policy',
                region_name='RegionOne')

    #
    # Subroutine to extract the contents of congress policy rows list
    #
    @log.log
    def _congress_policy_row_list (self, context, policy_name_t, table_name_t):

        row_list_data = []
        congressclient = self._get_congress_client()
        prow_result = congressclient.list_policy_rows (policy_name_t, table_name_t)
        for each_data in prow_result['results']:
            row_list_data.append(each_data['data'])
        return row_list_data

    @log.log
    def get_label_tree_precommit(self, context):
        """
        Get label tree list from congress client
        :param context:
        :return:
        """
        new_lt_list = self._create_label_trees_from_file(context, cfg.CONF.congress_driver.label_hierarchy_file)
        old_lt = context.current
        plugin = context._plugin

        # Create or update
        # 1. If a node in new_lt_list is not in the old_lt_list (compared by name), create a new label tree
        existed_node = None
        for lt in new_lt_list:
            if 'label_tree' in lt and lt['label_tree']['name'] == old_lt['name']:
                    existed_node = lt
                    break

        if existed_node:
            # update
            lt_node = {}
            lt_node['name'] = existed_node['label_tree']['name']
            lt_node['spec'] = existed_node
            lt_node['description'] = 'Label tree for %s'%(existed_node['label_tree']['name'])
            plugin.update_label_tree(context._plugin_context, old_lt['id'],
                                    {'label_tree': lt_node})
    @log.log
    def get_label_tree_postcommit(self, context):
        pass

    @log.log
    def get_label_trees_precommit(self, context):
        """
        Get a label tree from congress client
        :param context:
        :return:
        """
        new_lt_list = self._create_label_trees_from_file(context, cfg.CONF.congress_driver.label_hierarchy_file)
        #print "#########################Created label trees from file successfully ############"
        old_lt_list = context.current
        new_lt_list_map = {}
        old_lt_list_map = {}
        plugin = context._plugin

        for lt in old_lt_list:
            old_lt_list_map[lt['name']] = lt

        # Create or update
        # 1. If a node in new_lt_list is not in the old_lt_list (compared by name), create a new label tree
        # 2. Otherwise, update the label tree
        for lt in new_lt_list:
            if 'label_tree' in lt:
                # create hash map for new lt list
                new_lt_list_map[lt['label_tree']['name']] = lt
                existed_node = None
                if lt['label_tree']['name'] in old_lt_list_map:
                    existed_node = old_lt_list_map[lt['label_tree']['name']]
                if existed_node:
                    # update
                    existed_node['name'] = lt['label_tree']['name']
                    existed_node['spec'] = lt
                    existed_node['description'] = 'Label tree for %s'%(lt['label_tree']['name'])
                    plugin.update_label_tree(context._plugin_context, existed_node['id'],
                                        {'label_tree': existed_node})
                else:
                    # create
                    lt_node = {}
                    lt_node['name'] = lt['label_tree']['name']
                    lt_node['spec'] = lt
                    lt_node['description'] = 'Label tree for %s'%(lt['label_tree']['name'])
                    lt_node['editable'] = False
                    lt_node['type'] = 'epg'
                    plugin.create_label_tree(context._plugin_context, {'label_tree': lt_node})

        # Remove label trees which are not in the new_lt_list
        for old_lt in old_lt_list:
            if not old_lt['editable']:
                existed_node = None
                if old_lt['name'] in new_lt_list_map:
                    existed_node = new_lt_list_map[old_lt['name']]
                if not existed_node:
                    # remove the node because it is not in the new list
                    plugin.delete_label_tree(context._plugin_context, old_lt['id'])

    @log.log
    def create_label_tree_precommit(self, context):
        #TODO: Add to create a congress policy rule using the given label
        pass

    @log.log
    def update_label_tree_precommit(self, context):
        #TODO: Add to update a congress policy rule using the given label
        pass

    @log.log
    def create_input_policy_graph_precommit(self, context):
        pass

    @log.log
    def create_input_policy_graph_postcommit(self, context):
        pass

    @log.log
    def update_input_policy_graph_precommit(self, context):
        pass

    @log.log
    def update_input_policy_graph_postcommit(self, context):
        pass

    @log.log
    def delete_input_policy_graph_precommit(self, context):
        pass

    @log.log
    def delete_input_policy_graph_postcommit(self, context):
        pass

    @log.log
    def create_composed_policy_graph_precommit(self, context):
        pass

    @log.log
    def create_composed_policy_graph_postcommit(self, context):
        pass

    @log.log
    def update_composed_policy_graph_precommit(self, context):
        pass

    @log.log
    def update_composed_policy_graph_postcommit(self, context):
        pass

    @log.log
    def delete_composed_policy_graph_precommit(self, context):
        pass

    @log.log
    def delete_composed_policy_graph_postcommit(self, context):
        pass

    @log.log
    def create_deployed_policy_graph_precommit(self, context):
        pass

    @log.log
    def create_deployed_policy_graph_postcommit(self, context):
        pass

    @log.log
    def update_deployed_policy_graph_precommit(self, context):
        pass

    @log.log
    def update_deployed_policy_graph_postcommit(self, context):
        pass

    @log.log
    def delete_deployed_policy_graph_precommit(self, context):
        pass

    @log.log
    def delete_deployed_policy_graph_postcommit(self, context):
        pass

