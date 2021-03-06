DEBUG = True
ALLOWED_HOSTS = ("*", )

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_URL = "/media/"
STATIC_URL = "/static/"
JOUST_STATIC_URL = "//static.hsreplay.net/static/joust/"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INTERNAL_IPS = (
	"0.0.0.0",
	"127.0.0.1",
)

RAVEN_CONFIG = {
	"dsn": "https://******@app.getsentry.com/80388",
	# If you are using git, you can also automatically configure the
	# release based on the git info.
	# "release": raven.fetch_git_sha(os.path.join(os.path.dirname(__file__), "..")),
}
# JOUST_RAVEN_DSN_PUBLIC = "https://hash@app.getsentry.com/12345"
# JOUST_RAVEN_ENVIRONMENT = "development"

INFLUX_DATABASES = {
	"hsreplaynet": {
		"NAME": "hsreplaynet",
		"ADDRESS": "localhost",
		"PORT": 8086,
		"USER": "",
		"PASSWORD": "",
		"SSL": False,
	}
}


# AWS SNS Settings
SNS_PROCESS_UPLOAD_EVENT_TOPIC = ""
