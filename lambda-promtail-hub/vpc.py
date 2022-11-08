import pulumi
from pulumi_aws import ec2, config
from settings import demo_vpc_cidr, general_tags

"""
Creates a minium of AWS networking objects required for the demo stack to work
"""

# Create a VPC and Internet Gateway:
demo_vpc = ec2.Vpc("demo-hub-vpc",
    cidr_block=demo_vpc_cidr,
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={**general_tags, "Name": f"demo-vpc-{config.region}"}
)

demo_igw = ec2.InternetGateway("demo-hub-igw",
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

# Create a private subnet to host the Lambda function, it's route table and corresponding association:
demo_private_subnet = ec2.Subnet("demo-private-subnet",
    cidr_block="10.200.0.0/20",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": f"demo-privsub-{config.region}"}
)

demo_private_subnet_route_table = ec2.RouteTable("demo-private-route-table",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": f"demo-privsub-rt-{config.region}"}
)

demo_private_subnet_route_table_association = ec2.RouteTableAssociation("private-route-table-association",
    route_table_id=demo_private_subnet_route_table.id,
    subnet_id=demo_private_subnet.id
)

# Create a public subnet to host a NAT gateway, it's route table and corresponding association:
demo_public_subnet = ec2.Subnet("demo-public-subnet",
    cidr_block="10.200.16.0/20",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": f"demo-pubsub-{config.region}"}
)

demo_public_subnet_route_table = ec2.RouteTable("demo-public-route-table",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": f"demo-pubsub-rt-{config.region}"}
)

demo_public_subnet_route_table_association = ec2.RouteTableAssociation("public-route-table-association",
    route_table_id=demo_public_subnet_route_table.id,
    subnet_id=demo_public_subnet.id
)

# Create a NAT Gateway in the public subnet:
demo_eip = ec2.Eip("demo-eip",
    tags={**general_tags, "Name": f"demo-eip-{config.region}"}
)

demo_nat_gateway = ec2.NatGateway("demo-nat-gateway",
    allocation_id=demo_eip.id,
    subnet_id=demo_public_subnet.id,
    tags={**general_tags, "Name": f"demo-nat-{config.region}"},
    opts=pulumi.ResourceOptions(depends_on=[demo_igw])
)

# Create a WAN route from private subnet towards the NAT:
demo_private_wan_route = ec2.Route("demo-private-wan-route",
    route_table_id=demo_private_subnet_route_table.id,
    nat_gateway_id=demo_nat_gateway.id,
    destination_cidr_block="0.0.0.0/0"
)

# Create an S3 endpoint to save money on NAT traffic:
demo_s3_endpoint = ec2.VpcEndpoint("demo-s3-endpoint",
    vpc_id=demo_vpc.id,
    service_name=f"com.amazonaws.{config.region}.s3",
    vpc_endpoint_type="Interface",
    subnet_ids=[demo_private_subnet.id],
    security_group_ids=[demo_sg.id],
    tags={**general_tags, "Name": f"demo-s3-endpoint-{config.region}"})