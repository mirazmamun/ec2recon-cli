from click import core
import boto3
from termcolor import colored
import sys
from typing import Optional, List, Union


def validate_instance_id(ctx: core.Context, param: str, value: str):
    return value


def get_ec2_client() -> boto3.client:
    return boto3.client('ec2')


async def get_ec2_info(instance_ids: Union[str, List[str]], loop = None):
    ec2 = get_ec2_client()
    results = ec2.describe_instances(
        InstanceIds=instance_ids)
    return results.get('Reservations')[0].get('Instances')[0]
