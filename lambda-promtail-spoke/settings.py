import pulumi
from pulumi_aws import get_caller_identity

"""
General resource tags.
"""
general_tags = {
    "lambda-promtail:project": "lambda-promtail-demo",
    "lambda-promtail:account": "promtail-spoke"
}

"""
Configuration variables from pulumi settings file
"""

project_config = pulumi.Config()

demo_vpc_cidr = "10.200.0.0/16"
demo_public_subnet_cidrs = [
    "10.200.0.0/20",
    "10.200.16.0/20"
]

demo_bucket_name = project_config.require("log-bucket-name")
demo_promtail_lambda_role_arn = project_config.require("lambda-promtail-role-arn")
demo_promtail_lambda_function_arn = project_config.require("lambda-promtail-function-arn")
regional_alb_account_id = project_config.require("regional-alb-account")
account_id = get_caller_identity().account_id