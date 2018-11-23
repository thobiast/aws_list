"""
Module to handle AWS VPC
"""
import logging
from pcof import msg
from pcof import print_table
from Aws import Aws_ec2_vpc
from Aws import query_aws
from Aws import initialize_boto3_session


log = logging.getLogger(__name__)


##############################################################################
# List VPC
##############################################################################
def cmd_list_vpcs(args):
    log.info("params: %s", args)

    ec2 = initialize_boto3_session(args, 'ec2')

    # check if filter was specified
    filter_name = args.filter[0] if args.filter else ""
    filter_value = args.filter[1] if args.filter else ""

    resource = 'vpcs'
    # get resources id
    vpcs_id = query_aws(ec2,
                        resource_type=resource,
                        filter_name=filter_name,
                        filter_value=filter_value)
    if not vpcs_id:
        msg("red", "Error: No vpcs found", 1)

    # instantiate all ec2 vpcs returned in the query
    vpcs = [Aws_ec2_vpc(ec2, 'Vpc', i_id) for i_id in vpcs_id]

    if args.detail:
        for vpc in vpcs:
            vpc.show_metadata()
    else:
        header = ['VpcId', 'Tag_Name', 'CidrBlock', 'DhcpOptionsId',
                  'IsDefault', 'InstanceTenancy', 'State']
        rows = list()
        for vpc in vpcs:
            row = list()
            for attr in header:
                row.append((getattr(vpc, attr.lower())()))
            rows.append(row)

        sortby = args.sortby if args.sortby else "VpcId"
        align_left = ['CidrBlock']
        print_table(header, rows, sortby=sortby, alignl=align_left)

# vim: ts=4
