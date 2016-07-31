#!/usr/bin/env python

import json
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument("setting", type=str, nargs="*")

	def handle(self, *args, **options):
		keys = options["setting"]
		ret = {}
		for key in keys:
			if hasattr(settings, key):
				ret[key] = getattr(settings, key)

		self.stdout.write(json.dumps(ret))
