"""
Module class to handle AWS EC2 instances
"""
import logging
import pprint
from pcof import msg
from pcof import print_table
from Aws import Aws_ec2
from Aws import Aws_ec2_instance
from Aws import Aws_ec2_ami
from Aws import Aws_ec2_volume
from Aws import query_aws
from Aws import initialize_boto3_session


log = logging.getLogger(__name__)


##########################################################################
# Show instances' ami details
##########################################################################
def show_instances_ami(*args, **kwargs):
    log.info("args: %s", pprint.pformat(args))
    log.info("args: %s", pprint.pformat(kwargs))

    header = ['InstanceId', 'Tag_Name', 'ImageId', 'Description',
              'OwnerId', 'ImageOwnerAlias']

    rows = list()
    for instance in kwargs["instances"]:
        row = list()
        # handle the instance methods
        for metadata_key in header[:3]:
            row.append((getattr(instance, metadata_key.lower())()))

        ami = Aws_ec2_ami(kwargs['ec2'], 'Image', instance.imageid())
        # handle the ami methods
        for ami_attr in header[3:]:
            row.append((getattr(ami, ami_attr.lower())()))
        rows.append(row)

    align_left = ['Description', 'Tag_Name']
    sortby = kwargs['sortby'] if kwargs['sortby'] else "InstanceId"
    print_table(header, rows, sortby=sortby, alignl=align_left)


###############################################################################
# Show instances' volumes details
###############################################################################
def show_instances_volume(*args, **kwargs):
    log.info("args: %s", pprint.pformat(args))
    log.info("args: %s", pprint.pformat(kwargs))

    header = ['InstanceId', 'Tag_Name', 'VolumeId', 'Size',
              'VolumeType', 'Device', 'State', 'DeleteOnTermination']

    rows = list()
    for instance in kwargs["instances"]:
        # get all instance's volumes
        vol_ids = instance.getvolumesids()

        for vol_id in vol_ids:
            row = list()
            # handle the instance methods
            for metadata_key in header[:2]:
                row.append((getattr(instance, metadata_key.lower())()))
            # handle volumes methods
            vol = Aws_ec2_volume(kwargs["ec2"], 'Volume', vol_id)
            for vol_attr in header[2:]:
                row.append((getattr(vol, vol_attr.lower())()))
            rows.append(row)

    align_right = ['Size']
    align_left = ['Tag_Name']
    sortby = kwargs['sortby'] if kwargs['sortby'] else "InstanceId"
    print_table(
        header,
        rows,
        sortby=sortby,
        alignl=align_left,
        alignr=align_right)


##########################################################################
# Show instances' security group
##########################################################################
def show_instances_secgroup(*args, **kwargs):
    log.info("args: %s", pprint.pformat(args))
    log.info("args: %s", pprint.pformat(kwargs))

    header = ['InstanceId', 'Tag_Name', 'SecurityGroups']
    rows = list()
    for instance in kwargs["instances"]:
        row = list()
        for method in header:
            if method == 'SecurityGroups':
                all_sec_groups = ""
                sec_groups = getattr(instance, method.lower())()
                log.debug("sec_groups: %s", sec_groups)
                for sec_group in sec_groups:
                    if all_sec_groups:
                        all_sec_groups += "\n"
                    all_sec_groups += sec_group['GroupId']
                    all_sec_groups += " -> "
                    all_sec_groups += sec_group['GroupName']
                row.append(all_sec_groups)

            else:
                row.append(getattr(instance, method.lower())())
        rows.append(row)

    align_left = ['Tag_Name', 'SecurityGroups']
    sortby = kwargs['sortby'] if kwargs['sortby'] else "InstanceId"
    print_table(header, rows, sortby=sortby, alignl=align_left, hrules="ALL")


###############################################################################
# Show instances resource names
###############################################################################
def show_instances_names(*args, **kwargs):
    # get vpc id for all instances
    vpcs_id = set([i.vpcid() for i in kwargs['instances'] if i.vpcid()])
    log.debug("vpcs_id: %s", pprint.pformat(vpcs_id))
    # get subnet id for all instances
    subnets_id = set([i.subnetid()
                      for i in kwargs['instances'] if i.subnetid()])
    log.debug("subnets_id: %s", pprint.pformat(subnets_id))

    # instantiate all ec2 vpcs returned in the query
    vpcs = [Aws_ec2(kwargs['ec2'], 'Vpc', i_id) for i_id in vpcs_id]
    # instantiate all ec2 subnets returned in the query
    subnets = [Aws_ec2(kwargs['ec2'], 'Subnet', i_id) for i_id in subnets_id]

    header = ['InstanceId', 'InstanceName', 'VpcName', 'SubnetName',
              'AvailabilityZone']

    rows = list()
    for instance in kwargs['instances']:
        row = list()
        row.append(instance.instanceid())
        row.append(instance.tag_name())
        vpc_name = [i.tag_name() for i in vpcs
                    if i.resource_id == instance.vpcid()]
        row.append(vpc_name[0] if vpc_name else "")
        subnet_name = [i.tag_name() for i in subnets
                       if i.resource_id == instance.subnetid()]
        row.append(subnet_name[0] if subnet_name else "")
        row.append(instance.availabilityzone())
        rows.append(row)

    align_left = ['InstanceName']
    sortby = kwargs['sortby'] if kwargs['sortby'] else "InstanceId"
    print_table(header, rows, sortby=sortby, alignl=align_left)


