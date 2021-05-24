# -*- coding: utf-8 -*-
"""Define the csbs-cdk-cw-syn lambda logic."""
from __future__ import annotations

import os
from typing import Any, Dict

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
logger = Logger(service="", level=LOG_LEVEL)

metrics = Metrics(namespace="", service="")
tracer = Tracer(service="")


@metrics.log_metrics(capture_cold_start_metric=True)
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Handle invocations of """
    # Log the updated references from the event
    logger.info("EVENT: (%s)" % event)
    logger.info("CONTEXT: (%s)" % context)

    metrics.add_metric(name="TotalInvocations", unit=MetricUnit.Count, value=1)

    test_key = event.get("test_request")
    if test_key:
        logger.info("This is a test execution of the  function")
        return {"status": "TEST_RUN"}

    try:
        session = boto3.session.Session()
        logger.info("Boto3 session region: (%s)" % session.region_name)
        metrics.add_metric(name="SuccessfulInvocations", unit=MetricUnit.Count, value=1)
        return {"success": True, "status": "MONEY"}
    except Exception as e:
        logger.error(f"Error encountered invoking: .")
        metrics.add_metric(name="FailedInvocations", unit=MetricUnit.Count, value=1)
        return {"success": False, "status": "PROBLEMS"}
