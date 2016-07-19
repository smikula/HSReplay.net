import pytest
from django.core.management import call_command


@pytest.yield_fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
	with django_db_blocker:
		call_command("load_cards")


@pytest.yield_fixture(scope="session")
def random_deck(django_db_setup, django_db_blocker):
	with django_db_blocker:
		pass

@pytest.yield_fixture(scope="session")
def upload_event():
	yield {}


@pytest.yield_fixture(scope="session")
def upload_context():
	yield None
