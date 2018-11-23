# aws_list

**aws_list** - Python script to list useful Amazon Web Services (AWS) information.
It display information about VPCs, EC2 Instances, Security Groups, EC2 volumes, S3 bucket, etc.

Authorization is performed using Environment Variables or Shared Credentials File (~/.aws/credentials).
Please check https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html for additional details.

Developed for Python 3.

### Usage:

```bash
$ ./aws_list.py
usage: aws_list.py [-h] [--debug] [--profile PROFILE]
                   {instances,numinstances,ami,regions,secgroups,subnets,s3,volumes,vpcs}
                   ...

Script to list AWS information

optional arguments:
  -h, --help            show this help message and exit
  --debug, -d           debug flag
  --profile PROFILE, -p PROFILE
                        Profile Name

Commands:
  {instances,numinstances,ami,regions,secgroups,subnets,s3,volumes,vpcs}
    instances           List [EC2] Instances
    numinstances        List [EC2] Number of Instance
    ami                 List [EC2] AMI (Amazon Machine Images)
    regions             List [EC2] Regions and Availability Zones
    secgroups           List [EC2] Security Groups
    subnets             List [EC2] Subnets
    s3                  List [S3] Buckets
    volumes             List [EC2] Volumes
    vpcs                List VPC (Amazon Virtual Private Cloud)

    Example of use:
        ./aws_list.py instances
        ./aws_list.py instances -filter instance-id i-0b89900d840198c16
        ./aws_list.py instances -filter tag:Name DNS
        ./aws_list.py instances -detail
```

Each subcommand has its own help.

```bash
$ ./aws_list.py instances -h
usage: aws_list.py instances [-h] [-filter filter_name value] [-sortby SORTBY]
                             [-detail | -tags | -ami | -volumes | -secgroup | -names]

optional arguments:
  -h, --help            show this help message and exit
  -filter filter_name value
                        Filter instances
  -sortby SORTBY        Sort table output by "column"
  -detail               Show instances metadata
  -tags                 Show instances tags
  -ami                  Show ami details
  -volumes              Show volumes details
  -secgroup             Show Security Groups details
  -names                Show vpc and subnet names details

$ ./aws_list.py secgroups -h
usage: aws_list.py secgroups [-h] [-sortby SORTBY] [-detail] [-rules]
                             [-filter filter_name value]

optional arguments:
  -h, --help            show this help message and exit
  -sortby SORTBY        Sort table output by "column"
  -detail               Show security group details
  -rules                Show security group rules
  -filter filter_name value
                        Filter VPCs
```

### Example:

