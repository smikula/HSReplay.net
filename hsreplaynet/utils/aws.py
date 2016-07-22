import json
from django.conf import settings

try:
	import boto3
	S3 = boto3.client("s3")
	SNS = boto3.client("sns")
	LAMBDA = boto3.client("lambda")
except ImportError:
	S3 = None
	SNS = None
	LAMBDA = None


def enable_processing_raw_uploads():
	processing_lambda = LAMBDA.get_function(FunctionName="ProcessS3CreateObjectV1")
	S3.put_bucket_notification_configuration(
		Bucket=settings.S3_RAW_LOG_UPLOAD_BUCKET,
		NotificationConfiguration={
			"LambdaFunctionConfigurations": [
				{
					"LambdaFunctionArn": processing_lambda["Configuration"]["FunctionArn"],
					"Events": [
						"s3:ObjectCreated:*"
					],
					"Id": "TriggerLambdaOnLogCreate",
					"Filter": {
						"Key": {
							"FilterRules": [
								{
									"Value": "power.log",
									"Name": "Suffix"
								}
							]
						}
					}
				}
			]
		}
	)


def disable_processing_raw_uploads():
	# Remove any existing event notification rules by
	# putting an empty configuration on the bucket
	S3.put_bucket_notification_configuration(
		Bucket=settings.S3_RAW_LOG_UPLOAD_BUCKET,
		NotificationConfiguration={}
	)


def publish_sns_message(topic, message):
	return SNS.publish(
		TopicArn=topic,
		Message=json.dumps({"default": json.dumps(message)}),
		MessageStructure="json"
	)


def list_all_objects_in(bucket, prefix=None):
	list_response = S3.list_objects_v2(
		Bucket=bucket,
		Prefix=prefix,
	)
	objects = list_response["Contents"]
	while objects:
		yield objects.pop(0)
		if list_response["IsTruncated"] and not objects:
			list_response = S3.list_objects_v2(
				Bucket=bucket,
				Prefix=prefix,
				ContinuationToken=list_response["NextContinuationToken"]
			)
			objects += list_response["Contents"]
