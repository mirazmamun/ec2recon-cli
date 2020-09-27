import click
from typing import Optional
import sys
from ec2recon.ec2_autoscaling import validate_instance_id, get_ec2_info
from ec2recon.elb import get_instance_elb_tg
import asyncio

# the main group
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass

# subcommand autoscaling


async def run_elb_task(loop, instance_id):
    ec2_info_task = asyncio.create_task(get_ec2_info(list([instance_id]), loop=loop))
    elb_info_task = asyncio.create_task(get_instance_elb_tg(loop=loop, instance_id=instance_id))
    return await asyncio.gather(ec2_info_task, elb_info_task)

@cli.command(context_settings=CONTEXT_SETTINGS, short_help='EC2 autoscaling info')
@click.option('-i', '--instance-id', 'instance_id', required=True, type=str, help='Instance ID', metavar='INSTANCE_ID', show_default=True, callback=validate_instance_id)
def elb(instance_id):
    loop = asyncio.get_event_loop()
    # ec2_info_task = asyncio.create_task(get_ec2_info(list([instance_id]), loop=loop))
    # get elb details
    all_info = loop.run_until_complete(run_elb_task(loop=loop, instance_id=instance_id))
    click.echo(all_info)
