#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Define the overall CDK pipeline for the NMLS Spring Boot application.

Attributes:
    APP_TAGS (dict): The application/stack tags to be applied across all resources.
    GLOBAL_CONFIG (dict): The configuration mapping that can be referenced across
        the project.  This variable is used to build default APP_TAGS values.
    PIPELINE_REGION (str): The AWS region to target for pipeline deployment.
        Uses the environment variable: CDK_PIPELINE_REGION.
        Defaults to: us-east-1.
    PIPELINE_ID (str): The CDK stack ID to be used for the CdkPipeline.
        Uses the environment variable: CDK_PIPELINE_ID.
        Defaults to: NmlsInfraPipelineStack.
    MGMT_PIPELINE_ACCOUNT (str): The AWS account to be targetted for pipeline deployment.
        Uses the environment variable: CDK_MGMT_PIPELINE_ACCOUNT.
        Defaults to: ************ (management).
    NONPROD_TARGET_ACCOUNT (str): The AWS account to be targetted for nonproduction deployments.
        Uses the environment variable: CDK_NONPROD_NONPROD_ACCOUNT.
        Defaults to: ************ (nonproduction).

"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_codedeploy as codedeploy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda, aws_lambda_python
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_synthetics as synthetics
from aws_cdk import core as cdk
from aws_cdk import aws_cloudwatch_actions as cw_actions
from aws_cdk import aws_sns as sns
from cdk_watchful import Watchful

from canaries.content_service_live import content_service_live_lambda_function
from canaries.content_service_ready import content_service_ready_lambda_function
from canaries.content_service_summary import content_service_summary_lambda_function
from canaries.token_service import token_service_lambda_function
from canaries.download_service import download_service__lambda_function
from canaries.pdfton_service import pdftron_service_live_lambda_function
from canaries.share_service import share_service_live_lambda_function

# class LambdaStack(cdk.Stack):
#    """Define the lambda stack."""
#
#    def __init__(self, scope: cdk.Construct, construct_id: str, lambda_name: str, **kwargs) -> None:
#        """Initialize the lambda stack."""
#        super().__init__(scope, construct_id, **kwargs)
#
#        lambda_func = aws_lambda_python.PythonFunction(
#            self,
#            f"{lambda_name}-id",
#            runtime=aws_lambda.Runtime.PYTHON_3_8,
#            entry="./src/",
#            index="handler.py",
#            handler="lambda_handler",
#
#            timeout=cdk.Duration.minutes(3),
#        )
#
#        alias = aws_lambda.Alias(
#            self, f"{lambda_name.title()}Alias", alias_name="Current", version=lambda_func.current_version)


