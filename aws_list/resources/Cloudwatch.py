"""
Module to handle Cloud Watch
"""
import logging
from datetime import datetime, timedelta
import boto3


log = logging.getLogger(__name__)


##############################################################################
# Cloud Watch Class
##############################################################################
class Cloudwatch:
    """
    Class to handle pre-defined queries on Cloud Watch
    """

    def __init__(self, profile=''):
        if profile:
            session = boto3.Session(profile_name=profile)
            self.cw = session.client('cloudwatch')
        else:
            self.cw = boto3.client('cloudwatch')

    def get_s3_bucket_size(self, bucket_name, numdays='7'):
        """
        Return S3 Bucket Size

        Params:
            bucket_name    (str): Bucket Name
            numdays        (int): Number of days to show (now - numdays)
        """
        log.debug("bucket_name: %s, numdays: %s", bucket_name, numdays)

        resp = self.cw.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName='BucketSizeBytes',
            Unit='Bytes',
            Statistics=['Average'],
            EndTime=datetime.now(),
            StartTime=datetime.now() - timedelta(days=int(numdays)),
            Period=86400,
            Dimensions=[
                {'Name': 'BucketName', 'Value': bucket_name},
                {'Name': 'StorageType', 'Value': 'StandardStorage'}
            ]
        )
        return resp['Datapoints']

    def get_s3_bucket_numobj(self, bucket_name, numdays='7'):
        """
        Return S3 Bucket Number of Objects

        Params:
            bucket_name    (str): Bucket Name
            numdays        (int): Number of days to show (now - numdays)
        """
        log.debug("bucket_name: %s, numdays: %s", bucket_name, numdays)

        resp = self.cw.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName='NumberOfObjects',
            Unit='Count',
            Statistics=['Average'],
            EndTime=datetime.now(),
            StartTime=datetime.now() - timedelta(days=int(numdays)),
            Period=86400,
            Dimensions=[
                {'Name': 'BucketName', 'Value': bucket_name},
                {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
            ]
        )
        return resp['Datapoints']

# vim: ts=4
