# EC2 Reconnaissance tool
Handy tool to find out helpful information about EC2, which otherwise requires few round of AWS Cli output scaping or Console searching.

## Usage
This package is not published to *PyPI* yet, but will be done soon. Until then, treat it as local package.
- (Optional) It is recommended to use `virtualenv`. Use it like: `python -m virtualenv venv && . venv/bin/activate`. Paired with this option, once done, just run `deactivate` to exit the venv subshell.
- `pip install -e .`
- Make sure you are authenticated against your AWS account and you AWS CLI configuration is setup. If you are using no-default AWS CLI profile, make sure you export the profile to default `export AWS_PROFILE=<your authenticated profile name>`
- `ec2recon -h` for all the options
- One example command would be `ec2recon elb -i i-123456abcdef`
