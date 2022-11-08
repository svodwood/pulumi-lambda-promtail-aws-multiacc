import pulumi

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

demo_vpc_cidr = project_config.require("vpc-cidr")
demo_bucket_name = project_config.require("log-bucket-name")
demo_promtail_lambda_role_arn = project_config.require("lambda-promtail-role-arn")
demo_promtail_lambda_function_arn = project_config.require("lambda-promtail-function-arn")
regional_alb_account_id = project_config.require("regional-alb-account")