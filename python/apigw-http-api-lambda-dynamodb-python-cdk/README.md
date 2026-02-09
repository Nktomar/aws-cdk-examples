
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

## After Deploy
Navigate to AWS API Gateway console and test the API with below sample data 
```json
{
    "year":"2023", 
    "title":"kkkg",
    "id":"12"
}
```

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

Logs include structured JSON format with security context (request ID, source IP, user agent) for security investigations.

### Viewing X-Ray Traces

1. Navigate to AWS X-Ray console
2. View the Service Map to see request flows: API Gateway → Lambda → DynamoDB
3. Click on traces to see detailed timing and subsegments
4. Use CloudWatch ServiceLens for integrated observability

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
