
# AWS API Gateway HTTP API to AWS Lambda in VPC to DynamoDB CDK Python Sample!


## Overview

Creates an [AWS Lambda](https://aws.amazon.com/lambda/) function writing to [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) and invoked by [Amazon API Gateway](https://aws.amazon.com/api-gateway/) REST API. 

![architecture](docs/architecture.png)

## Prerequisites

### AWS CloudTrail
This application requires AWS CloudTrail to be enabled in your AWS account for comprehensive security logging. CloudTrail captures API-level activity for all resources created by this stack.

Ensure you have:
- An organization-wide CloudTrail trail, OR
- A CloudTrail trail configured for the deployment account with management events enabled
- CloudTrail logs stored in S3 with appropriate retention policies (recommended: 1-7 years)

### Logging and Monitoring
This stack implements AWS Well-Architected Framework best practices for logging:
- **Lambda Function Logs**: Retained for 1 year in CloudWatch Logs
- **API Gateway Access Logs**: Retained for 1 year with detailed request information
- **VPC Flow Logs**: Enabled for all network traffic, retained for 1 year
- **DynamoDB**: Point-in-time recovery and streams enabled for audit trails

### Distributed Tracing
This stack implements AWS Well-Architected Framework best practices for observability:
- **AWS X-Ray**: End-to-end tracing enabled across API Gateway, Lambda, and DynamoDB
- **Service Map**: Visualize request flows and identify performance bottlenecks
- **Trace Analysis**: Debug errors and latency issues with detailed subsegment data

## Setup

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Deploy
At this point you can deploy the stack. 

Using the default profile

```
$ cdk deploy
```

With specific profile

```
$ cdk deploy --profile test
```

After deployment, note the API key IDs from the stack outputs. You'll need these to retrieve the actual API key values.

## API Key Management

This API requires an API key for all requests. Two usage tiers are available:

### Retrieving API Keys

After deployment, retrieve the API key values using the AWS CLI:

```bash
# Get Standard tier API key
aws apigateway get-api-key --api-key <StandardApiKeyId> --include-value --query 'value' --output text

# Get Premium tier API key
aws apigateway get-api-key --api-key <PremiumApiKeyId> --include-value --query 'value' --output text
```

Replace `<StandardApiKeyId>` and `<PremiumApiKeyId>` with the values from the stack outputs.

### Usage Tiers

#### Standard Tier
- **Rate Limit**: 50 requests per second
- **Burst Limit**: 100 requests
- **Daily Quota**: 10,000 requests per day
- **Use Case**: Development, testing, low-volume applications

#### Premium Tier
- **Rate Limit**: 100 requests per second
- **Burst Limit**: 200 requests
- **Daily Quota**: 50,000 requests per day
- **Use Case**: Production applications, high-volume consumers

### Making API Requests

Include the API key in the `x-api-key` header:

```bash
curl -X POST https://YOUR_API_GATEWAY_URL/ \
  -H "x-api-key: YOUR_API_KEY_VALUE" \
  -H "Content-Type: application/json" \
  -d '{
    "year": "2023",
    "title": "Test Movie",
    "id": "12"
  }'
```

### Error Responses

- **403 Forbidden**: Missing or invalid API key
- **429 Too Many Requests**: Rate limit or quota exceeded for your usage plan

## After Deploy
Navigate to AWS API Gateway console and test the API with below sample data 
```json
{
    "year":"2023", 
    "title":"kkkg",
    "id":"12"
}
```

**Important**: Remember to include the `x-api-key` header with your API key value.

You should get below response 

```json
{"message": "Successfully inserted data!"}
```

## Monitoring and Logs

After deployment, you can access logs and traces through:
- **Lambda Logs**: CloudWatch Logs → Log group `/aws/lambda/apigw_handler`
- **API Gateway Logs**: CloudWatch Logs → Log group created by the stack
- **VPC Flow Logs**: CloudWatch Logs → Log group created by the stack
- **CloudTrail**: S3 bucket configured in your CloudTrail trail
- **X-Ray Traces**: AWS X-Ray console → Service map and trace analysis
- **CloudWatch ServiceLens**: Integrated view of traces, metrics, logs, and alarms
- **Usage Plan Metrics**: API Gateway console → Usage Plans → View metrics per API key

Logs include structured JSON format with security context (request ID, source IP, user agent) for security investigations.

### Viewing X-Ray Traces

1. Navigate to AWS X-Ray console
2. View the Service Map to see request flows: API Gateway → Lambda → DynamoDB
3. Click on traces to see detailed timing and subsegments
4. Use CloudWatch ServiceLens for integrated observability

### Monitoring API Key Usage

Monitor per-consumer usage in the API Gateway console:
1. Navigate to API Gateway → Usage Plans
2. Select a usage plan (Standard or Premium)
3. View API Keys tab to see associated consumers
4. Click on an API key to view usage metrics and quota consumption

## Cleanup 
Run below script to delete AWS resources created by this sample stack.
```
cdk destroy
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
