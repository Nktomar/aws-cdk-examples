
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

## Throttle Limits and Capacity

This stack implements AWS Well-Architected Framework best practice **REL05-BP02: Throttle requests** with multi-layered throttling to protect against resource exhaustion:

### Configured Throttle Limits

#### API Gateway Stage Throttling
- **Rate Limit**: 100 requests per second (sustained)
- **Burst Limit**: 200 requests (temporary spike capacity)
- **Behavior**: Returns `429 Too Many Requests` when exceeded
- **Purpose**: Protects backend Lambda and DynamoDB from overload

#### Usage Plan Throttling (Per Consumer)
- **Standard Tier**: 50 RPS, 100 burst, 10k/day quota
- **Premium Tier**: 100 RPS, 200 burst, 50k/day quota
- **Behavior**: Returns `429 Too Many Requests` when consumer exceeds their tier limits
- **Purpose**: Prevents single consumer from impacting others

#### AWS WAF Rate Limiting
- **Rate Limit**: 2000 requests per 5 minutes per IP address
- **Behavior**: Returns `403 Forbidden` when exceeded
- **Purpose**: Protects against DDoS attacks and malicious traffic from individual sources

#### Lambda Reserved Concurrency
- **Concurrent Executions**: 100 maximum
- **CloudWatch Alarm**: Triggers at 80 concurrent executions (80% threshold)
- **Purpose**: Prevents consuming all account-level Lambda concurrency (default 1000 per region)

### Capacity Planning

The current configuration supports:
- **Sustained Traffic**: 100 requests/second (stage limit)
- **Per-Consumer Traffic**: 50 RPS (Standard) or 100 RPS (Premium)
- **Burst Traffic**: 200 requests (short duration)
- **Concurrent Processing**: Up to 100 Lambda executions
- **DynamoDB**: On-demand capacity mode (auto-scales)

### Load Testing Recommendations

Before increasing throttle limits, perform load testing to validate capacity:

1. **Install Artillery** (Node.js load testing tool):
   ```bash
   npm install -g artillery
   ```

2. **Create test configuration** (`artillery-config.yml`):
   ```yaml
   config:
     target: "https://YOUR_API_GATEWAY_URL"
     phases:
       - duration: 60
         arrivalRate: 50
         name: "Warm up"
       - duration: 120
         arrivalRate: 100
         name: "Sustained load"
       - duration: 60
         arrivalRate: 150
         name: "Spike test"
     http:
       headers:
         x-api-key: "YOUR_API_KEY_VALUE"
   scenarios:
     - name: "POST request"
       flow:
         - post:
             url: "/"
             json:
               year: "2023"
               title: "Load Test"
               id: "{{ $randomString() }}"
   ```

3. **Run load test**:
   ```bash
   artillery run artillery-config.yml
   ```

4. **Monitor during test**:
   - CloudWatch Lambda metrics (concurrent executions, duration, errors)
   - API Gateway metrics (4xx/5xx errors, latency, count)
   - DynamoDB metrics (consumed capacity, throttled requests)
   - WAF metrics (blocked/allowed requests)
   - Usage plan metrics (per-consumer throttling)

5. **Analyze results**:
   - Verify 429 responses when exceeding limits
   - Check Lambda concurrency stays below 100
   - Confirm no DynamoDB throttling
   - Validate P99 latency remains acceptable
   - Verify per-consumer limits work correctly

### Increasing Throttle Limits

To increase limits safely:

1. **Verify current capacity** through load testing
2. **Update CDK stack** with new limits:
   ```python
   # In apigw_http_api_lambda_dynamodb_python_cdk_stack.py
   
   # Stage throttling
   throttling_rate_limit=200,  # Increase from 100
   throttling_burst_limit=400,  # Increase from 200
   
   # Usage plans
   standard_usage_plan = api.add_usage_plan(
       throttle=apigw_.ThrottleSettings(
           rate_limit=100,  # Increase from 50
           burst_limit=200,  # Increase from 100
       ),
   )
   
   # Lambda concurrency
   reserved_concurrent_executions=200,  # Increase from 100
   ```
3. **Redeploy**: `cdk deploy`
4. **Re-test** with higher load to validate
5. **Update documentation** with new tested limits

**Important**: Always ensure Lambda reserved concurrency and API Gateway throttle limits are aligned to prevent Lambda throttling errors.

## Monitoring and Logs

After deployment, you can access logs and traces through:
- **Lambda Logs**: CloudWatch Logs → Log group `/aws/lambda/apigw_handler`
- **API Gateway Logs**: CloudWatch Logs → Log group created by the stack
- **VPC Flow Logs**: CloudWatch Logs → Log group created by the stack
- **CloudTrail**: S3 bucket configured in your CloudTrail trail
- **X-Ray Traces**: AWS X-Ray console → Service map and trace analysis
- **CloudWatch ServiceLens**: Integrated view of traces, metrics, logs, and alarms
- **Usage Plan Metrics**: API Gateway console → Usage Plans → View metrics per API key
- **WAF Logs**: AWS WAF console → Sampled requests and blocked traffic

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

### Monitoring Throttled Requests

Monitor throttling behavior in CloudWatch:
- **API Gateway**: `4XXError` metric (includes 429 responses)
- **Lambda**: `ConcurrentExecutions` metric with alarm at 80
- **WAF**: `BlockedRequests` metric for rate-limited IPs
- **Usage Plans**: Per-consumer throttling metrics in API Gateway console

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
