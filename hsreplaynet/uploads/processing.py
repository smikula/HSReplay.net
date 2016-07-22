"""
A module for scheduling UploadEvents to be processed or reprocessed.

For additional details see:
http://boto3.readthedocs.io/en/latest/reference/services/sns.html#SNS.Client.publish
"""
import logging
import os
from django.conf import settings
from django.utils.timezone import now
from hsreplaynet.uploads.models import UploadEvent
from hsreplaynet.utils.instrumentation import error_handler, influx_metric
from hsreplaynet.utils import aws

logger = logging.getLogger(__file__)


def queue_raw_uploads_for_processing():
	"""Requeue all raw logs to attempt processing them into UploadEvents.

	The primary use for this is for when we deploy code. The intended deploy process is:
		- Notify S3 to suspend triggering lambda upon log upload
		- Perform the Deploy
		- Notify S3 to resume triggering lambda upon log upload
		- Invoke this function to queue for processing any logs uploaded during the deploy

	This method can also be used to recover from a service outage.
	"""
	# Note, this method is intended to only be run in production.
	if settings.IS_RUNNING_LIVE:
		for object in aws.list_all_objects_in(settings.S3_RAW_LOG_UPLOAD_BUCKET, prefix="raw"):
			key = object["Key"]
			if key.endswith("power.log"):  # Don't queue the descriptor files, just the logs.

				message = {
					"raw_bucket": settings.S3_RAW_LOG_UPLOAD_BUCKET,
					"raw_key": key,
				}

				aws.publish_sns_message(settings.SNS_PROCESS_RAW_LOG_UPOAD_TOPIC, message)


def queue_upload_event_for_processing(upload_event_id):
	"""
	This method is used when UploadEvents are initially created.
	However it can also be used to requeue an UploadEvent to be
	processed again if an error was detected downstream that has now been fixed.
	"""
	if settings.IS_RUNNING_LIVE or settings.IS_RUNNING_AS_LAMBDA:
		if "TRACING_REQUEST_ID" in os.environ:
			token = os.environ["TRACING_REQUEST_ID"]
		else:
			# If this was re-queued manually the tracing ID may not be set yet.
			event = UploadEvent.objects.get(id=upload_event_id)
			token = str(event.token.key)

		message = {
			"id": upload_event_id,
			"token": token,
		}

		success = True
		try:
			logger.info("Submitting %r to SNS", message)
			response = aws.publish_sns_message(settings.SNS_PROCESS_UPLOAD_EVENT_TOPIC, message)
			logger.info("SNS Response: %s" % str(response))
		except Exception as e:
			logger.error("Exception raised.")
			error_handler(e)
			success = False
		finally:
			influx_metric(
				"queue_upload_event_for_processing",
				fields={"value": 1},
				timestamp=now(),
				tags={
					"success": success,
					"is_running_as_lambda": settings.IS_RUNNING_AS_LAMBDA,
				}
			)
	else:
		logger.info("Processing UploadEvent %r locally", upload_event_id)
		upload = UploadEvent.objects.get(id=upload_event_id)
		upload.process()
