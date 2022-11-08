import pulumi
import json
from pulumi_aws import s3
from settings import account_id, general_tags, demo_bucket_name, regional_alb_account_id, demo_promtail_lambda_role_arn, demo_promtail_lambda_function_arn

"""
Creates an S3 log storage location
"""

# Create the log bucket:
demo_s3_access_log_bucket = s3.Bucket("demo-s3-spoke-log-bucket",
    bucket=demo_bucket_name,
    lifecycle_rules=[
        s3.BucketLifecycleRuleArgs(
            enabled=True,
            expiration=s3.BucketLifecycleRuleExpirationArgs(
                days=1,
            ),
            id="log-retention",
        )
    ],
    tags=general_tags
)

# Add a bucket policy:
demo_s3_log_bucket_policy = s3.Bucket("demo-s3-spoke-log-bucket-policy",
    bucket=demo_s3_access_log_bucket.id,
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
                ],
                "Principal": {
                    "AWS": f"{demo_promtail_lambda_role_arn}"
                }
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{regional_alb_account_id}:root"
                },
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{demo_bucket_name}/AWSLogs/{account_id}/*"
            }
        ]
    }))

# Add an event notification to the s3 bucket:
demo_s3_log_bucket_notification = s3.BucketNotification("demo-s3-spoke-log-bucket-notification",
    bucket=demo_s3_access_log_bucket.id,
    lambda_functions=[s3.BucketNotificationLambdaFunctionArgs(
        lambda_function_arn=demo_promtail_lambda_function_arn,
        events=["s3:ObjectCreated:*"]
    )])
