#!/usr/bin/perl -w

# Clean the exiting rules and create them fresh
my $ret_del = `./policy_congress_del.pl`;
#print $ret_del;

#
# Tenants
#
my $tenants_ret = `openstack congress policy rule create PGAClassification 'tenant("tenant", tenant_name, time_t) :- keystone:tenants(name=tenant_name), now(time_t)'`;
print "$tenants_ret\n";

#
# Users
#
my $users_ret = `openstack congress policy rule create PGAClassification 'user("user", user_name, time_t) :- keystone:users(name=user_name), now(time_t)'`;
print "$users_ret\n";

#
# User Tenants mapping
#
my $tenants_users_ret = `openstack congress policy rule create PGAClassification 'users_tenants_map(user_name, tenant_name, tenant_id, time_t ) :- keystone:users(name=user_name, tenantId=tenant_id), keystone:tenants(name=tenant_name, id=tenant_id), now(time_t) '`;
print $tenants_users_ret;

#
# Applications List - Excluding Library
#
my $apps = `openstack congress policy rule create PGAClassification 'application("application", app_value, time_t) :- murano:objects(owner_id=owner_id, object_id=app_id, type=app_type), murano:properties(name="name", value=app_value, owner_id=app_id), now(time_t), not equal(app_type, "Library") '`;
print $apps;

#
# Locations tree 
#
#Commeting the region part of creation
#my $loc_reg = `openstack congress policy rule create PGAClassification 'regions("Locations", "RegionOne", time_t) :- nova:availability_zones(zoneName=az_name ), now(time_t)'`;
#print $loc_reg;

my $loc_az = `openstack congress policy rule create PGAClassification 'availability_zone("Location", az_name, time_t) :- nova:availability_zones(zoneName=az_name ), now(time_t)'`;
print $loc_az;

my $loc_hosts = `openstack congress policy rule create PGAClassification 'host(az_name, host_name, time_t) :- nova:availability_zones(zoneName=az_name ), nova:hosts(host_name=host_name, service="compute", zone=az_name), now(time_t)'`;
print $loc_hosts;

my $loc_agg = `openstack congress policy rule create PGAClassification 'aggregate(az_name, host_agg, time_t) :- nova:aggregates(name=host_agg, availability_zone=az_name), now(time_t)'`;
print $loc_agg;

#
# Environments List
#

my $envs = `openstack congress policy rule create PGAClassification 'environment ("Environment", env_name, time_t) :- murano:environments(name=env_name, tenant_id=tenant_id), keystone:tenants(id=tenant_id), now(time_t)'`;
print $envs;


#
# Aggregates to hosts list
#
# Need to enhance the congress nova driver for aggregates to hosts list
# 'nova aggregate-details Agg_vasu1'
#+----+-----------+-------------------+-------+----------------------------+
#| Id | Name      | Availability Zone | Hosts | Metadata                   |
#+----+-----------+-------------------+-------+----------------------------+
#| 7  | Agg_vasu1 | Zone14            |       | 'availability_zone=Zone14' |
#+----+-----------+-------------------+-------+----------------------------+




