from aws_cdk import core as cdk

from .stacks import SyntheticsStack
from typing import Any, Dict, List, Optional

# class LambdaStage(cdk.Stage):
#    """Define the lambda stage."""
#
#    def __init__(self, scope: cdk.Construct, construct_id: str, lambda_name: str, **kwargs) -> None:
#        """Initialize the lambda stage."""
#        super().__init__(scope, construct_id, **kwargs)
#        service = LambdaStack(
#            self, f"{lambda_name.title()}Stage", "CloudWatchSynthetics")
#        #self.url_output = service.url_output


class Synthetics(cdk.Stage):
    """Define the Synthethics stage."""

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
        """Initialize the lambda stage."""
        super().__init__(scope, construct_id, **kwargs)
        service = SyntheticsStack(
            self,
            f"{name.title()}",
            "CloudWatchSynthetics",
            account_id=account_id,
            account_name=account_name,
            region=region,
            vpc_id=vpc_id,
            subnet_ids=subnet_ids,
            environment=environment,
        )
        # self.url_output = service.url_output
