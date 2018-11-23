"""
Module to handle S3
"""
import logging
import pprint
import prettytable
from pcof import bytes2human
from Cloudwatch import Cloudwatch
from Aws import initialize_boto3_session


log = logging.getLogger(__name__)


##############################################################################
# Query S3 Bucket Size
# Params:
#   - bucket_names   (list): list with bucket names
#   - numdays         (int): number days to show
##############################################################################
def s3_buckets_size(bucket_names, numdays=7):
    log.debug("bucket_names: %s", bucket_names)

    header = ['BucketName', 'Timestamp', 'BucketSizeBytes']
    output = prettytable.PrettyTable(header)
    output.format = True

    cloudwatch = Cloudwatch()
    for bucket_name in bucket_names:
        resp = cloudwatch.get_s3_bucket_size(bucket_name, numdays)
        log.debug("resp: %s", pprint.pformat(resp))
        if resp:
            for resp_day in resp:
                row = list()
                row.append(bucket_name)
                row.append(resp_day['Timestamp'])
                size = resp_day['Average']
                row.append("{0} {1}".format(*bytes2human(size)))
                output.add_row(row)
        else:
            row = list()
            row.append(bucket_name)
            row.append("")
            row.append("")
            output.add_row(row)

    output.align['BucketName'] = 'l'
    output.sortby = 'BucketName'
    print(output)


##############################################################################
# Query S3 Bucket Number of Object
# Params:
#   - bucket_names   (list): list with bucket names
#   - numdays         (int): number days to show
##############################################################################
def s3_buckets_numobj(bucket_names, numdays=7):
    log.debug("bucket_names: %s", bucket_names)

    header = ['BucketName', 'Timestamp', 'NumberOfObjects']
    output = prettytable.PrettyTable(header)
    output.format = True

    cloudwatch = Cloudwatch()
    for bucket_name in bucket_names:
        resp = cloudwatch.get_s3_bucket_numobj(bucket_name, numdays)
        log.debug("resp: %s", pprint.pformat(resp))
        if resp:
            for resp_day in resp:
                row = list()
                row.append(bucket_name)
                row.append(resp_day['Timestamp'])
                num = resp_day['Average']
                row.append("{:.0f}".format(num))
                output.add_row(row)
        else:
            row = list()
            row.append(bucket_name)
            row.append("")
            row.append("")
            output.add_row(row)

    output.align['BucketName'] = 'l'
    output.sortby = 'BucketName'
    print(output)


##############################################################################
# List S3 Buckets
##############################################################################
def cmd_list_s3(args):
    log.info("params: %s", args)

    s3 = initialize_boto3_session(args, 's3')

    buckets_name = list()
    for bucket in s3.buckets.all():
        buckets_name.append(bucket.name)

    if args.size:
        s3_buckets_size(buckets_name, 1)
    elif args.numobj:
        s3_buckets_numobj(buckets_name, 4)
    else:
        print("\n".join(buckets_name))

# vim: ts=4