class SyntheticsStack(cdk.Stack):
    """Define the CloudWatch Synthetics Stack."""

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        name: str,
        account_id: str,
        account_name: str,
        region: str,
        vpc_id: str,
        subnet_ids: List[str],
        environment: str,
        **kwargs,
    ) -> None:
        """Initialize the CloudWatch Synthetics Stack."""
        super().__init__(scope, construct_id, **kwargs)

        policy_statement = iam.PolicyStatement(
            actions=[
                "ssm:DescribeParameters",
                "ssm:GetParameters",
                "ssm:GetParameter",
                "sts:GetCallerIdentity",
                "cloudwatch:PutMetricData",
                "ec2:CreateNetworkInterface",
                "s3:ListAllMyBuckets",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DeleteNetworkInterface",
                "xray:*",
            ],
            resources=["*"],
        )

        service_principal = iam.ServicePrincipal("lambda.amazonaws.com")

        synthetics_role = iam.Role(
            self,
            f"{name}-role",
            role_name=f"{name}-role",
            assumed_by=service_principal,
            description="Allows Lambda functions to call AWS services on your behalf.",
        )

        synthetics_role.add_to_policy(policy_statement)

        cloudwatch_results_bucket = s3.Bucket(
            self, f"{environment}-cw-syn-results-{account_id}-{region}", bucket_name=f"{environment}-cw-syn-results-{account_id}-{region}"
        )

        allow_read = iam.PolicyStatement(
            sid="AllowRead",
            effect=iam.Effect.ALLOW,
            principals=[iam.AnyPrincipal()],
            actions=["s3:*"],
            resources=[
                f"{cloudwatch_results_bucket.bucket_arn}",
                f"{cloudwatch_results_bucket.bucket_arn}/*",
            ],
        )
        cloudwatch_results_bucket.add_to_resource_policy(allow_read)

        vpc = ec2.Vpc.from_lookup(self, "LookupVpc", vpc_id=vpc_id)
        private_subnets = vpc.select_subnets(subnet_group_name="Private")
        synthetics_security_group = ec2.SecurityGroup(
            self,
            "CloudWatchSyntheticsSG",
            vpc=vpc,
            allow_all_outbound=True,
            description=f"Allows CloudWatch Synthetic Canaries to hit Alfresco endpoints",
        )

        # synthetics_security_group.add_egress_rule(
        #    ec2.Peer.ipv4("0.0.0.0/0"), ec2.Port.tcp(80))

        # Python3 code here creating class
        class CanaryClass(object):
            def __init__(self, name, key, code):
                self.name = name
                self.key = key
                self.code = code

        # creating list
        content_service_live = CanaryClass(
            f"{environment}-cnt-srv-live",
            "content-service-live",
            synthetics.CfnCanary.CodeProperty(
                handler="handler.handler", script=content_service_live_lambda_function(environment)
            ),
        )
        content_service_ready = CanaryClass(
            f"{environment}-cnt-srv-rdy",
            "content_service_ready",
            synthetics.CfnCanary.CodeProperty(
                handler="handler.handler", script=content_service_ready_lambda_function(environment)
            ),
        )
        content_service_summary = CanaryClass(
            f"{environment}-cnt-srv-sum",
            "content_service_summary",
            synthetics.CfnCanary.CodeProperty(
                handler="handler.handler", script=content_service_summary_lambda_function(environment)
            ),
        )
        download_service = CanaryClass(
            f"{environment}-dwld-srv",
            "download_service",
            synthetics.CfnCanary.CodeProperty(
                handler="handler.handler", script=download_service__lambda_function(environment)
            ),
        )
        pdftron_service = CanaryClass(
            f"{environment}-pdf-srv",
            "pdftron_service",
            synthetics.CfnCanary.CodeProperty(
                handler="handler.handler", script=pdftron_service_live_lambda_function(environment)
            ),
        )
        share_service = CanaryClass(
            f"{environment}-share-srv",
            "share_service",
            synthetics.CfnCanary.CodeProperty(
                handler="handler.handler", script=share_service_live_lambda_function(environment)
            ),
        )
        token_service = CanaryClass(
            f"{environment}-token-srv",
            "token_service",
            synthetics.CfnCanary.CodeProperty(
                handler="handler.handler", script=token_service_lambda_function(environment)
            ),
        )

        list = [
            content_service_live,
            content_service_ready,
            content_service_summary,
            download_service,
            pdftron_service,
            share_service,
            token_service,
        ]

        schedule = synthetics.CfnCanary.ScheduleProperty(
            duration_in_seconds="0", expression="rate(5 minutes)")
        vpc_config = synthetics.CfnCanary.VPCConfigProperty(
            vpc_id=vpc.vpc_id, subnet_ids=subnet_ids, security_group_ids=[synthetics_security_group.security_group_id])
        topic = sns.Topic.from_topic_arn(
            self, f'Imported-{account_name}-Topic', topic_arn=f'arn:aws:sns:{region}:{account_id}:csbs-{account_name}-alerts')

        for obj in list:
            # Canaries
            synthetics.CfnCanary(
                self,
                f"{obj.name}",
                name=obj.name,
                code=obj.code,
                execution_role_arn=synthetics_role.role_arn,
                artifact_s3_location=f's3://{cloudwatch_results_bucket.bucket_name}/canary/{obj.key}',
                runtime_version="syn-python-selenium-1.0",
                schedule=schedule,
                start_canary_after_creation=True,
                vpc_config=vpc_config)
            # Alarms
            metric = cloudwatch.Metric(
                namespace="CloudWatchSynthetics",
                metric_name="SuccessPercent",
                dimensions=dict(CanaryName=f"{obj.name}"),
                period=cdk.Duration.minutes(5)
            )

            alarm = cloudwatch.Alarm(self, f"{obj.name}-Alarm",
                                     alarm_name=f"{environment}-Alfresco-{obj.key}-Unhealthy-API-Endpoint",
                                     metric=metric,
                                     threshold=85,
                                     evaluation_periods=3,
                                     datapoints_to_alarm=2,
                                     statistic="Average",
                                     alarm_description="Synthetics alarm metric: SuccessPercent LessThanThreshold 90",
                                     comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
                                     treat_missing_data=cloudwatch.TreatMissingData.IGNORE
                                     )
            alarm.add_alarm_action(cw_actions.SnsAction(topic))
