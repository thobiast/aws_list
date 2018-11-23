"""
Module to handle AWS AMI (Amazon Machine Images)
"""
import logging
import botocore
from pcof import msg
from Aws import Aws_ec2_ami
from Aws import initialize_boto3_session


log = logging.getLogger(__name__)


##############################################################################
# Show details of an AMI
##############################################################################
def cmd_show_ami_detail(args):
    log.info("params: %s", args)

    # Configure boto3 ec2 resource
    ec2 = initialize_boto3_session(args, 'ec2')

    try:
        ami = Aws_ec2_ami(ec2, 'Image', args.ami_id)
    except botocore.exceptions.ClientError as error:
        msg("red", str(error), 1)
    ami.show_metadata()

# vim: ts=4
