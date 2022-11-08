import json
from pulumi import export
from pulumi_aws import iam, lambda_, ec2, cloudwatch, ecr, config
from vpc import demo_private_subnet, demo_vpc, demo_sg
from settings import general_tags, demo_bucket_name, demo_promtail_image_uri

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
demo_promtail_forwarder_role_vpc_policy_attachment = iam.RolePolicyAttachment("demo-promtail-role-vpc-policy-attachment",
    role=demo_promtail_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole")

# Create lambda-promtail's own CloudWatch log group:
demo_promtail_forwarder_logs = cloudwatch.LogGroup("demo-lambda-loggroup", 
    retention_in_days=1,
    name="/aws/lambda/lambda_promtail",
    tags={**general_tags, "Name": f"demo-promtail-loggroup-{config.region}"}
)

# Create the Lambda function from the ECR image:
demo_promtail_lambda_function = lambda_.Function("demo-lambda-promtail",
        name="lambda_promtail",
        image_uri=demo_promtail_image_uri,
        role=demo_promtail_role.arn,
        memory_size=256,
        timeout=60,
        architectures=["arm64"],
        package_type="Image",
        vpc_config=lambda_.FunctionVpcConfigArgs(
            subnet_ids=[demo_private_subnet.id],
            security_group_ids=[demo_sg.id],
        ),
        environment=lambda_.FunctionEnvironmentArgs(
            variables={
                "WRITE_ADDRESS": "",
                "USERNAME": "",
                "PASSWORD": "",
                "BEARER_TOKEN": "",
                "KEEP_STREAM": "",
                "BATCH_SIZE": "",
                "EXTRA_LABELS": "",
                "TENANT_ID": ""
            },
        ),
        tags=general_tags)

# Allow for the lambda function to be invoked by S3 notifications in the spoke account
allow_invoke_lambda_from_spoke_s3 = lambda_.Permission("demo-lambda-promtail-invoke-permission",
        action="lambda:InvokeFunction",
        function=demo_promtail_lambda_function.name,
        principal="s3.amazonaws.com",
        source_arn=f"arn:aws:s3:::{demo_bucket_name}",
    )

export("lambda-promtail-role-arn", demo_promtail_role.arn)
export("lambda-promtail-function-arn", demo_promtail_lambda_function.arn)