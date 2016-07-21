import json

try:
	import boto3
	S3 = boto3.client("s3")
	SNS = boto3.client("sns")
except ImportError:
	S3 = None
	SNS = None


def publish_sns_message(topic, message):
	return SNS.publish(
				TopicArn=topic,
				Message=json.dumps({"default": json.dumps(message)}),
				MessageStructure="json"
			)


def list_all_objects_in(bucket, prefix=None):
	list_response = S3.list_objects_v2(
		Bucket = bucket,
		Prefix = prefix,
	)
	objects = list_response["Contents"]
	while len(objects):
		yield objects.pop(0)
		if list_response["IsTruncated"] and len(objects) == 0:
			list_response = S3.list_objects_v2(
				Bucket = bucket,
				Prefix = prefix,
				ContinuationToken = list_response["NextContinuationToken"]
			)
			objects += list_response["Contents"]
