from fabric.api import run, sudo
from fabric.contrib.files import exists
from fabric.context_managers import path


REPO_URL = "https://github.com/HearthSim/HSReplay.net"
NO_PIP_CACHE = True


def deploy():
	site_folder = "/srv/http/hsreplay.net"
	source_folder = site_folder + "/source"
	venv = site_folder + "/virtualenv"
	nodeenv = site_folder + "/nodeenv"

	sudo("mkdir -p %s" % (source_folder), user="www-data")

	_get_latest_source(source_folder)
	_update_virtualenv(venv, source_folder + "/requirements/live.txt")
	_update_nodeenv(venv, nodeenv, source_folder)
	_update_bundles(venv, nodeenv, source_folder)
	_compile_error_pages(venv, source_folder)
	_update_static_files(venv, source_folder)
	_update_database(venv, source_folder)

	_restart_web_server()


def _get_latest_source(path):
	if exists(path + "/.git"):
		sudo("git -C %s fetch" % (path), user="www-data")
	else:
		sudo("git clone %s %s" % (REPO_URL, path), user="www-data")
	current_commit = run("git -C %s rev-parse origin/master" % (path))
	sudo("git -C %s reset --hard %s" % (path, current_commit), user="www-data")


def _update_virtualenv(venv, requirements):
	if not exists(venv + "/bin/pip"):
		sudo("python3 -m venv %s" % (venv), user="www-data")

	command = "%s/bin/pip install -r %s" % (venv, requirements)
	if NO_PIP_CACHE:
		command += " --no-cache-dir"
	sudo(command, user="www-data")


def _update_nodeenv(venv, nodeenv, source_path):
	if not exists(nodeenv + "/bin/npm"):
		sudo("%s/bin/nodeenv %s" % (venv, nodeenv), user="www-data")

	with path(nodeenv + "/bin", "prepend"):
		sudo("npm -C %s install --no-progress --production" % (source_path), user="www-data")


def _update_bundles(venv, nodeenv, source_path):
	with path("%s/bin:%s/bin" % (nodeenv, venv), "prepend"):
		sudo("npm -C %s run build" % (source_path), user="www-data")


def _compile_error_pages(venv, path, strip_whitespace=True):
	command = "%s/bin/python %s/manage.py compile_error_pages" % (venv, path)
	if strip_whitespace:
		command += " --strip-whitespace"
	sudo(command, user="www-data")


def _update_static_files(venv, path):
	if not exists(path + "/hsreplaynet/static/vendor"):
		sudo(path + "/scripts/get_vendor_static.sh", user="www-data")
	# XXX: Hardcoding the scss paths is nasty. This should be part of collectstatic.
	scss_input = path + "/hsreplaynet/static/styles/main.scss"
	scss_output = scss_input.replace(".scss", ".css")
	sudo("%s/bin/sassc %s %s" % (venv, scss_input, scss_output), user="www-data")
	sudo("%s/bin/python %s/manage.py collectstatic --noinput" % (venv, path), user="www-data")


def _update_database(venv, path):
	sudo("%s/bin/python %s/manage.py migrate --noinput" % (venv, path), user="www-data")


def _restart_web_server():
	sudo("supervisorctl restart hsreplay.net")
