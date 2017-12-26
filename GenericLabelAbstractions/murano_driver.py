## Copyright (c) 2015 Hewlett-Packard. All rights reserved.
#
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
#
import inspect
import os
import pprint
import keystoneclient.v2_0.client as ksclient
import muranoclient.client
from muranoclient.common.exceptions import HTTPException

from congress.datasources import datasource_driver
from congress.datasources import datasource_utils
from congress.datasources import murano_classes
from congress.openstack.common import log as logging
from congress.openstack.common import uuidutils
from congress.utils import value_to_congress

logger = logging.getLogger(__name__)

pp = pprint.PrettyPrinter(depth=6)

def d6service(name, keys, inbox, datapath, args):
    """This method is called by d6cage to create a dataservice instance."""
    return MuranoDriver(name, keys, inbox, datapath, args)


class MuranoDriver(datasource_driver.DataSourceDriver):
    OBJECTS = "objects"
    PARENT_TYPES = "parent_types"
    PROPERTIES = "properties"
    RELATIONSHIPS = "relationships"
    CONNECTED = "connected"
    STATES = "states"
    ENVIRONMENTS_LIST = "environments"
    UNUSED_PKG_PROPERTIES = ['id', 'owner_id', 'description']
    UNUSED_ENV_PROPERTIES = ['id', 'tenant_id']
    APPS_TYPE_PREFIXES = ['io.murano.apps', 'io.murano.databases']

    def __init__(self, name='', keys='', inbox=None, datapath=None, args=None):
        super(MuranoDriver, self).__init__(name, keys, inbox, datapath, args)
        self.creds = args
        logger.info("Credentials = %s" % self.creds)
        keystone = ksclient.Client(**self.creds)
        murano_endpoint = keystone.service_catalog.url_for(
            service_type='application_catalog',
            endpoint_type='publicURL')
        logger.debug("murano_endpoint = %s" % murano_endpoint)
        client_version = "1"
        self.murano_client = muranoclient.client.Client(
            client_version,
            endpoint=murano_endpoint,
            token=keystone.auth_token)
        logger.debug("Successfully created murano_client")
        self.initialized = True

    @staticmethod
    def get_datasource_info():
        result = {}
        result['id'] = 'murano'
        result['description'] = ('Datasource driver that interfaces with '
                                 'murano')
        result['config'] = datasource_utils.get_openstack_required_config()
        result['secret'] = ['password']
        return result

    def update_from_datasource(self):
        """Called when it is time to pull new data from this datasource.

        Sets self.state[tablename] = <set of tuples of strings/numbers>
        for every tablename exported by this datasource.
        """
        self.state[self.STATES] = set()
        self.state[self.OBJECTS] = set()
        self.state[self.PROPERTIES] = set()
        self.state[self.PARENT_TYPES] = set()
        self.state[self.RELATIONSHIPS] = set()
        self.state[self.CONNECTED] = set()

        # Workaround for 401 error issue
        try:
            # Moves _translate_packages above translate_services to
            # make use of properties table in translate_services
            logger.debug("Murano grabbing packages")
            packages = self.murano_client.packages.list()
            self._translate_packages(packages)
            logger.debug("Murano grabbing environments")
            environments = self.murano_client.environments.list()
            self._translate_environments(environments)
            #pp.pprint (environments)
            self._translate_services(environments)
            self._translate_deployments(environments)
            self._translate_connected()
        except HTTPException as e:
            if e.code == 401:
                logger.debug("Obtain keystone token again")
                keystone = ksclient.Client(**self.creds)
                self.murano_client.auth_token = keystone.auth_token
            else:
                raise e

    @classmethod
    def get_schema(cls):
        """Returns a dictionary of table schema.

        The dictionary mapping tablenames to the list of column names
        for that table. Both tablenames and columnnames are strings.
        """
        d = {}
        d[cls.OBJECTS] = ('object_id', 'owner_id', 'type')
        # parent_types include not only the type of object's immediate
        # parent but also all of its ancestors and its own type.  The
        # additional info helps writing better datalog rules.
        d[cls.PARENT_TYPES] = ('id', 'parent_type')
        d[cls.PROPERTIES] = ('owner_id', 'name', 'value')
        d[cls.RELATIONSHIPS] = ('source_id', 'target_id', 'name')
        d[cls.ENVIRONMENTS_LIST] = ('name', 'env_id', 'tenant_id', 'Created', 'Updated')
        d[cls.CONNECTED] = ('source_id', 'target_id')
        d[cls.STATES] = ('id', 'state')
        return d

    def _translate_environments(self, environments):
        """Translate the environments into tables.

        Assigns self.state[tablename] for all those TABLENAMEs
        generated from environments
        """
        logger.debug("_translate_environments: %s", environments)
        if not environments:
            return
        self.state[self.STATES] = set()
        if self.OBJECTS not in self.state:
            self.state[self.OBJECTS] = set()
        if self.PROPERTIES not in self.state:
            self.state[self.PROPERTIES] = set()
        if self.PARENT_TYPES not in self.state:
            self.state[self.PARENT_TYPES] = set()
        if self.RELATIONSHIPS not in self.state:
            self.state[self.RELATIONSHIPS] = set()
        if self.CONNECTED not in self.state:
            self.state[self.CONNECTED] = set()
        if self.ENVIRONMENTS_LIST not in self.state:
            self.state[self.ENVIRONMENTS_LIST] = set()

        env_type = 'io.murano.Environment'
        for env in environments:
            self.state[self.OBJECTS].add(
                (env.id, env.tenant_id, env_type))
            self.state[self.STATES].add((env.id, env.status))
            self.state[self.ENVIRONMENTS_LIST].add((env.name, env.id, env.tenant_id, env.created, env.updated))
            parent_types = self._get_parent_types(env_type)
            self._add_parent_types(env.id, parent_types)
            for key, value in env.to_dict().iteritems():
                if key in self.UNUSED_ENV_PROPERTIES:
                    continue
                self._add_properties(env.id, key, value)

    def _translate_services(self, environments):
        """Translate the environment services into tables.

        Assigns self.state[tablename] for all those TABLENAMEs
        generated from services
        """
        logger.debug("Murano grabbing environments services")
        if not environments:
            return
        for env in environments:
            services = self.murano_client.services.list(env.id)
            self._translate_environment_services(services, env.id)

    def _translate_environment_services(self, services, env_id):
        """Translate the environment services into tables.

        Assigns self.state[tablename] for all those TABLENAMEs
        generated from services
        """
        if not services:
            return
        for s in services:
            s_dict = s.to_dict()
            s_id = s_dict['?']['id']
            s_type = s_dict['?']['type']
            self.state[self.OBJECTS].add((s_id, env_id, s_type))
            for key, value in s_dict.iteritems():
                if key in ['instance', '?']:
                    continue
                self._add_properties(s_id, key, value)
                self._add_relationships(s_id, key, value)

            parent_types = self._get_parent_types(s_type)
            self._add_parent_types(s_id, parent_types)
            self._add_relationships(env_id, 'services', s_id)

            if 'instance' not in s_dict:
                continue
            # populate service instance
            si_dict = s.instance
            si_id = si_dict['?']['id']
            si_type = si_dict['?']['type']
            self.state[self.OBJECTS].add((si_id, s_id, si_type))

            for key, value in si_dict.iteritems():
                if key in ['?']:
                    continue
                self._add_properties(si_id, key, value)
                if key not in ['image']:
                    # there's no murano image object in the environment,
                    # therefore glance 'image' relationship is irrelevant
                    # at this point.
                    self._add_relationships(si_id, key, value)
            # There's a relationship between the service and instance
            self._add_relationships(s_id, 'instance', si_id)

            parent_types = self._get_parent_types(si_type)
            self._add_parent_types(si_id, parent_types)

    def _translate_deployments(self, environments):
        """Translate the environment deployments into tables.

        Assigns self.state[tablename] for all those TABLENAMEs
        generated from deployments
        """
        if not environments:
            return
        for env in environments:
            deployments = self.murano_client.deployments.list(env.id)
            self._translate_environment_deployments(deployments, env.id)

    def _translate_environment_deployments(self, deployments, env_id):
        """Translate the environment deployments into tables.

        Assigns self.state[tablename] for all those TABLENAMEs
        generated from deployments
        """
        if not deployments:
            return
        for d in deployments:
            if 'defaultNetworks' not in d.description:
                continue
            default_networks = d.description['defaultNetworks']
            net_id = None
            if 'environment' in default_networks:
                net_id = default_networks['environment']['?']['id']
                net_type = default_networks['environment']['?']['type']
                self.state[self.OBJECTS].add((net_id, env_id, net_type))

                parent_types = self._get_parent_types(net_type)
                self._add_parent_types(net_id, parent_types)

                for key, value in default_networks['environment'].iteritems():
                    if key in ['?']:
                        continue
                    self._add_properties(net_id, key, value)

            if not net_id:
                continue
            self._add_relationships(env_id, 'defaultNetworks', net_id)
            for key, value in default_networks.iteritems():
                if key in ['environment']:
                    # data from environment already populated
                    continue
                new_key = 'defaultNetworks.' + key
                self._add_properties(net_id, new_key, value)
            # services from deployment are not of interest because the same
            # info is obtained from services API

    def _translate_packages(self, packages):
        """Translate the packages into tables.

        Assigns self.state[tablename] for all those TABLENAMEs
        generated from packages/applications
        """
        # packages is a generator type
        if not packages:
	    return
        if self.OBJECTS not in self.state:
            self.state[self.OBJECTS] = set()
        if self.PROPERTIES not in self.state:
            self.state[self.PROPERTIES] = set()

        for pkg in packages:
            logger.debug("pkg=%s", pkg.to_dict())
            pkg_type = pkg.type
            if pkg.type == 'Application':
                pkg_type = 'io.murano.Application'
            self.state[self.OBJECTS].add((pkg.id, pkg.owner_id, pkg_type))

            for key, value in pkg.to_dict().iteritems():
                if key in self.UNUSED_PKG_PROPERTIES:
                    continue
                self._add_properties(pkg.id, key, value)

    def _add_properties(self, obj_id, key, value):
        """Add a set of (obj_id, key, value) to properties table.

        :param obj_id: uuid of object
        :param key: property name. For the case value is a list, the
        same key is used for multiple values.
        :param value: property value. If value is a dict, the nested
        properties will be mapped using dot notation.
        """
        if value is None or value == '':
            return
        if isinstance(value, dict):
            for k, v in value.iteritems():
                new_key = key + "." + k
                self._add_properties(obj_id, new_key, v)
        elif isinstance(value, list):
            if len(value) == 0:
                return
            for item in value:
                self.state[self.PROPERTIES].add(
                    (obj_id, key, value_to_congress(item)))
        else:
            self.state[self.PROPERTIES].add(
                (obj_id, key, value_to_congress(value)))

    def _add_relationships(self, obj_id, key, value):
        """Add a set of (obj_id, value, key) to relationships table.

        :param obj_id: source uuid
        :param key: relationship name
        :param value: target uuid
        """
        if (not isinstance(value, basestring) or
                not uuidutils.is_uuid_like(value)):
            return
        logger.debug("Relationship: source = %s, target = %s, rel_name = %s"
                     % (obj_id, value, key))
        self.state[self.RELATIONSHIPS].add((obj_id, value, key))

    def _transitive_closure(self):
        """Computes transitive closure on a directed graph.

        In other words computes reachability within the graph.
        E.g. {(1, 2), (2, 3)} -> {(1, 2), (2, 3), (1, 3)}
        (1, 3) was added because there is path from 1 to 3 in the graph.
        """
        closure = self.state[self.CONNECTED]
        while True:
            # Attempts to discover new transitive relations
            # by joining 2 subsequent relations/edges within the graph.
            new_relations = {(x, w) for x, y in closure
                             for q, w in closure if q == y}
            # Creates union with already discovered relations.
            closure_until_now = closure | new_relations
            # If no new relations were discovered in last cycle
            # the computation is finished.
            if closure_until_now == closure:
                self.state[self.CONNECTED] = closure
                break
            closure = closure_until_now

    def _add_connected(self, source_id, target_id):
        """Looks up the target_id in objects and add links to connected table.

        Adds sets of (source_id, target_id) to connected table along
        with its indirections.
        :param source_id: source uuid
        :param target_id: target uuid
        """
        for row in self.state[self.OBJECTS]:
            if row[1] == target_id:
                self.state[self.CONNECTED].add((row[1], row[0]))
                self.state[self.CONNECTED].add((source_id, row[0]))
        self.state[self.CONNECTED].add((source_id, target_id))

    def _translate_connected(self):
        """Translates relationships table into connected table."""
        for row in self.state[self.RELATIONSHIPS]:
            self._add_connected(row[0], row[1])
        self._transitive_closure()

    def _add_parent_types(self, obj_id, parent_types):
        """Add sets of (obj_id, parent_type) to parent_types table.

        :param obj_id: uuid of object
        :param parent_types: list of parent type string
        """
        if parent_types:
            for p_type in parent_types:
                self.state[self.PARENT_TYPES].add((obj_id, p_type))

    def _get_package_type(self, class_name):
        """Determine whether obj_type is an Application or Library.

        :param class_name: <string> service/application class name
            e.g. io.murano.apps.linux.Telnet.
        :return - package type (e.g. 'Application') if found.
            - None if no package type found.
        """
        pkg_type = None
        if self.PROPERTIES in self.state:
            idx_uuid = 0
            idx_value = 2
            uuid = None
            for row in self.state[self.PROPERTIES]:
                if 'class_definitions' in row and class_name in row:
                    uuid = row[idx_uuid]
                    break
            if uuid:
                for row in self.state[self.PROPERTIES]:
                    if 'type' in row and uuid == row[idx_uuid]:
                        pkg_type = row[idx_value]

        # If the package is removed after deployed, its properties
        #  are not known and so above search will fail. In that case
        #  let's check for class_name prefix as the last resort.
        if not pkg_type:
            for prefix in self.APPS_TYPE_PREFIXES:
                if prefix in class_name:
                    pkg_type = 'Application'
                    break
        return pkg_type

    def _get_parent_types(self, obj_type):
        """Get class types of all OBJ_TYPE's parents including itself.

        Look up the hierachy of OBJ_TYPE and return types of all its
        ancestor including its own type.
        :param obj_type: <string>
        """
        class_types = []
        p = lambda x: inspect.isclass(x)
        g = inspect.getmembers(murano_classes, p)
        for name, cls in g:
            logger.debug("%s: %s" % (name, cls))
            if (cls is murano_classes.IOMuranoApps and
                    self._get_package_type(obj_type) == 'Application'):
                cls.name = obj_type
            if 'get_parent_types' in dir(cls):
                class_types = cls.get_parent_types(obj_type)
                if class_types:
                    break
        return class_types
