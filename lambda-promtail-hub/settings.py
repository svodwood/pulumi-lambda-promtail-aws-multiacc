import pulumi

"""
General resource tags.
"""
general_tags = {
    "lambda-promtail:project": "lambda-promtail-demo",
    "lambda-promtail:account": "promtail-hub"
}

"""
Configuration variables from pulumi settings file
"""

project_config = pulumi.Config()

demo_vpc_cidr = project_config.require("vpc-cidr")
demo_bucket_name = project_config.require("log-bucket-name")
demo_promtail_image_uri = project_config.require("promtail-image-uri")