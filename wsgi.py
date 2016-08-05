"""
WSGI config for HSReplay.net

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hsreplaynet.settings")
import sys; sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from django.conf import settings
from django.core.wsgi import get_wsgi_application


application = get_wsgi_application()


# Run webpack in the background if we are in DEBUG mode
if settings.DEBUG:
	import subprocess

	webpack_bin = os.path.join(settings.BASE_DIR, "node_modules/.bin/webpack")

	# Windows can't execute "webpack"; it has to execute "webpack.cmd"
	if os.name == "nt":
		webpack_bin = webpack_bin + ".cmd"

	webpack_config = os.path.join(settings.BASE_DIR, "webpack.config.js")
	subprocess.Popen([
		webpack_bin,
		"-d", "--devtool", "cheap-module-eval-source-map",
		"--verbose", "--progress", "--colors",
		"--config", webpack_config,
		"--watch",
	])

	sassc = os.path.join(settings.BASE_DIR)
	subprocess.Popen([
		"sassc", settings.SCSS_INPUT_FILE, settings.SCSS_OUTPUT_FILE,
		"--sourcemap", "--source-comments",
		"--watch",
	])
