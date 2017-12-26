#!/usr/bin/perl -w

print "## openstack congress policy row list PGAClassification users\n";
my $ret_users = `openstack congress policy row list PGAClassification user`;
print $ret_users;

print "## openstack congress policy row list PGAClassification tenants\n";
my $ret_tenants = `openstack congress policy row list PGAClassification tenant`;
print $ret_tenants;

#print "## openstack congress policy row list PGAClassification users_tenants_map\n";
#my $ret_u_t = `openstack congress policy row list PGAClassification users_tenants_map`;
#print $ret_u_t;

print "## openstack congress policy row list PGAClassification applications\n";
my $ret_apps = `openstack congress policy row list PGAClassification application`;
print $ret_apps;

print "## openstack congress policy row list PGAClassification availability_zones\n";
my $ret_azs = `openstack congress policy row list PGAClassification availability_zone`;
print $ret_azs;

print "## openstack congress policy row list PGAClassification hosts\n";
my $ret_hosts = `openstack congress policy row list PGAClassification host`;
print "$ret_hosts";

#print "## openstack congress policy row list PGAClassification aggregates\n";
#my $ret_agg = `openstack congress policy row list PGAClassification aggregates`;
#print "$ret_agg";


print "## openstack congress policy row list PGAClassification environments\n";
my $ret_envs = `openstack congress policy row list PGAClassification environment`;
print "$ret_envs";


