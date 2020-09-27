from setuptools import setup, find_packages

setup(
    name='ec2rcon',
    description='Get various information about EC2',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        ec2recon=ec2recon.app:cli
    ''',
)