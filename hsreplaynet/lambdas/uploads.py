import json
import logging
import tempfile
import re
from datetime import datetime
from base64 import b64decode
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework.test import APIRequestFactory
from hsreplaynet.api.views import UploadEventViewSet
from hsreplaynet.uploads.models import UploadEvent, UploadEventType, _generate_upload_key
from hsreplaynet.uploads.processing import queue_upload_event_for_processing
from hsreplaynet.utils import instrumentation, aws


def emulate_api_request(path, data, headers):
	"""
	Emulates an API request from the API gateway's data.
	"""
	factory = APIRequestFactory()
	request = factory.post(path, data, format="json", **headers)
	SessionMiddleware().process_request(request)
	return request


@instrumentation.lambda_handler
def process_s3_create_handler(event, context):
	"""
	A handler that is triggered whenever a "..power.log" suffixed object is created in S3.
	"""
	logger = logging.getLogger("hsreplaynet.lambdas.process_s3_create_handler")
	logger.info("***** EVENT INFO *****")
	logger.info(json.dumps(event, sort_keys=True, indent=4))

	s3_record = event["Records"][0]["s3"]
	raw_bucket = s3_record["bucket"]["name"]
	raw_key = s3_record["object"]["key"]
	logger.info("S3 Upload Event >> Bucket: %s Key: %s ", raw_bucket, raw_key)
	process_raw_upload(raw_bucket, raw_key)


@instrumentation.lambda_handler
def process_raw_upload_sns_handler(event, context):
	"""
	A handler that subscribes to an SNS queue to support reprocessing of raw log uploads.
	"""
	logger = logging.getLogger("hsreplaynet.lambdas.process_raw_upload_sns_handler")

	message = json.loads(event["Records"][0]["Sns"]["Message"])
	logger.info("SNS message: %r", message)
	raw_bucket = message["raw_bucket"]
	raw_key = message["raw_key"]
	process_raw_upload(raw_bucket, raw_key)


def process_raw_upload(raw_bucket, raw_key):
	"""A method for processing a raw upload in S3.

	This will usually be invoked by process_s3_create_handler, however
	it can also be invoked when a raw upload is queued for reprocessing via SNS.
	"""
	logger = logging.getLogger("hsreplaynet.lambdas.process_raw_upload")
	pattern = r"raw/(?P<ts>\d{4}/\d{2}/\d{2}/\d{2}/\d{2})/(?P<shortid>\w{22})\.power.log"
	match = re.match(pattern, raw_key)

	if not match:
		logger.info("ERROR: We failed to match against the S3 Key - no processing was done.")
		return

	timestamp, shortid = match.groups()
	ts = datetime.strptime(timestamp, "%Y/%m/%d/%H/%M")

	logger.info("Timestamp: %s", timestamp)
	logger.info("ShortID: %s", shortid)

	descriptor_key = "raw/%s/%s.descriptor.json" % (timestamp, shortid)
	logger.info("Descriptor Key: %s", descriptor_key)

	obj = aws.S3.get_object(Bucket=raw_bucket, Key=descriptor_key)
	descriptor = json.load(obj["Body"])

	logger.info("***** COMPLETE DESCRIPTOR *****")
	logger.info(json.dumps(descriptor, sort_keys=True, indent=4))

	new_key = _generate_upload_key(ts, shortid)
	new_bucket = settings.AWS_STORAGE_BUCKET_NAME

	# First we copy the log to the proper location
	copy_source = "%s/%s" % (raw_bucket, raw_key)

	logger.info("*** COPY RAW LOG TO NEW LOCATION ***")
	logger.info("SOURCE: %s" % copy_source)
	logger.info("DESTINATION: %s/%s" % (new_bucket, new_key))

	aws.S3.copy_object(
		Bucket=new_bucket,
		Key=new_key,
		CopySource=copy_source,
	)

	# Then we build the request and send it to DRF
	# If "file" is a string, DRF will interpret as a S3 Key
	upload_metadata = descriptor["upload_metadata"]
	upload_metadata["shortid"] = descriptor["shortid"]
	upload_metadata["file"] = new_key
	upload_metadata["type"] = int(UploadEventType.POWER_LOG)

	logger.info("***** UPLOADED METADATA *****")
	logger.info(json.dumps(upload_metadata, sort_keys=True, indent=4))

	gateway_headers = descriptor["gateway_headers"]
	headers = {
		"HTTP_X_FORWARDED_FOR": descriptor["source_ip"],
		"HTTP_AUTHORIZATION": gateway_headers["Authorization"],
		"HTTP_X_API_KEY": gateway_headers["X-Api-Key"],
	}

	logger.info("***** HEADERS *****")
	logger.info(json.dumps(headers, sort_keys=True, indent=4))

	path = descriptor["event"]["path"]
	logger.info("REQUEST Path: %s", path)

	request = emulate_api_request(path, upload_metadata, headers)

	try:
		result = create_upload_event_from_request(request)
	except Exception as e:
		# If DRF fails: delete the copy of the log, and update the descriptor.
		# We update the descriptor as a way to pass status
		# info back to the client that uploaded it.
		logger.exception(e)
		aws.S3.delete_object(Bucket=new_bucket, Key=new_key)

		result_exception_json = json.loads(str(e))
		descriptor["UPLOAD_ERROR"] = result_exception_json
		descriptor["UPLOAD_ERROR_TS"] = datetime.now().isoformat()
		aws.S3.put_object(
			Key=descriptor_key,
			Body=json.dumps(descriptor).encode("utf8"),
			Bucket=raw_bucket,
		)

		raise
	else:
		logger.info("Create Upload Event Request Succeeded.")
		logger.info("Raw log and descriptor will be deleted now.")

		# If DRF returns success, then we delete the descriptor and log from raw uploads
		aws.S3.delete_objects(
			Bucket=raw_bucket,
			Delete={
				"Objects": [{"Key": raw_key}, {"Key": descriptor_key}]
			}
		)

	logger.info("Processing Complete.")
	return result


