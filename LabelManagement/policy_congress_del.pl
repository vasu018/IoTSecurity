#!/usr/bin/perl -w


print "## Deleting policy rules: \n";

my @list_policy_ids = `openstack congress policy rule list PGAClassification | grep -i "ID:"`;

foreach $policy (@list_policy_ids) {
    if ($policy =~m/(.*)ID: (.*)/) {
        my $policy_id = $2;
        chomp ($policy_id);
        print "# Deleting POlicy with ID: $policy_id\n";
        my $result = `openstack congress policy rule delete PGAClassification $policy_id`;
        print $result
    }
}

@list_policy_ids = `openstack congress policy rule list PGAClassification | grep -i "ID:"`;

foreach $policy (@list_policy_ids) {
    if ($policy =~m/(.*)ID: (.*)/) {
        my $policy_id = $2;
        chomp ($policy_id);
        print "# Deleting POlicy with ID: $policy_id\n";
        my $result = `openstack congress policy rule delete PGAClassification $policy_id`;
        print $result
    }
}

print "Creating the PGAClassification classifier";
my $result_create = `openstack congress policy create PGAClassification`;

print $result_create;

exit (0);
