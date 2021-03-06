import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.serializers import ValidationError
from hsreplaynet.api.serializers import SmartFileField


def test_smart_file_field():
	field = SmartFileField()
	with pytest.raises(ValidationError):
		field.run_validation("does_not_exist_12e89fhcu923rks.txt")

	value = default_storage.save("test_file.txt", ContentFile("test data"))
	field.run_validation(value)
	default_storage.delete(value)


@pytest.mark.django_db
def test_auth_token_request(client):
	data = {
		"full_name": "Test Client",
		"email": "test@example.org",
		"website": "https://example.org",
	}
	response = client.post("/api/v1/agents/", data)

	assert response.status_code == 201
	out = response.json()

	api_key = out["api_key"]
	assert api_key
	assert out["full_name"] == data["full_name"]
	assert out["email"] == data["email"]
	assert out["website"] == data["website"]

	url = "/api/v1/tokens/"
	response = client.post(url, content_type="application/json", HTTP_X_API_KEY=api_key)
	assert response.status_code == 201
	out = response.json()

	token = out["key"]
	assert token
	assert out["user"] is None

	# GET (listing tokens) should error
	response = client.get(url)
	assert response.status_code == 403

	# POST without API key should error
	response = client.post(url)
	assert response.status_code == 403
