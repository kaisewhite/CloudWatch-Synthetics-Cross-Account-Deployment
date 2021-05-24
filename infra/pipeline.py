# -*- coding: utf-8 -*-
"""Define the Pipeline stack for use with ."""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codecommit as commit
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as cpactions
from aws_cdk import aws_iam as iam
from aws_cdk import core
from aws_cdk import core as cdk
from aws_cdk import pipelines

from .stages import Synthetics


class CdkPipelineStack(cdk.Stack):
    """Define the Pipeline stack infrastructure and stage components."""

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        # target_account: str,
        # target_region: str = "us-east-1",
        default_branch: str = "master",
        prefix: str = "csbs",
        suffix: str = "",
        **kwargs,
    ) -> None:
        """Initialize the Pipeline stack."""
        pipeline_name: str = kwargs.pop(
            "pipeline_name", "ses-cloudwatch-synthetics")
        cross_account_keys: bool = kwargs.pop("cross_account_keys", True)
        target_repo: str = kwargs.pop(
            "target_repo", "arn:aws:codecommit:us-east-1:************:ses-cloudwatch-synthetics"
        )

        super().__init__(scope, construct_id, **kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        repo = commit.Repository.from_repository_arn(
            self, f"{prefix}Repository{suffix}", target_repo)
        pipeline_service_principal = iam.ServicePrincipal(
            "codepipeline.amazonaws.com")
        pipeline_role = iam.Role(
            self,
            f"{prefix}PipelineRole{suffix}",
            role_name=f"{pipeline_name}-role",
            assumed_by=pipeline_service_principal,
        )
        pipeline_role.add_to_policy(iam.PolicyStatement(
            resources=["*"], actions=["ecr:GetAuthorizationToken"]))
        code_pipeline = codepipeline.Pipeline(
            self,
            f"{prefix}BasePipeline{suffix}",
            role=pipeline_role,
            restart_execution_on_update=True,
            cross_account_keys=cross_account_keys,
            pipeline_name=pipeline_name,
        )

        build_role_policy = iam.PolicyStatement(
            resources=["*"], actions=["ecr:GetAuthorizationToken"])
        pipeline = pipelines.CdkPipeline(
            self,  # Scope (Construct).
            f"{prefix}CdkPipeline{suffix}",  # The CDK ID.
            # Artifact to hold the assembly for synth action.
            cloud_assembly_artifact=cloud_assembly_artifact,
            code_pipeline=code_pipeline,
            # Whether or not the pipeline can modify itself.
            self_mutating=True,
            source_action=cpactions.CodeCommitSourceAction(
                output=source_artifact,  # Output Artifact.
                repository=repo,  # IRepository.
                branch=default_branch,
                # Can be EVENTS, POLL, or NONE.
                trigger=cpactions.CodeCommitTrigger.EVENTS,
                role=pipeline_role,
                # The name of the action.  Must be unique within a single Stage.
                action_name="Source",
            ),
            synth_action=pipelines.SimpleSynthAction(
                source_artifact=source_artifact,
                role_policy_statements=[build_role_policy],
                environment=codebuild.BuildEnvironment(privileged=True),
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_commands=[
                    "npm install -g aws-cdk cdk-assume-role-credential-plugin",
                    "pip3 install --upgrade wheel setuptools pip",
                    "pip3 --disable-pip-version-check --no-cache-dir install --pre --upgrade poetry",
                    "poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi",
                ],
                build_commands=[
                    # "python3 -m venv env",
                    # "source env/bin/activate",
                    # "make safety",
                    # "make ci-test",
                    # "aws ecr get-login --no-include-email --region us-east-1",
                    # "echo $DOCKER_PASSWORD | docker login -u $DOCKER_USER --password-stdin",
                ],
                synth_command="cdk synth",
            ),
        )
        repo.grant_read(pipeline.code_pipeline.role)
        repo.grant_pull(pipeline.code_pipeline.role)

        # Support Stacks
        # sandbox_test = LambdaStage(
        #    self, "LambdaStage", lambda_name="CloudWatchSynthetics", env={"account": target_account, "region": target_region}
        # )

        pipeline.add_application_stage(Synthetics(
            self,
            "SES-Sandbox",
            name="Cloudwatch-Synthetics",
            account_name="sandbox",
            account_id="************",
            region="us-east-1",
            environment="sandbox",  # Ex: dev, qa, test, stage, hotfix
            vpc_id="vpc-03da4c32bdfe44451",
            subnet_ids=["subnet-0343c1b675f340001",
                        "subnet-0f630a9970b461e7a"],
            env={"account": "************",
                 "region": "us-east-1"},  # Target Account
        ))

        pipeline.add_application_stage(Synthetics(
            self,
            "SES-Dev",  # Project-Environment
            name="Cloudwatch-Synthetics",
            account_name="nonprod",
            account_id="************",
            region="us-east-1",
            environment="dev",  # Ex: dev, qa, test, stage, hotfix
            vpc_id="vpc-0845cc5232f7b37ed",
            subnet_ids=["subnet-062c110ab35d1d77f",
                        "subnet-04dd2f7d9ed7eefa5"],
            env={"account": "************", "region": "us-east-1"},
        ))

        pipeline.add_application_stage(Synthetics(
            self,
            "SES-Qa",  # Project-Environment
            name="Cloudwatch-Synthetics",
            account_name="nonprod",
            account_id="************",
            region="us-east-1",
            environment="qa",  # Ex: dev, qa, test, stage, hotfix
            vpc_id="vpc-01c22840c3fcfb0fb",
            subnet_ids=["subnet-05ebf645231a1b8cc",
                        "subnet-00999de71ef4580e9"],
            env={"account": "************", "region": "us-east-1"},
        ))

        pipeline.add_application_stage(Synthetics(
            self,
            "SES-Test",  # Project-Environment
            name="Cloudwatch-Synthetics",
            account_name="nonprod",
            account_id="************",
            region="us-east-1",
            environment="test",  # Ex: dev, qa, test, stage, hotfix
            vpc_id="vpc-090876ecb5fe52b6c",
            subnet_ids=["subnet-0c28f225726411559",
                        "subnet-0f610f2b6eb809cfd"],
            env={"account": "************", "region": "us-east-1"},
        ))
#
        # pipeline.add_application_stage(Synthetics(
        #    self,
        #    "SES-Train",  # Project-Environment
        #    name="Cloudwatch-Synthetics",
        #    account_name="preprod",
        #    account_id="************",
        #    region="us-east-1",
        #    environment="train",  # Ex: dev, qa, test, stage, hotfix
        #    vpc_id="vpc-0fcf579746559e694",
        #    subnet_ids=["subnet-03cf4a8c7892c42d1",
        #                "subnet-00545a4f6a63d73ab"],
        #    env={"account": "************", "region": "us-east-1"},
        # ))
#
        # pipeline.add_application_stage(Synthetics(
        #    self,
        #    "SES-Stage",  # Project-Environment
        #    name="Cloudwatch-Synthetics",
        #    account_name="preprod",
        #    account_id="************",
        #    region="us-east-1",
        #    environment="stage",  # Ex: dev, qa, test, stage, hotfix
        #    vpc_id="vpc-07fe1dd1ef7d8bda0",
        #    subnet_ids=["subnet-00b1ae36fbcde9d04",
        #                "subnet-0ff95886822a30223"],
        #    env={"account": "************", "region": "us-east-1"},
        # ))
#
        # pipeline.add_application_stage(Synthetics(
        #    self,
        #    "SES-Hotfix",  # Project-Environment
        #    name="Cloudwatch-Synthetics",
        #    account_name="preprod",
        #    account_id="************",
        #    region="us-east-1",
        #    environment="hotfix",  # Ex: dev, qa, test, stage, hotfix
        #    vpc_id="vpc-0f53dc936f0f40ccf",
        #    subnet_ids=["subnet-02d3eb3305c6790a9",
        #                "subnet-09ff59fd05d30c6f7"],
        #    env={"account": "************", "region": "us-east-1"},
        # ))

        # pipeline.add_application_stage(Synthetics(
        #   self,
        #   "SES-Prod",  # Project-Environment
        #   name="Cloudwatch-Synthetics",
        #   account_name="prod",
        #   account_id="305666597712",
        #   region="us-east-1",
        #   environment="prod",  # Ex: dev, qa, test, stage, hotfix
        #   vpc_id="vpc-09a0b806a428804da",
        #   subnet_ids=["subnet-06d6ecffca0b50eff",
        #               "subnet-0526b18b2a2cc711f"],
        #   env={"account": "305666597712", "region": "us-east-1"},

        # ))
