"""
Module to handle regions
"""
import logging
import pprint
import boto3
import prettytable


log = logging.getLogger(__name__)


##############################################################################
# Query all AWS Regions
#
# Return a list with regions name
##############################################################################
def query_regions():
    ec2 = boto3.client('ec2')

    regions = ec2.describe_regions()
    log.debug("regions: %s", pprint.pformat(regions))

    region_name = [i['RegionName'] for i in regions['Regions']]
    log.debug("region_name: %s", region_name)

    return region_name


##############################################################################
# Query AvailabilityZones for an specific region
#
# Return a list with zone names
##############################################################################
def query_availability_zones(region_name):
    log.debug("Params region_name: %s", region_name)
    ec2 = boto3.client('ec2', region_name=region_name)

    avail_zones = ec2.describe_availability_zones()
    log.debug("avail_zones: %s", pprint.pformat(avail_zones))

    zones_name = [i['ZoneName'] for i in avail_zones['AvailabilityZones']]
    return zones_name


##############################################################################
# List Regions
##############################################################################
def cmd_list_regions(args):
    log.debug("params: %s", args)

    regions_name = query_regions()

    header = ['Region', 'NumberAvailabilityZones', 'AvailabilityZones']
    output = prettytable.PrettyTable(header)
    output.format = True

    for region_name in regions_name:
        row = list()
        row.append(region_name)
        zones = query_availability_zones(region_name)
        row.append(len(zones))
        row.append(", ".join(zones))
        output.add_row(row)

    output.align['AvailabilityZones'] = 'l'
    output.align['Region'] = 'l'
    print(output)

# vim: ts=4
