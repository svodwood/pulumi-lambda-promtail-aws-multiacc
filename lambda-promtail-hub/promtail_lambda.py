import json
from pulumi_aws import iam, lambda_, ec2, cloudwatch, ecr, config
from vpc import demo_private_subnet, demo_vpc, demo_sg
from settings import general_tags, demo_bucket_name

"""
Creates a promtail lambda function
"""

# Create a Lambda function role:

demo_promtail_role = iam.Role("demo-promtail-role", assume_role_policy="""{
    "Version": "2012-10-17",
    "Statement": [
        {
        "Action": "sts:AssumeRole",
        "Principal": {
            "Service": "lambda.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": ""
        }
    ]
    }
    """,
   tags={**general_tags, "Name": f"demo-promtail-role-{config.region}"}
)

# Create a policy for the above role:
demo_promtail_role_policy = iam.RolePolicy("demo-promtail-role-policy",
    role=demo_promtail_role.id,
    policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "s3:GetObject"
                ],
                "Effect": "Allow",
                "Resource": [
                    f"arn:aws:s3:::{demo_bucket_name}/*"
                ]
            }
        ]
    }))

# Attach a managed Lambda VPC execution policy to the Lambda role:
promtail_forwarder_role_vpc_policy_attachment = iam.RolePolicyAttachment("demo-promtail-role-vpc-policy-attachment",
    role=demo_promtail_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole")

# Create lambda-promtail's own CloudWatch log group:
promtail_forwarder_logs = cloudwatch.LogGroup("demo-lambda-loggroup", 
    retention_in_days=1,
    name="/aws/lambda/lambda_promtail",
    tags={**general_tags, "Name": f"demo-promtail-loggroup-{config.region}"}
)