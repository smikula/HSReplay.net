"""Minimalist Lambda Handlers

This module represents our most mission critical code and has minimal dependencies.

Specific design considerations:
	- It is designed to not require DB connectivity
	- It does not bootstrap the Django machinery
	- It does not depend on hsreplaynet.* modules
	- It makes minimal assumptions about the structure of the data it receives

These design considerations mean this lambda can be deployed on a different cycle than
the rest of the hsreplaynet codebase.
"""
import shortuuid
import json
from datetime import datetime

try:
	# boto3 is provided automatically by the lambda runtime
	import boto3
	s3 = boto3.client('s3')
except ImportError:
	s3 = object()

S3_RAW_LOG_UPLOAD_BUCKET = "hsreplaynet-raw-log-uploads"


def generate_log_upload_address_handler(event, context):
	upload_uuid = shortuuid.uuid()
	ts = datetime.now()
	yyyymmddHHMM = ts.strftime("%Y/%m/%d/%H/%M")

	s3_descriptor_key = "raw/%s/%s/descriptor.json" % (yyyymmddHHMM, upload_uuid)
	# S3 only triggers downstream lambdas for PUTs suffixed with '...power.log'
	s3_powerlog_key = "raw/%s/%s/power.log" % (yyyymmddHHMM, upload_uuid)

	descriptor = {"shortid": upload_uuid}
	descriptor.update(event)

	s3.put_object(ACL='private',
				  Key=s3_descriptor_key,
				  Body=json.dumps(descriptor).encode("utf8"),
				  Bucket=S3_RAW_LOG_UPLOAD_BUCKET)

	descriptor_read_expiration = 60 * 60 * 24 * 7
	# 7 days so clients can debug missing replays
	# Authorization errors and other messages will be written back to the descriptor
	presigned_descriptor_url = s3.generate_presigned_url('get_object',
							  Params={'Bucket':S3_RAW_LOG_UPLOAD_BUCKET,
									  'Key':s3_descriptor_key},
							  ExpiresIn=descriptor_read_expiration,
							  HttpMethod='GET')

	log_put_expiration = 60 * 60 * 24
	# Only one day, since if it hasn't been used by then it's unlikely to be used.
	presigned_put_url = s3.generate_presigned_url('put_object',
							  Params={'Bucket':S3_RAW_LOG_UPLOAD_BUCKET,
									  'Key':s3_powerlog_key},
							  ExpiresIn=log_put_expiration,
							  HttpMethod='PUT')

	return {
		"get_descriptor_url" : presigned_descriptor_url,
		"put_raw_log_url" : presigned_put_url,
		"replay_uuid": upload_uuid
	}



