"""
Module to handle AWS Volumes
"""
import logging
from pcof import msg
from pcof import print_table
from Aws import Aws_ec2_volume
from Aws import query_aws
from Aws import initialize_boto3_session


log = logging.getLogger(__name__)


##############################################################################
# List volumes
##############################################################################
def cmd_list_volumes(args):
    log.info("params: %s", args)

    ec2 = initialize_boto3_session(args, 'ec2')

    # check if filter was specified
    filter_name = args.filter[0] if args.filter else ""
    filter_value = args.filter[1] if args.filter else ""

    resource = 'volumes'
    # get resources id
    volumes_id = query_aws(ec2,
                           resource_type=resource,
                           filter_name=filter_name,
                           filter_value=filter_value)
    if not volumes_id:
        msg("red", "Error: No volumes found", 1)

    # instantiate all ec2 volumes returned in the query
    volumes = [Aws_ec2_volume(ec2, 'Volume', i_id) for i_id in volumes_id]

    if args.detail:
        for volume in volumes:
            volume.show_metadata()

    else:
        header = ['VolumeId', 'VolumeType', 'State', 'AvailabilityZone',
                  'Size', 'CreateTime', 'InstanceId', 'Device',
                  'DeleteOnTermination']
        rows = list()
        for volume in volumes:
            row = list()
            for attr in header:
                row.append((getattr(volume, attr.lower())()))
            rows.append(row)

        align_right = ['Size']
        sortby = args.sortby if args.sortby else "InstanceId"
        print_table(header, rows, sortby=sortby, alignr=align_right)

# vim: ts=4