###############################################################################
# Show all instances metadata
###############################################################################
def show_instances_details(*args, **kwargs):
    log.info("args: %s", pprint.pformat(args))
    log.info("args: %s", pprint.pformat(kwargs))

    for instance in kwargs["instances"]:
        instance.show_metadata()


###############################################################################
# Show instances information as table
###############################################################################
def show_instances_table(*args, **kwargs):
    log.info("args: %s", pprint.pformat(args))
    log.info("args: %s", pprint.pformat(kwargs))

    header = ['InstanceId', 'Tag_Name', 'VpcId', 'AvailabilityZone',
              'InstanceType', 'InstanceState', 'KeyName', 'PrivateIpAddress',
              'LaunchTime']
    rows = list()
    for instance in kwargs["instances"]:
        row = list()
        for metadata_key in header:
            row.append((getattr(instance, metadata_key.lower())()))

        rows.append(row)

    align_left = ['PrivateIpAddress', 'Tag_Name']
    sortby = kwargs['sortby'] if kwargs['sortby'] else "InstanceId"
    print_table(header, rows, sortby=sortby, alignl=align_left)


###############################################################################
# Show all instance tags
###############################################################################
def show_instances_tags(*args, **kwargs):
    log.info("args: %s", pprint.pformat(args))
    log.info("args: %s", pprint.pformat(kwargs))

    # find all tags key
    all_keys = set()
    for instance in kwargs["instances"]:
        all_keys.update(instance.all_tags_key())
    log.debug("all_keys: %s", pprint.pformat(all_keys))

    # create a nested list with all table rows
    # instance_id, tag_key, tag_value
    rows = list()
    for instance in kwargs["instances"]:
        row = list()
        row.append(instance.resource_id)
        all_tags = ""
        for tag_key in all_keys:
            value = instance.tag_value(tag_key)
            # since it is looping through all tag keys, ensure
            # the tag is defined for this specific instance
            if value:
                if all_tags:
                    all_tags += "\n"
                all_tags += tag_key + " -> " + value
        row.append(all_tags)
        rows.append(row)
    header = ['InstanceId', 'Tags']
    sortby = "InstanceId"
    align_left = ['Tags']
    print_table(header, rows, sortby=sortby, alignl=align_left, hrules="ALL")


###############################################################################
# Show number of instance per "type"
###############################################################################
def cmd_num_inst(args):
    log.info("params: %s", args)

    ec2 = initialize_boto3_session(args, 'ec2')

    # check if filter was specified
    filter_name = args.filter[0] if args.filter else ""
    filter_value = args.filter[1] if args.filter else ""

    resource = 'instances'
    # get resources id
    instances_id = query_aws(ec2,
                             resource_type=resource,
                             filter_name=filter_name,
                             filter_value=filter_value)
    if not instances_id:
        msg("red", "Error: No instance found", 1)

    # instantiate all ec2 instances returned in the query
    instances = [Aws_ec2_instance(ec2, 'Instance', i_id)
                 for i_id in instances_id]

    all_types = [getattr(i, args.pertype.lower())() for i in instances]
    log.debug("all_types: %s", pprint.pformat(all_types))

    rows = list()
    for each_type in set(all_types):
        row = list()
        row.append(each_type)
        row.append(all_types.count(each_type))
        rows.append(row)

    header = [args.pertype, 'Number']
    sortby = args.sortby if args.sortby else args.pertype
    print_table(header, rows, sortby=sortby)


###############################################################################
# List instances attributes
###############################################################################
def cmd_list_instances(args):
    log.info("params: %s", args)

    ec2 = initialize_boto3_session(args, 'ec2')

    # check if filter was specified
    filter_name = args.filter[0] if args.filter else ""
    filter_value = args.filter[1] if args.filter else ""

    resource = 'instances'
    # get resources id
    instances_id = query_aws(ec2,
                             resource_type=resource,
                             filter_name=filter_name,
                             filter_value=filter_value)
    if not instances_id:
        msg("red", "Error: No instance found", 1)

    # instantiate all ec2 instances returned in the query
    instances = [Aws_ec2_instance(ec2, 'Instance', i_id)
                 for i_id in instances_id]

    # For each option, store the function to call
    funcs = {
        "table": show_instances_table,
        "detail": show_instances_details,
        "tags": show_instances_tags,
        "ami": show_instances_ami,
        "volume": show_instances_volume,
        "secgroup": show_instances_secgroup,
        "names": show_instances_names}

    # call function to handle the output type
    funcs[args.output](ec2=ec2, instances=instances, sortby=args.sortby)

# vim: ts=4
