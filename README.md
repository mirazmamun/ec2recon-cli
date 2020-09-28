# EC2 Reconnaissance tool
Handy tool to find out helpful information about EC2, which otherwise requires few round of AWS Cli output scaping or Console searching.

## Usage
- `pip install -e .` 
- Make sure you are authenticated against your AWS account and you AWS CLI configuration is setup. If you are using no-default AWS CLI profile, make sure you export the profile to default `export AWS_PROFILE=<your authenticated profile name>`
- `ec2recon -h` for all the options
- One example command would be `ec2recon elb -i i-123456abcdef`