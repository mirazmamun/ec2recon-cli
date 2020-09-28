import click
from typing import Optional
import sys
from ec2recon.ec2_autoscaling import validate_instance_id, get_ec2_info
from ec2recon.elb import get_instance_elb_tg
import asyncio
from termcolor import colored
from halo import Halo
import pprint
from ec2recon.utils import print_dict_list

# the main group
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass

# subcommand autoscaling


async def run_elb_task(loop, instance_id):
    """Runs the ELB task

    Args:
        loop (even.loop): 
        instance_id ([type]): [description]

    Returns:
        Coroutine: resolved with list
    """
    ec2_info_task = asyncio.create_task(
        get_ec2_info(list([instance_id]), loop=loop))
    elb_info_task = asyncio.create_task(
        get_instance_elb_tg(loop=loop, instance_id=instance_id))
    return await asyncio.gather(ec2_info_task, elb_info_task)


@cli.command(context_settings=CONTEXT_SETTINGS, short_help='EC2 autoscaling info')
@click.option('-i', '--instance-id', 'instance_id', required=True, type=str, help='Instance ID', metavar='INSTANCE_ID', show_default=True, callback=validate_instance_id)
def elb(instance_id):
    loop = asyncio.get_event_loop()
    # print spinner
    spinner = Halo(
        text=f"Running query for {instance_id}, sit tight", spinner='dots')
    spinner.start()
    all_info = loop.run_until_complete(
        run_elb_task(loop=loop, instance_id=instance_id))
    spinner.stop()
    # print all info
    click.echo(
        f"{colored(f'======== Instance Details: {instance_id} =========', color='magenta'):^100}")
    click.echo(f"{colored('ELB Info:', attrs=['bold'])}")
    for i in all_info[1]:
        click.echo(
            f"{colored('LB Name:', color='cyan', attrs=['bold']):<40} {colored(i.get('LoadBalancerName', ''))}")
        click.echo(
            f"{colored('Target Group Name:', color='cyan', attrs=['bold']):<40} {colored(i.get('TargetGroupName', ''))}")
        click.echo(f"")
    ec2_details = all_info[0]
    click.echo(f"{colored('EC2 Info:', attrs=['bold'])}")
    click.echo(
        f"{colored('Instance Type:', color='cyan', attrs=['bold']):<40} {colored(ec2_details.get('InstanceType', ''))}")
    click.echo(
        f"{colored('Launch Time:', color='cyan', attrs=['bold']):<40} {colored( ec2_details.get('LaunchTime').isoformat() if ec2_details.get('LaunchTime') else '')}")
    click.echo(f"{colored('IP Addresses:', color='cyan', attrs=['bold']):<40} Private - {colored(ec2_details.get('PrivateIpAddress', ''))}"
               f" Public - {colored(ec2_details.get('PublicIpAddress', ''))}")
    click.echo(
        f"{colored('Status:', color='cyan', attrs=['bold']):<40} {colored(ec2_details.get('State', '').get('Name', ''))}")
    click.echo(
        f"{colored('Tags:', color='cyan', attrs=['bold']):<40}\n{colored(print_dict_list(ec2_details.get('Tags', [])[:5]))}")
    click.echo(
        f"{colored('VPC Id:', color='cyan', attrs=['bold']):<40} {colored(ec2_details.get('VpcId', ''))}")
    click.echo(
        f"{colored('Subnet Id:', color='cyan', attrs=['bold']):<40} {colored(ec2_details.get('SubnetId', ''))}")
