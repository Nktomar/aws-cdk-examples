# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json
import logging
import uuid
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch all supported libraries for X-Ray tracing
patch_all()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


def handler(event, context):
    # Extract security context
    request_id = context.request_id
    source_ip = event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown")
    user_agent = event.get("requestContext", {}).get("identity", {}).get("userAgent", "unknown")
    table = os.environ.get("TABLE_NAME")
    
    # Structured logging with security context
    log_context = {
        "request_id": request_id,
        "source_ip": source_ip,
        "user_agent": user_agent,
        "table_name": table
    }
    
    logger.info(json.dumps({
        **log_context,
        "event": "request_received",
        "has_body": bool(event.get("body"))
    }))
    
    if event["body"]:
        item = json.loads(event["body"])
        logger.info(json.dumps({
            **log_context,
            "event": "processing_payload",
            "item_id": item.get("id")
        }))
        year = str(item["year"])
        title = str(item["title"])
        id = str(item["id"])
        
        # DynamoDB operation will be automatically traced by X-Ray
        dynamodb_client.put_item(
            TableName=table,
            Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
        )
        logger.info(json.dumps({
            **log_context,
            "event": "data_inserted",
            "item_id": id
        }))
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
    else:
        logger.info(json.dumps({
            **log_context,
            "event": "no_payload_received"
        }))
        item_id = str(uuid.uuid4())
        
        # DynamoDB operation will be automatically traced by X-Ray
        dynamodb_client.put_item(
            TableName=table,
            Item={
                "year": {"N": "2012"},
                "title": {"S": "The Amazing Spider-Man 2"},
                "id": {"S": item_id},
            },
        )
        logger.info(json.dumps({
            **log_context,
            "event": "default_data_inserted",
            "item_id": item_id
        }))
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
