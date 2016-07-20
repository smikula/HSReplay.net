import json
from isolated import uploaders
from unittest.mock import MagicMock


def test_upload(upload_event, upload_context, monkeypatch):
	# Mock out S3
	mock_s3 = MagicMock()
	mock_s3.put_object = MagicMock()
	mock_s3.generate_presigned_url = MagicMock(return_value="[A SIGNED URL]")
	monkeypatch.setattr(uploaders, "S3", mock_s3)

	# Invoke code under test
	result = uploaders.generate_log_upload_address_handler(upload_event, upload_context)

	descriptor_object_bytes = mock_s3.put_object.call_args[1]["Body"]
	descriptor = json.loads(descriptor_object_bytes.decode("utf8"))

	assert "descriptor_url" in result
	assert result["descriptor_url"] == "[A SIGNED URL]"
	assert "put_url" in result
	assert result["put_url"] == "[A SIGNED URL]"

	assert "upload_shortid" in result
	# Ensure the shortID returned is also saved to use on the upload event
	assert descriptor["shortid"] == result["upload_shortid"]
