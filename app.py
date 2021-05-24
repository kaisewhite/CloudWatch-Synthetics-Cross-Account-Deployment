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

import os
from typing import Dict

from aws_cdk import core as cdk

from infra.pipeline import CdkPipelineStack

# Define application level attributes.
PIPELINE_REGION: str = os.environ.get("CDK_PIPELINE_REGION", "us-east-1")
PIPELINE_ID: str = os.environ.get(
    "CDK_PIPELINE_ID", "ses-cloudwatch-synthetics")
MANAGED_BY: str = os.environ.get("CDK_MANAGED_BY", "CDK")
REPO: str = os.environ.get("CDK_REPO", "ses-cloudwatch-synthetics")

MGMT_PIPELINE_ACCOUNT: str = os.environ.get(
    "CDK_MGMT_PIPELINE_ACCOUNT", "************")
SANDBOX_TARGET_ACCOUNT: str = os.environ.get(
    "CDK_SANDBOX_ACCOUNT", "************")
NONPROD_TARGET_ACCOUNT: str = os.environ.get(
    "CDK_NONPROD_ACCOUNT", "************")
PREPROD_TARGET_ACCOUNT: str = os.environ.get(
    "CDK_PREPROD_ACCOUNT", "************")

GLOBAL_CONFIG: Dict[str, str] = {
    "namespace": os.environ.get("CDK_APP_NAMESPACE", "csbs"),
    "service": os.environ.get("CDK_SERVICE", "csbs"),
}
APP_TAGS: Dict[str, str] = {
    **{k.title(): v for k, v in GLOBAL_CONFIG.items()},
    **{
        # Add additional application level tags here.
        "managed-by": MANAGED_BY,
        "repo:name": REPO,
        "owner": "",
        "creator": "",
        "project": "",
        "account:name": "management",
        "account:number": "************"
    },
}

# Instantiate the main application.
app = cdk.App()

# Define environments.
management_env = cdk.Environment(
    account=MGMT_PIPELINE_ACCOUNT, region=PIPELINE_REGION)
sbx_env = cdk.Environment(
    account=SANDBOX_TARGET_ACCOUNT, region=PIPELINE_REGION)
nonprod_env = cdk.Environment(
    account=NONPROD_TARGET_ACCOUNT, region=PIPELINE_REGION)

# Infra CDK pipeline
CdkPipelineStack(
    app,
    PIPELINE_ID,
    env=management_env,
    tags=APP_TAGS,
    # target_account=SANDBOX_TARGET_ACCOUNT,
)

# CdkPipelineStack(
#    app,
#    PIPELINE_ID,
#    env=management_env,
#    tags=APP_TAGS,
#    target_account=NONPROD_TARGET_ACCOUNT,
# )

app.synth()
