"""
Minimalist Lambda Handlers

This module represents our most mission critical code and has minimal dependencies.

Specific design considerations:
- It is designed to not require DB connectivity
- It does not bootstrap the Django machinery
- It does not depend on hsreplaynet.* modules
- It makes minimal assumptions about the structure of the data it receives

These design considerations mean this lambda can be deployed on a different cycle than
the rest of the hsreplaynet codebase.
"""
import json
import shortuuid
from base64 import b64decode
from datetime import datetime


try:
	import boto3
	S3 = boto3.client("s3")
except ImportError:
	S3 = None

S3_RAW_LOG_UPLOAD_BUCKET = "hsreplaynet-raw-log-uploads"


def generate_log_upload_address_handler(event, context):
	gateway_headers = event["headers"]

	if "Authorization" not in gateway_headers:
		raise Exception("The Authorization Header is required.")

	auth_components = gateway_headers["Authorization"].split()
	if len(auth_components) != 2:
		raise Exception("Authorization header must have a scheme and a token.")

	auth_token = auth_components[1]

	upload_shortid = shortuuid.uuid()
	ts = datetime.now()
	ts_path = ts.strftime("%Y/%m/%d/%H/%M")

	upload_metadata = json.loads(b64decode(event.pop("body")).decode("utf8"))

	descriptor = {"shortid": upload_shortid}
	descriptor["upload_metadata"] = upload_metadata
	descriptor["source_ip"] = event["source_ip"]
	descriptor["gateway_headers"] = gateway_headers

	s3_descriptor_key = "raw/%s/%s/%s/descriptor.json" % (ts_path, auth_token, upload_shortid)
	# S3 only triggers downstream lambdas for PUTs suffixed with '...power.log'
	s3_powerlog_key = "raw/%s/%s/%s/power.log" % (ts_path, auth_token, upload_shortid)

	descriptor["event"] = event

	S3.put_object(
		ACL="private",
		Key=s3_descriptor_key,
		Body=json.dumps(descriptor).encode("utf8"),
		Bucket=S3_RAW_LOG_UPLOAD_BUCKET
	)

	descriptor_read_expiration = 60 * 60 * 24 * 7
	# 7 days so clients can debug missing replays
	# Authorization errors and other messages will be written back to the descriptor
	presigned_descriptor_url = S3.generate_presigned_url(
		"get_object",
		Params={
			"Bucket": S3_RAW_LOG_UPLOAD_BUCKET,
			"Key": s3_descriptor_key
		},
		ExpiresIn=descriptor_read_expiration,
		HttpMethod="GET"
	)

	log_put_expiration = 60 * 60 * 24
	# Only one day, since if it hasn't been used by then it's unlikely to be used.
	presigned_put_url = S3.generate_presigned_url(
		"put_object",
		Params={
			"Bucket": S3_RAW_LOG_UPLOAD_BUCKET,
			"Key": s3_powerlog_key
		},
		ExpiresIn=log_put_expiration,
		HttpMethod="PUT"
	)

	return {
		"descriptor_url": presigned_descriptor_url,
		"put_url": presigned_put_url,
		"upload_shortid": upload_shortid,
	}
