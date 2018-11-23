"""
Module to handle AWS Security Groups
"""
import logging
import pprint
from pcof import msg
from pcof import print_table
from Aws import Aws_ec2_secgroup
from Aws import query_aws
from Aws import initialize_boto3_session


log = logging.getLogger(__name__)


##############################################################################
# List security groups
##############################################################################
def cmd_list_securitygroup(args):
    log.debug("params: %s", args)

    ec2 = initialize_boto3_session(args, 'ec2')

    # check if filter was specified
    filter_name = args.filter[0] if args.filter else ""
    filter_value = args.filter[1] if args.filter else ""

    resource = 'security_groups'
    # get resources id
    secgroups_id = query_aws(ec2,
                             resource_type=resource,
                             filter_name=filter_name,
                             filter_value=filter_value)
    if not secgroups_id:
        msg("red", "Error: No security group found", 1)

    # instantiate all ec2 security group returned in the query
    secgroups = [Aws_ec2_secgroup(ec2, 'SecurityGroup', i_id)
                 for i_id in secgroups_id]

    if args.detail:
        for secgroup in secgroups:
            secgroup.show_metadata()
        return
    elif args.rules:
        header = ['GroupId', 'VpcId', 'GroupName', 'InBound', 'OutBound']
    else:
        header = ['GroupId', 'VpcId', 'GroupName', 'Description']

    rows = list()
    for secgroup in secgroups:
        row = list()
        for attr in header:
            row.append((getattr(secgroup, attr.lower())()))
        rows.append(row)

    align_left = ['GroupName', 'Description', 'InBound', 'OutBound']
    sortby = args.sortby if args.sortby else "GroupId"
    print_table(header, rows, sortby=sortby, alignl=align_left, hrules="ALL")

# vim: ts=4
