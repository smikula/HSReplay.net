import json
import os
import time
import re
from contextlib import contextmanager
from functools import wraps
from django.conf import settings
from django.utils.timezone import now
from . import logger


if "raven.contrib.django.raven_compat" in settings.INSTALLED_APPS:
	from raven.contrib.django.raven_compat.models import client as sentry
else:
	sentry = None


def error_handler(e):
	if sentry is not None:
		sentry.captureException()
	else:
		logger.exception(e)


def get_token_from_key(key):
	RAW_KEY_PATTERN = r"raw/(?P<timestamp>\d{4}/\d{2}/\d{2}/\d{2}/\d{2})/(?P<token>)[a-z0-9-]{36}/(?P<shortid>\w{22})/power.log"
	match = re.match(RAW_KEY_PATTERN, key)
	return match.groupdict()["token"]


def get_tracing_id(event):
	"""
	Returns the Authorization token as a unique identifier.
	Used in the Lambda logging system to trace sessions.
	"""
	UNKNOWN_ID = "unknown-id"
	if "Records" in event and "Sns" in event["Records"][0]:
		# We are in a lambda triggered via SNS
		message = json.loads(event["Records"][0]["Sns"]["Message"])

		if "raw_key" in message:
			# We are in a lambda to process a raw s3 upload
			return get_token_from_key(message["raw_key"])

		elif "token" in message:
			# We are in a lambda for processing an upload event
			return message["token"]
		else:
			return UNKNOWN_ID

	if "Records" in event and "s3" in event["Records"][0]:
		# We are in the process_s3_object Lambda
		s3_record = event['Records'][0]['s3']
		return get_token_from_key(s3_record['object']['key'])

	auth_header = None

	if "authorizationToken" in event:
		# We are in the Authorization Lambda
		auth_header = event["authorizationToken"]

	elif "headers" in event:
		# We are in the create upload event Lambda
		auth_header = event["headers"]["Authorization"]

	if auth_header:
		# The auth header is in the format 'Token <id>'
		return auth_header.split()[1]

	return UNKNOWN_ID


def lambda_handler(func):
	"""Indicates the decorated function is a AWS Lambda handler.

	The following standard lifecycle services are provided:
		- Sentry reporting for all Exceptions that propagate
		- Capturing a standard set of metrics for Influx
		- Making sure all connections to the DB are closed
	"""
	@wraps(func)
	def wrapper(event, context):
		tracing_id = get_tracing_id(event)
		os.environ["TRACING_REQUEST_ID"] = tracing_id
		if sentry:
			# Provide additional metadata to sentry in case the exception
			# gets trapped and reported within the function.
			sentry.user_context({
				"aws_log_group_name": getattr(context, "log_group_name"),
				"aws_log_stream_name": getattr(context, "log_stream_name"),
				"aws_function_name": getattr(context, "function_name"),
				"tracing_id": tracing_id
			})

		try:
			measurement = "%s_duration_ms" % func.__name__
			handler_start = now()
			with influx_timer(
				measurement, timestamp=handler_start,
				is_running_as_lambda=settings.IS_RUNNING_AS_LAMBDA):

				return func(event, context)

		except Exception as e:
			logger.exception("Got an exception: %r", e)
			if sentry:
				logger.info("Inside sentry capture block.")
				sentry.captureException()
			else:
				logger.info("Sentry is not available.")
			raise
		finally:
			from django.db import connection
			connection.close()

	return wrapper


try:
	if settings.IS_RUNNING_LIVE or settings.IS_RUNNING_AS_LAMBDA:
		from influxdb import InfluxDBClient

		influx_settings = settings.INFLUX_DATABASES["hsreplaynet"]
		influx = InfluxDBClient(
			host=influx_settings["HOST"],
			port=influx_settings.get("PORT", 8086),
			username=influx_settings["USER"],
			password=influx_settings["PASSWORD"],
			database=influx_settings["NAME"],
			ssl=influx_settings.get("SSL", False),
		)
	else:
		influx = None
except ImportError as e:
	logger.info("Influx is not installed, so will be disabled (%s)", e)
	influx = None


def influx_write_payload(payload):
	try:
		influx.write_points(payload)
	except Exception as e:
		# Can happen if Influx if not available for example
		error_handler(e)


def influx_metric(measure, fields, timestamp=None, **kwargs):
	if influx is None:
		return
	if timestamp is None:
		timestamp = now()
	if settings.IS_RUNNING_LIVE or settings.IS_RUNNING_AS_LAMBDA:
		payload = {
			"measurement": measure,
			"tags": kwargs,
			"fields": fields,
		}

		payload["time"] = timestamp.isoformat()
		influx_write_payload([payload])


@contextmanager
def influx_timer(measure, timestamp=None, **kwargs):
	"""
	Reports the duration of the context manager.
	Additional kwargs are passed to InfluxDB as tags.
	"""
	start_time = time.clock()
	exception_raised = False
	if timestamp is None:
		timestamp = now()
	try:
		yield
	except Exception:
		exception_raised = True
		raise
	finally:
		stop_time = time.clock()
		duration = (stop_time - start_time) * 10000

		tags = kwargs
		tags["exception_thrown"] = exception_raised
		payload = {
			"measurement": measure,
			"tags": tags,
			"fields": {
				"value": duration,
			}
		}

		payload["time"] = timestamp.isoformat()
		if influx:
			influx_write_payload([payload])
