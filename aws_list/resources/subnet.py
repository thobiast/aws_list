"""
Module to handle subnets
"""
import logging
from pcof import msg
from pcof import print_table
from Aws import Aws_ec2_subnet
from Aws import query_aws
from Aws import initialize_boto3_session


log = logging.getLogger(__name__)


##############################################################################
# List Subnets
##############################################################################
def cmd_list_subnets(args):
    log.info("params: %s", args)

    ec2 = initialize_boto3_session(args, 'ec2')

    # check if filter was specified
    filter_name = args.filter[0] if args.filter else ""
    filter_value = args.filter[1] if args.filter else ""

    resource = 'subnets'
    # get resources id
    subnets_id = query_aws(ec2,
                           resource_type=resource,
                           filter_name=filter_name,
                           filter_value=filter_value)
    if not subnets_id:
        msg("red", "Error: No subnet found", 1)

    # instantiate all ec2 subnets returned in the query
    subnets = [Aws_ec2_subnet(ec2, 'Subnet', i_id) for i_id in subnets_id]

    if args.detail:
        for subnet in subnets:
            subnet.show_metadata()
    else:
        header = ['SubnetId', 'Tag_Name', 'VpcId', 'CidrBlock',
                  'AvailableIpAddressCount', 'AvailabilityZone',
                  'DefaultForAz', 'State']
        rows = list()
        for subnet in subnets:
            row = list()
            for attr in header:
                row.append((getattr(subnet, attr.lower())()))
            rows.append(row)
        sortby = args.sortby if args.sortby else "SubnetId"
        align_left = ['CidrBlock', 'Tag_Name']
        print_table(header, rows, sortby=sortby, alignl=align_left)

# vim: ts=4
