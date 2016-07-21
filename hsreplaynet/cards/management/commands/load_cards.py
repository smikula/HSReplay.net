from django.core.management.base import BaseCommand
from hearthstone import cardxml
from ...models import Card


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument("path", nargs="?", help="CardDefs.xml file")

	def handle(self, *args, **options):
		path = options["path"]
		db, _ = cardxml.load(path)
		self.stdout.write("%i cards available" % (len(db)))

		qs = Card.objects.all().values_list("id")
		known_ids = [item[0] for item in qs]
		missing = [id for id in db if id not in known_ids]
		self.stdout.write("%i known cards" % (len(known_ids)))

		new_cards = [Card.from_cardxml(db[id]) for id in missing]
		Card.objects.bulk_create(new_cards)
		self.stdout.write("%i new cards" % (len(new_cards)))
