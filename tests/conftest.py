import pytest
from django.core.management import call_command
from base64 import b64encode

@pytest.yield_fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
	with django_db_blocker:
		call_command("load_cards")


@pytest.yield_fixture(scope="session")
def random_deck(django_db_setup, django_db_blocker):
	with django_db_blocker:
		pass


@pytest.yield_fixture(scope="session")
def upload_context():
	yield None


@pytest.yield_fixture(scope="session")
def upload_event():
	yield {
		"headers": {
			"Authorization": "Token beh7141d-c437-4bfe-995e-1b3a975094b1"
		},
		"body" : b64encode('{"player1_rank": 5}'.encode("utf8")),
		"source_ip": "127.0.0.1"
	}


@pytest.yield_fixture(scope="session")
def s3_create_object_event():
	yield {
		"Records": [{
			"s3": {
				"bucket": {
					"name": "hsreplaynet-raw-log-uploads"
				},
				"object": {
					"key": "raw/2016/07/20/10/37/hUHupxzE9GfBGoEE8ECQiN/power.log"
				}
			}
		}]
	}