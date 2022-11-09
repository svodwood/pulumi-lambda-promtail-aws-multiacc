# Lambda Promtail Pulumi Demo

AWS Application Load Balancer access log data collection from S3 using lambda-promtail and Loki: a hub and spoke use case.

## Lambda Promtail Hub

[![Deploy](https://get.pulumi.com/new/button.svg)](https://app.pulumi.com/new?template=https://github.com/svodwood/pulumi-lambda-promtail-aws-multiacc/tree/main/lambda-promtail-hub)

Pulumi code to provision demo objects in a hub log collection account:
- VPC
- Lambda

## Lambda Promtail Spoke

[![Deploy](https://get.pulumi.com/new/button.svg)](https://app.pulumi.com/new?template=https://github.com/svodwood/pulumi-lambda-promtail-aws-multiacc/tree/main/lambda-promtail-spoke)

Pulumi code to provision demo objects in a spoke log producer account:
- VPC
- Application Load Balancer
- S3 Bucket