```
$ ./aws_list.py instances
+---------------------+----------------------+--------------+------------------+--------------+---------------+----------------+------------------+---------------------------+
|      InstanceId     | Tag_Name             |    VpcId     | AvailabilityZone | InstanceType | InstanceState |    KeyName     | PrivateIpAddress |         LaunchTime        |
+---------------------+----------------------+--------------+------------------+--------------+---------------+----------------+------------------+---------------------------+
| i-00038adk49e06010c | TEST SERVER          | vpc-al398d8a |    sa-east-1a    |   t2.micro   |    running    | mykey          | 172.16.80.230    | 2018-10-18 17:28:35+00:00 |
| i-00e39saj498224623 | OpenLDAP Server      | vpc-al398d8a |    sa-east-1a    |   t3.micro   |    running    | mykey          | 172.16.83.78     | 2018-10-22 17:56:45+00:00 |
| i-01cd1ak49s9sa8c42 | Prometheus           | vpc-al398d8a |    sa-east-1a    |  t2.medium   |    running    | mykey          | 172.16.82.153    | 2018-09-20 14:30:16+00:00 |
+---------------------+----------------------+--------------+------------------+--------------+---------------+----------------+------------------+---------------------------+

$ ./aws_list.py instances -volumes
+---------------------+----------------------+-----------------------+------+------------+-----------+--------+---------------------+
|      InstanceId     | Tag_Name             |        VolumeId       | Size | VolumeType |   Device  | State  | DeleteOnTermination |
+---------------------+----------------------+-----------------------+------+------------+-----------+--------+---------------------+
| i-00038adk49e06010c | TEST SERVER          | vol-06e934928428s1c54 |    8 |    gp2     | /dev/xvda | in-use |         True        |
| i-00e39saj498224623 | OpenLDAP Server      | vol-0dd40193984e97c6f |   20 |  standard  | /dev/sda1 | in-use |         True        |
| i-01cd1ak49s9sa8c42 | Prometheus           | vol-0a740949494992a85 |   20 |  standard  | /dev/sda1 | in-use |         True        |
+---------------------+----------------------+-----------------------+------+------------+-----------+--------+---------------------+

$ ./aws_list.py instances -ami
+---------------------+----------------------+-----------------------+------------------------------------------------+--------------+-----------------+
|      InstanceId     | Tag_Name             |        ImageId        | Description                                    |   OwnerId    | ImageOwnerAlias |
+---------------------+----------------------+-----------------------+------------------------------------------------+--------------+-----------------+
| i-00038adk49e06010c | TEST SERVER          | ami-0e2e2a5f6c0977c50 | Amazon Linux 2 AMI 2.0.20181008 x86_64 HVM gp2 | 137112412989 |      amazon     |
| i-00e39saj498224623 | OpenLDAP Server      |      ami-cb5803a7     | CentOS Linux 7 x86_64 HVM EBS ENA 1805_01      | 679593333241 | aws-marketplace |
| i-01cd1ak49s9sa8c42 | Prometheus           |      ami-cb5803a7     | CentOS Linux 7 x86_64 HVM EBS ENA 1805_01      | 679593333241 | aws-marketplace |
+---------------------+----------------------+-----------------------+------------------------------------------------+--------------+-----------------+

$ ./aws_list.py vpcs
+--------------+-------------+-----------------+------------------------+-----------+-----------------+-----------+
|    VpcId     |   Tag_Name  | CidrBlock       |     DhcpOptionsId      | IsDefault | InstanceTenancy |   State   |
+--------------+-------------+-----------------+------------------------+-----------+-----------------+-----------+
| vpc-49a93d92 | us-east-1   | 172.16.120.0/21 | dopt-008ad8a833a26483a |   False   |     default     | available |
| vpc-al398d8a | us-east-1   | 172.16.80.0/21  | dopt-0538a34234283ad3f |   False   |     default     | available |
+--------------+-------------+-----------------+------------------------+-----------+-----------------+-----------+

$ ./aws_list.py instances -filter tag:Name 'OpenLDAP Server'
+---------------------+-----------------+--------------+------------------+--------------+---------------+----------------+------------------+---------------------------+
|      InstanceId     | Tag_Name        |    VpcId     | AvailabilityZone | InstanceType | InstanceState |    KeyName     | PrivateIpAddress |         LaunchTime        |
+---------------------+-----------------+--------------+------------------+--------------+---------------+----------------+------------------+---------------------------+
| i-00e39saj498224623 | OpenLDAP Server | vpc-al398d8a |    sa-east-1a    |   t3.micro   |    running    | mykey          | 172.16.83.78     | 2018-10-22 17:56:45+00:00 |
| i-0ce9c7d7ae7e37187 | OpenLDAP Server | vpc-al398d8a |    sa-east-1c    |   t3.micro   |    running    | mykey          | 172.16.86.205    | 2018-10-22 18:00:53+00:00 |
+---------------------+-----------------+--------------+------------------+--------------+---------------+----------------+------------------+---------------------------+

$ ./aws_list.py subnets
+-----------------+--------------------+--------------+-----------------+-------------------------+------------------+--------------+-----------+
|     SubnetId    | Tag_Name           |    VpcId     | CidrBlock       | AvailableIpAddressCount | AvailabilityZone | DefaultForAz |   State   |
+-----------------+--------------------+--------------+-----------------+-------------------------+------------------+--------------+-----------+
| subnet-213adb7c | public-sa-east-1c  | vpc-49a93d92 | 172.16.124.0/24 |           250           |    sa-east-1c    |    False     | available |
| subnet-266a44aa | public-sa-east-1c  | vpc-al398d8a | 172.16.84.0/24  |           250           |    sa-east-1c    |    False     | available |
+-----------------+--------------------+--------------+-----------------+-------------------------+------------------+--------------+-----------+

$ ./aws_list.py instances -secgroup
+---------------------+------------------------+----------------------------------------------------+
|      InstanceId     | Tag_Name               | SecurityGroups                                     |
+---------------------+------------------------+----------------------------------------------------+
| i-000343429243923ac | TEST SERVER            | sg-93837a73 -> BastionSSH                          |
|           34342     |                        | sg-0b62838ad83832e3af -> Default Outgoing Access   |
|                     |                        | sg-01678dce1888f2201 -> Monitoramento - Prometheus |
|                     |                        | sg-0bf9893929aad93c0 -> ldap_traffic               |
+---------------------+------------------------+----------------------------------------------------+
| i-00239313s1343d623 | OpenLDAP Server        | sg-93837a73 -> BastionSSH                          |
|                     |                        | sg-0bf939ad939e64cc0 -> ldap_traffic               |
+---------------------+------------------------+----------------------------------------------------+
| i-01c99131231as8c42 | Prometheus             | sg-93837a73 -> BastionSSH                          |
|                     |                        | sg-0b62838ad83832e3af -> Default Outgoing Access   |
|                     |                        | sg-01678dce1888f2201 -> Monitoramento - Prometheus |
+---------------------+------------------------+----------------------------------------------------+
```

