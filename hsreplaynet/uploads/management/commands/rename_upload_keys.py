import json
from argparse import ArgumentTypeError
from django.core.management.base import BaseCommand
from ...models import UploadEvent


def update_upload(upload):
	d = json.loads(upload.metadata)
	if "match_start_timestamp" in d:
		d["match_start"] = d.pop("match_start_timestamp")
	if "client_id" in d:
		d["client_handle"] = d.pop("client_id")
	if "game_id" in d:
		d["game_handle"] = d.pop("game_id")
	if "hearthstone_build" in d:
		d["build"] = d.pop("hearthstone_build")
	if "spectate_key" in d:
		d["spectator_password"] = d.pop("spectate_key")
	upload.metadata = json.dumps(d)
	upload.save()


def key_pair(arg):
	old, _, new = arg.partition("=")
	if not old or not new:
		raise ArgumentTypeError("Argument must be formatted as old=new")
	return (old, new)


class Command(BaseCommand):
	help = "Rename a key on all UploadEvents"

	def add_arguments(self, parser):
		parser.add_argument("key_pair", nargs="+", type=key_pair)

	def handle(self, *args, **options):
		pairs = options["key_pair"]
		queryset = UploadEvent.objects.all()
		if len(pairs) == 1:
			queryset = queryset.filter(metadata__contains=pairs[0][0])

		total_updated = 0
		for upload in queryset:
			d = json.loads(upload.metadata)
			updated = False
			for old, new in pairs:
				if old in d:
					d[new] = d.pop(old)
					updated = True

			if updated:
				self.stdout.write("Updating %r" % (upload))
				upload.metadata = json.dumps(d)
				upload.save()
				total_updated += 1

		self.stdout.write("Updated %i UploadEvents" % (total_updated))