@instrumentation.lambda_handler
def create_power_log_upload_event_handler(event, context):
	"""
	A handler for creating UploadEvents via Lambda.
	"""
	logger = logging.getLogger("hsreplaynet.lambdas.create_power_log_upload_event_handler")

	body = event.pop("body")
	logger.info("source_ip=%r, query=%r", event["source_ip"], event["query"])

	body = b64decode(body)
	instrumentation.influx_metric("raw_power_log_upload_num_bytes", {"size": len(body)})

	file = tempfile.NamedTemporaryFile(mode="r+b", suffix=".log")
	file.write(body)
	file.flush()
	file.seek(0)

	data = event["query"]
	data["file"] = file
	data["type"] = int(UploadEventType.POWER_LOG)

	gateway_headers = event["headers"]
	headers = {
		"HTTP_X_FORWARDED_FOR": event["source_ip"],
		"HTTP_AUTHORIZATION": gateway_headers["Authorization"],
		"HTTP_X_API_KEY": gateway_headers["X-Api-Key"],
	}

	path = event["path"]
	request = emulate_api_request(path, data, headers)
	return create_upload_event_from_request(request)


def create_upload_event_from_request(request):
	logger = logging.getLogger("hsreplaynet.lambdas.create_upload_event_from_request")
	view = UploadEventViewSet.as_view({"post": "create"})

	response = view(request)
	response.render()
	logger.info("Response (code=%r): %s", response.status_code, response.content)

	if response.status_code != 201:
		result = {
			"result_type": "VALIDATION_ERROR",
			"status_code": response.status_code,
			"body": response.content,
		}
		raise Exception(json.dumps(result))

	# Extract the upload_event from the response and queue it for processing
	upload_event_id = response.data["id"]
	logger.info("Created UploadEvent %r", upload_event_id)
	queue_upload_event_for_processing(upload_event_id)

	return {
		"result_type": "SUCCESS",
		"body": response.content,
	}


@instrumentation.lambda_handler
def process_upload_event_handler(event, context):
	"""
	This handler is triggered by SNS whenever someone
	publishes a message to the SNS_PROCESS_UPLOAD_EVENT_TOPIC.
	"""
	logger = logging.getLogger("hsreplaynet.lambdas.process_upload_event_handler")

	message = json.loads(event["Records"][0]["Sns"]["Message"])
	logger.info("SNS message: %r", message)

	# This should never raise DoesNotExist.
	# If it does, the previous lambda made a terrible mistake.
	upload = UploadEvent.objects.get(id=message["id"])

	logger.info("Processing %r (%s)", upload.shortid, upload.status.name)
	upload.process()
	logger.info("Status: %s", upload.status.name)
