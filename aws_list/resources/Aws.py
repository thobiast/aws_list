"""
Module with AWS EC2 class and functions
"""
import logging
import pprint
import boto3
import botocore
from pcof import msg


log = logging.getLogger(__name__)


##############################################################################
# Aws EC2 Class
##############################################################################
class Aws_ec2():
    """
    Base Aws_ec2 class
    Params:
        ec2            (obj): boto3 ec2 resource
        resource_type  (str): Aws resource type
        resource_id    (str): Aws resource id
    """
    available_types = ['Volume', 'Image', 'Instance', 'Vpc', 'Subnet',
                       'SecurityGroup', 'RouteTable', 'VpcPeeringConnection']

    def __init__(self, ec2, resource_type, resource_id):
        log.info("Creating Aws type: %s, id: %s", resource_type, resource_id)

        if resource_type not in self.available_types:
            msg("red", "Erro: Aws class: Resource type not found", 1)

        self.resource_type = resource_type
        self.resource_id = resource_id
        # fetch an attribute from an object
        # ec2.resource_type(resource_id)
        self.ec2 = getattr(ec2, self.resource_type)(self.resource_id)
        self.ec2.load()
        self.metadata = self.ec2.meta.__dict__['data']
        if not self.metadata:
            msg("red", "resource_type: " + resource_type)
            msg("red", "resource_id: " + resource_id)
            msg("red", "metadata not loaded", 1)
        log.debug("metadata: %s", pprint.pformat(self.metadata))

    def show_metadata(self):
        """
        Print all metadata information
        """
        log.info("Show details of: %s", self.resource_type)
        msg("blue", "##################################")
        msg("blue", "# ID: " + self.resource_id)
        msg("blue", "##################################")
        for key, value in self.metadata.items():
            msg("green", key + ": ", end='')
            pprint.pprint(value)
        print("")

    def tag_value(self, key):
        """
        Return tag value for a specific tag key

        Params:
            key    (str): metadata Tag key
        """
        log.info("key: %s", key)

        try:
            value = [tag['Value']
                     for tag in self.metadata['Tags'] if tag['Key'] == key]
        except KeyError:
            return [""][0]

        if value:
            return value[0]
        else:
            return [""][0]

    def all_tags_key(self):
        """
        Return a list with all tag keys
        """
        log.info("Looking for tag keys: id: %s", self.resource_id)

        all_keys = [tag['Key'] for tag in self.metadata['Tags']]

        log.debug("all_keys: %s", pprint.pformat(all_keys))
        return all_keys

    def tag_name(self):
        """
        Return Tag key "Name"
        """
        return self.tag_value("Name")

    def find_key(self, dict_obj, key):
        """
        Function to search in a dictionary for an specific key
        It supports nested dictionary
        Params:
            dict_obj    (obj): A list or a dictionary
            key         (str): dictionary key

        Return a list with values that matches the key
        """
        # List to store values
        results = list()

        # if dict_obj is a dictionary
        if isinstance(dict_obj, dict):
            for k, v in dict_obj.items():
                # if value is == key
                if k == key:
                    results.append(v)
                else:
                    # call function again, it can be a nested dict
                    results.extend(self.find_key(v, key))
        # If dict_obj is a list
        elif isinstance(dict_obj, list):
            # for each item, call again the function, as maybe there are
            # dict inside the list
            for item in dict_obj:
                results.extend(self.find_key(item, key))

        return results


##############################################################################
# Instance Aws EC2 Class
##############################################################################
class Aws_ec2_instance(Aws_ec2):
    """
    Aws ec2 class for Instance
    """

    def availabilityzone(self):
        return self.metadata['Placement']['AvailabilityZone']

    def instanceid(self):
        return self.resource_id

    def instancetype(self):
        return self.metadata['InstanceType']

    def instancestate(self):
        return self.metadata['State']['Name']

    def keyname(self):
        try:
            return self.metadata['KeyName']
        except KeyError:
            return ""

    def privateipaddress(self):
        try:
            return self.metadata['PrivateIpAddress']
        except KeyError:
            return ""

    def imageid(self):
        return self.metadata['ImageId']

    def vpcid(self):
        try:
            return self.metadata['VpcId']
        except KeyError:
            return ""

    def launchtime(self):
        return self.metadata['LaunchTime']

    def securitygroups(self):
        return self.metadata['SecurityGroups']

    def subnetid(self):
        try:
            return self.metadata['SubnetId']
        except KeyError:
            return ""

    def getvolumesids(self):
        return [x['Ebs']['VolumeId']
                for x in self.metadata['BlockDeviceMappings']]


##############################################################################
# AMI Aws EC2 Class
##############################################################################
class Aws_ec2_ami(Aws_ec2):
    """
    Aws ec2 class for AMI
    """

    def description(self):
        return self.metadata['Description']

    def creationdate(self):
        return self.metadata['CreationDate']

    def ownerid(self):
        return self.metadata['OwnerId']

    def imageowneralias(self):
        try:
            return self.metadata['ImageOwnerAlias']
        except KeyError:
            return ""

    def rootdevicetype(self):
        return self.metadata['RootDeviceType']

    def name(self):
        return self.metadata['Name']


