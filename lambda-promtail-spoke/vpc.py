import pulumi
from pulumi_aws import ec2, config, get_availability_zones
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

demo_igw = ec2.InternetGateway("demo-spoke-igw",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": f"demo-igw-{config.region}"}
)

# Create a default any-any security group for demo purposes:
demo_sg = ec2.SecurityGroup("demo-security-group",
    description="Allow any-any",
    vpc_id=demo_vpc.id,
    ingress=[ec2.SecurityGroupIngressArgs(
        description="Any",
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )],
    egress=[ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )],
    tags={**general_tags, "Name": f"demo-sg-{config.region}"}
)

# Create demo subnets for the Application Load Balancer
demo_azs = get_availability_zones(state="available").names
demo_public_subnets = []

demo_public_subnet_cidrs = [
    "10.200.0.0/20",
    "10.200.16.0/20"
]

for i in range(2):
    prefix = f"{demo_azs[i]}"
    demo_subnet = ec2.Subnet(f"demo-spoke-subnet-{prefix}",
        vpc_id=demo_vpc.id,
        cidr_block=demo_public_subnet_cidrs[i],
        availability_zone=demo_azs[i],
        tags={**general_tags, "Name": f"demo-spoke-subnet-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_vpc)
    )
    
    demo_public_subnets.append(demo_subnet)

    demo_route_table = ec2.RouteTable(f"demo-spoke-rt-{prefix}",
        vpc_id=demo_vpc.id,
        tags={**general_tags, "Name": f"demo-spoke-subnet-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_vpc)
    )
    
    demo_route_table_association = ec2.RouteTableAssociation(f"demo-spoke-rt-association-{prefix}",
        route_table_id=demo_route_table.id,
        subnet_id=demo_subnet.id
    )

    demo_wan_route = ec2.Route(f"demo-wan-route-{prefix}",
        route_table_id=demo_route_table.id,
        gateway_id=demo_igw.id,
        destination_cidr_block="0.0.0.0/0"
    )
