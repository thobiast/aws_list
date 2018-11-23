#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to list Amazon Web Services (AWS) information
"""
import os
import sys
import argparse
import logging

# Get script path
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
# Add path where modules reside
sys.path.append(DIR_PATH + "/resources")

from s3 import cmd_list_s3
from regions import cmd_list_regions
from securitygroup import cmd_list_securitygroup
from subnet import cmd_list_subnets
from vpcs import cmd_list_vpcs
from volumes import cmd_list_volumes
from instances import cmd_num_inst
from instances import cmd_list_instances
from ami import cmd_show_ami_detail
from pcof import msg
from pcof import setup_logging


# If --debug, write log to filename
LOG_FILENAME = 'aws.log'

# Global log
log = ''

###########################################################################
# Parses the command line arguments
###########################################################################
def parse_parameters():
    # epilog message: Custom text after the help
    epilog = '''
    Example of use:
        %s instances
        %s instances -filter instance-id i-0b849030d3949ac16
        %s instances -filter tag:Name DNS
        %s instances -detail
    ''' % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
    # Create the argparse object and define global options
    parser = argparse.ArgumentParser(
        description='Script to list Amazon Web Services (AWS) information',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog)
    parser.add_argument('--debug', '-d',
                        action='store_true',
                        help='debug flag',
                        dest='debug')
    parser.add_argument('--profile', '-p',
                        help='Profile Name',
                        dest='profile')
    # Add subcommands options
    subparsers = parser.add_subparsers(title='Commands', dest='command')
    #############
    # Instances #
    #############
    listinst_parser = subparsers.add_parser('instances',
                                            help='List [EC2] Instances')
    listinst_parser.add_argument('-filter',
                                 nargs=2,
                                 metavar=('filter_name', 'value'),
                                 help='Filter instances')
    listinst_parser.add_argument('-sortby',
                                 dest='sortby',
                                 help='Sort table output by "column"')
    listinst_group = listinst_parser.add_mutually_exclusive_group()
    listinst_group.set_defaults(output='table')
    listinst_group.add_argument('-detail',
                                action='store_const',
                                const='detail',
                                dest='output',
                                help='Show instances metadata')
    listinst_group.add_argument('-tags',
                                action='store_const',
                                const='tags',
                                dest='output',
                                help='Show instances tags')
    listinst_group.add_argument('-ami',
                                action='store_const',
                                const='ami',
                                dest='output',
                                help='Show ami details')
    listinst_group.add_argument('-volumes',
                                action='store_const',
                                const='volume',
                                dest='output',
                                help='Show volumes details')
    listinst_group.add_argument('-secgroup',
                                action='store_const',
                                const='secgroup',
                                dest='output',
                                help='Show Security Groups details')
    listinst_group.add_argument('-names',
                                action='store_const',
                                const='names',
                                dest='output',
                                help='Show vpc and subnet names details')
    listinst_parser.set_defaults(func=cmd_list_instances)
    ###############
    # numinstance #
    ###############
    listnuminst_parser = subparsers.add_parser(
        'numinstances', help='List [EC2] Number of Instance')
    listnuminst_parser.add_argument('-filter',
                                    nargs=2,
                                    metavar=('filter_name', 'value'),
                                    help='Filter Instances')
    listnuminst_parser.add_argument('-sortby',
                                    dest='sortby',
                                    help='Sort table output by "column"')
    listnuminst_parser.add_argument(choices=['InstanceType',
                                             'ImageId',
                                             'VpcId',
                                             'AvailabilityZone',
                                             'SubnetId'],
                                    dest='pertype',
                                    help='Show Number of Instances per Type')
    listnuminst_parser.set_defaults(func=cmd_num_inst)
    #######
    # ami #
    #######
    listami_parser = subparsers.add_parser(
        'ami', help='List [EC2] AMI (Amazon Machine Images)')
    listami_parser.add_argument('ami_id',
                                help='AMI ID')
    listami_parser.set_defaults(func=cmd_show_ami_detail)
    ##################################
    # Regions and Availability Zones #
    ##################################
    listregion_parser = subparsers.add_parser(
        'regions', help='List [EC2] Regions and Availability Zones')
    listregion_parser.set_defaults(func=cmd_list_regions)
    ##################
    # security group #
    ##################
    listsecgroup_parser = subparsers.add_parser(
        'secgroups', help='List [EC2] Security Groups')
    listsecgroup_parser.add_argument('-sortby',
                                     dest='sortby',
                                     help='Sort table output by "column"')
    listsecgroup_parser.add_argument('-detail',
                                     action='store_true',
                                     help='Show security group details')
    listsecgroup_parser.add_argument('-rules',
                                     action='store_true',
                                     help='Show security group rules')
    listsecgroup_parser.add_argument('-filter',
                                     nargs=2,
                                     metavar=('filter_name', 'value'),
                                     help='Filter VPCs')
    listsecgroup_parser.set_defaults(func=cmd_list_securitygroup)
    ###########
    # subnets #
    ###########
    listsubnet_parser = subparsers.add_parser('subnets',
                                              help='List [EC2] Subnets')
    listsubnet_parser.add_argument('-sortby',
                                   dest='sortby',
                                   help='Sort table output by "column"')
    listsubnet_parser.add_argument('-detail',
                                   action='store_true',
                                   help='Show subnet metadata detail')
    listsubnet_parser.add_argument('-filter',
                                   nargs=2,
                                   metavar=('filter_name', 'value'),
                                   help='Filter VPCs')
    listsubnet_parser.set_defaults(func=cmd_list_subnets)
    ######
    # S3 #
    ######
    lists3_parser = subparsers.add_parser('s3',
                                          help='List [S3] Buckets')
    lists3_parser.add_argument('-size',
                               action='store_true',
                               help='Show S3 Bucket Size')
    lists3_parser.add_argument('-numobj',
                               action='store_true',
                               help='Show S3 Bucket Number of Objects')
    lists3_parser.set_defaults(func=cmd_list_s3)
    ###########
    # volumes #
    ###########
    listvolumes_parser = subparsers.add_parser('volumes',
                                               help='List [EC2] Volumes')
    listvolumes_parser.add_argument('-sortby',
                                    dest='sortby',
                                    help='Sort table output by "column"')
    listvolumes_parser.add_argument('-detail',
                                    action='store_true',
                                    help='Show volumes metadata')
    listvolumes_parser.add_argument('-filter',
                                    nargs=2,
                                    metavar=('filter_name', 'value'),
                                    help='Filter volumes')
    listvolumes_parser.set_defaults(func=cmd_list_volumes)
    #######
    # Vpc #
    #######
    listvpc_parser = subparsers.add_parser(
        'vpcs', help='List VPC (Amazon Virtual Private Cloud)')
    listvpc_parser.add_argument('-sortby',
                                dest='sortby',
                                help='Sort table output by "column"')
    listvpc_group = listvpc_parser.add_mutually_exclusive_group()
    listvpc_group.add_argument('-detail',
                               action='store_true',
                               help='Show vpcs detail')
    listvpc_parser.add_argument('-filter',
                                nargs=2,
                                metavar=('filter_name', 'value'),
                                help='Filter VPCs')
    listvpc_parser.set_defaults(func=cmd_list_vpcs)

    # If there is no parameter, print help
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


##############################################################################
# Main
##############################################################################
def main():
    global log

    # Parser the command line
    args = parse_parameters()

    # By default requests writes log messages to console.
    # The following line configure it to only write messages if is
    # at least warnings
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("boto3").setLevel(logging.ERROR)
    logging.getLogger("botocore").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    # Configure log if --debug
    log = setup_logging(LOG_FILENAME) if args.debug else logging

    log.debug('CMD line args: %s', vars(args))

    if not args.command:
        msg("red", "Erro: Use -h for help", 1)

    args.func(args)


##############################################################################
# Run from command line
##############################################################################
if __name__ == '__main__':
    main()

# vim: ts=4
