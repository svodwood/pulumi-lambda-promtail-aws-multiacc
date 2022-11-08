import pulumi
from pulumi_aws import ec2, config
from settings import demo_vpc_cidr, general_tags

"""
Creates a minium of AWS networking objects required for the demo stack to work
"""

# Create a VPC and Internet Gateway:
demo_vpc = ec2.Vpc("demo-spoke-vpc",
    cidr_block=demo_vpc_cidr,
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={**general_tags, "Name": f"demo-vpc-{config.region}"}
)