import click
import boto3
from termcolor import colored
import sys
from typing import Optional, List, Union, TypedDict
import random
import asyncio
import time
import collections

STATE_ACTIVE = 'active'
STATE_PROVISIONING = 'provisioning'


def get_elb_client(region='ap-southeast-1') -> boto3.client:
    return boto3.client('elbv2', region_name=region)


def filter_elbs(elb_list: List[dict] = []):
    active_elbs = filter(lambda i: i.get('State').get('Code') in [
                         STATE_ACTIVE, STATE_PROVISIONING], elb_list)
    return [{'LoadBalancerName': i.get('LoadBalancerName'), 'DNSName': i.get('DNSName'), 'LoadBalancerArn': i.get('LoadBalancerArn')} for i in list(active_elbs)]


def get_elbs():
    elb = get_elb_client()
    paginator = elb.get_paginator('describe_load_balancers')
    page_iterator = paginator.paginate()
    elb_list = []
    for page in page_iterator:
        elb_list.extend(page.get('LoadBalancers', []))
    filtered_elbs = filter_elbs(elb_list)
    return filtered_elbs


def filter_tg(tg_list: List[dict]):
    return [{'TargetGroupArn': i.get('TargetGroupArn'), 'TargetGroupName': i.get('TargetGroupName')} for i in tg_list]


def get_target_groups(elb_arn):
    elb = get_elb_client()
    tg = elb.describe_target_groups(LoadBalancerArn=elb_arn)
    filtered_tg = filter_tg(tg.get('TargetGroups'))
    return filtered_tg


def filter_targets(target_list: List[dict]):
    return [{'InstanceId': i.get('Target').get('Id')} for i in target_list]


def get_target_group_targets(tg_arn):
    elb = get_elb_client()
    targets = elb.describe_target_health(TargetGroupArn=tg_arn)
    filtered_tg = filter_targets(targets.get('TargetHealthDescriptions'))
    return filtered_tg


class Targets_Coll(TypedDict):
    Instances: List[str]


class TG_Targets_Coll(TypedDict):
    TargetGroupName: str
    Targets: List[Targets_Coll]


class ELB_TG_Targets_Coll(TypedDict):
    LoadBalancerName: str
    TargetGroups: List[TG_Targets_Coll]

# main entry point, get all lb -> [tg] -> [targets]


async def list_elb_tg_targets(loop):
    elbs = get_elbs()
    # all async functions
    def get_target_info(tg_arn, tg_name) -> TG_Targets_Coll:
        # click.echo(f'Running for TG {tg_name}@{time.perf_counter()}')
        target_list = []
        targets = get_target_group_targets(tg_arn=tg_arn)
        for target in targets:
            target_list.append(target.get('InstanceId'))
        return {
            'TargetGroupName' : tg_name,
            'Targets' : target_list
        }

    def get_tg_info(elb_arn, elb_name) -> ELB_TG_Targets_Coll:
        tgs = get_target_groups(elb_arn=elb_arn)
        # click.echo(f'Running for ELB {elb_name}@{time.perf_counter()}')
        tg_target_response = []
        for tg in tgs:
            tg_target_response.append(get_target_info(tg.get('TargetGroupArn'), tg.get('TargetGroupName')))
        return {
            'LoadBalancerName' : elb_name,
            'TargetGroups' : tg_target_response
        }
        
    elb_tasks = []
    for elb in elbs:
        elb_tasks.append(loop.run_in_executor(None, get_tg_info, elb.get('LoadBalancerArn'), elb.get('LoadBalancerName')))
    return await asyncio.gather(*elb_tasks)
        
async def list_instance_elb_tg(loop):
    elb_list = await list_elb_tg_targets(loop=loop)
    instance_elb_tg_list = collections.defaultdict(list)
    for elb in elb_list:
        elb_name = elb.get('LoadBalancerName')
        for tg in elb.get('TargetGroups'):
            tg_name = tg.get('TargetGroupName')
            for i in tg.get('Targets'):
                instance_elb_tg_list[i].append({
                    'LoadBalancerName' : elb_name,
                    'TargetGroupName' : tg_name
                })
    return instance_elb_tg_list

async def get_instance_elb_tg(loop , instance_id) -> List[dict]:
    """[summary]

    Args:
        loop ([type]): [description]
        instance_id ([type]): [description]
    """
    instances_list = await list_instance_elb_tg(loop=loop)
    return instances_list.get(instance_id, [])

if __name__ == '__main__':
    # lbarn = 'arn:aws:elasticloadbalancing:ap-southeast-1:102073650908:loadbalancer/app/production-abtest-api-lb/a1ae85cfb1f56905'
    # tgarn = 'arn:aws:elasticloadbalancing:ap-southeast-1:102073650908:targetgroup/production-abtest-api-tg/5dcb8127d6479f03'
    # print(get_target_group_targets(tgarn))
    loop = asyncio.get_event_loop()
    instances = loop.run_until_complete(list_instance_elb_tg(loop=loop))
    loop.close()
    print(len(instances))
    print(instances)
