from pulumi_aws import lb
from vpc import demo_public_subnets, demo_sg
from s3 import demo_s3_access_log_bucket
from settings import general_tags

"""
Creates a demo AWS Application Load Balancer and it's access log configuration
"""

# Create a load balancer:
demo_alb = lb.LoadBalancer("demo-spoke-alb",
    internal=False,
    load_balancer_type="application",
    security_groups=[demo_sg.id],
    subnets=demo_public_subnets,
    enable_deletion_protection=False,
    access_logs=lb.LoadBalancerAccessLogsArgs(
        bucket=demo_s3_access_log_bucket,
        enabled=True,
    ),
    tags={**general_tags, "Name": f"demo-spoke-alb"}
)
# Create a demo listener:
demo_listener = lb.Listener("demo-spoke-listener",
    load_balancer_arn=demo_alb.arn,
    port=80,
    protocol="HTTP",
    default_actions=[lb.ListenerDefaultActionArgs(
        type="fixed-response",
        fixed_response=lb.ListenerDefaultActionFixedResponseArgs(
            content_type="text/plain",
            message_body="Show this in Grafana",
            status_code="200",
        ),
    )])