##############################################################################
# Volume Aws EC2 Class
##############################################################################
class Aws_ec2_volume(Aws_ec2):
    """
    Aws ec2 class for volume
    """

    def volumeid(self):
        return self.resource_id

    def size(self):
        return self.metadata['Size']

    def createtime(self):
        return self.metadata['CreateTime']

    def iops(self):
        return self.metadata['Iops']

    def volumetype(self):
        return self.metadata['VolumeType']

    def device(self):
        device = [i['Device'] for i in self.metadata['Attachments']]
        return ",".join(device)

    def state(self):
        return self.metadata['State']

    def deleteontermination(self):
        deleteon = [i['DeleteOnTermination']
                    for i in self.metadata['Attachments']]
        return ",".join(str(i) for i in deleteon)

    def availabilityzone(self):
        return self.metadata['AvailabilityZone']

    def instanceid(self):
        inst_ids = [i['InstanceId'] for i in self.metadata['Attachments']]
        return ",".join(inst_ids)


##############################################################################
# VPC Aws EC2 Class
##############################################################################
class Aws_ec2_vpc(Aws_ec2):
    """
    Aws ec2 class for vpc
    """

    def vpcid(self):
        return self.resource_id

    def cidrblock(self):
        return self.metadata['CidrBlock']

    def dhcpoptionsid(self):
        return self.metadata['DhcpOptionsId']

    def isdefault(self):
        return self.metadata['IsDefault']

    def instancetenancy(self):
        return self.metadata['InstanceTenancy']

    def state(self):
        return self.metadata['State']


##############################################################################
# Subnet Aws EC2 Class
##############################################################################
class Aws_ec2_subnet(Aws_ec2):
    """
    Aws ec2 class for subnet
    """

    def subnetid(self):
        return self.resource_id

    def vpcid(self):
        return self.metadata['VpcId']

    def cidrblock(self):
        return self.metadata['CidrBlock']

    def availableipaddresscount(self):
        return self.metadata['AvailableIpAddressCount']

    def availabilityzone(self):
        return self.metadata['AvailabilityZone']

    def defaultforaz(self):
        return self.metadata['DefaultForAz']

    def state(self):
        return self.metadata['State']


##############################################################################
# Security Groups Aws EC2 Class
##############################################################################
class Aws_ec2_secgroup(Aws_ec2):
    """
    Aws ec2 class for Security Groups
    """

    def groupid(self):
        return self.resource_id

    def vpcid(self):
        return self.metadata['VpcId']

    def groupname(self):
        return self.metadata['GroupName']

    def description(self):
        return self.metadata['Description']

    def inbound(self):
        all_rules = ""
        for rule in self.metadata['IpPermissions']:
            if rule['IpProtocol'] == "-1":
                port = "(any -> any/any)"
            else:
                port = " ("
                port += str(rule['FromPort'])
                port += " -> "
                port += rule['IpProtocol']
                port += "/"
                port += str(rule['ToPort'])
                port += ")"

            if rule['IpRanges']:
                for ip_range in [i['CidrIp'] for i in rule['IpRanges']]:
                    if all_rules:
                        all_rules += "\n"
                    all_rules += str(ip_range) + port
            if rule['UserIdGroupPairs']:
                for sg_range in [i['GroupId']
                                 for i in rule['UserIdGroupPairs']]:
                    if all_rules:
                        all_rules += "\n"
                    all_rules += str(sg_range) + port

        return all_rules

    def outbound(self):
        all_rules = ""
        for rule in self.metadata['IpPermissionsEgress']:
            if rule['IpProtocol'] == "-1":
                port = "(any -> any/any)"
            else:
                port = " ("
                port += str(rule['FromPort'])
                port += " -> "
                port += rule['IpProtocol']
                port += "/"
                port += str(rule['ToPort'])
                port += ")"

            if rule['IpRanges']:
                for ip_range in [i['CidrIp'] for i in rule['IpRanges']]:
                    if all_rules:
                        all_rules += "\n"
                    all_rules += str(ip_range) + port
            if rule['UserIdGroupPairs']:
                for sg_range in [i['GroupId']
                                 for i in rule['UserIdGroupPairs']]:
                    if all_rules:
                        all_rules += "\n"
                    all_rules += str(sg_range) + port

        return all_rules


###############################################################################
# Query AWS EC2 resource
#
# Return list with resources id
###############################################################################
def query_aws(ec2, *, resource_type, filter_name='', filter_value=''):
    log.info("Params: filter_name: %s, filter_value: %s",
             filter_name, filter_value)

    filters = [{'Name': filter_name,
                'Values': ['*' + filter_value + '*']}]

    resources = list()

    if filter_name:
        log.debug("querying with filter")
        log.debug("filters: %s", pprint.pformat(filters))
        try:
            for resource in getattr(ec2, resource_type).filter(Filters=filters):
                resources.append(resource.id)
        except botocore.exceptions.ClientError as error:
            msg("red", str(error), 1)
    else:
        log.debug("querying without filter")
        for resource in getattr(ec2, resource_type).all():
            resources.append(resource.id)

    log.debug("Returning vpcs ids: %s", pprint.pformat(resources))
    return resources


###############################################################################
# Initialize boto3 session
# Params: args     (args)
#         resource (str): boto3 resource. Ex: ec2, s3
###############################################################################
def initialize_boto3_session(args, resource):
    log.info("args: %s, resource: %s", args, resource)

    # Configure boto3 resource
    if args.profile:
        session = boto3.Session(profile_name=args.profile)
        boto_resource = session.resource(resource)
    else:
        boto_resource = boto3.resource(resource)

    return boto_resource

# vim: ts=4
