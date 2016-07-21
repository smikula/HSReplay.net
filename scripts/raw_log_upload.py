"""
This command line tool is intended to simulate HDT uploading a raw log to the web server.
"""
import argparse
import os
import requests
import json
from codecs import encode

parser = argparse.ArgumentParser(description='Upload a raw log file.')
parser.add_argument('-m','--metadata_path', help='path to the .json file with metadata to send')
parser.add_argument('-a', '--api_key', help='An hsreplay.net API Key')
parser.add_argument('-t', '--auth_token', help='An hsreplay.net AuthToken')
parser.add_argument('log_path', help="path to the power.log file to upload")

args = parser.parse_args()

HOST = "https://upload.hsreplay.net/api/v1/replay/upload/request"
api_key = args.api_key if args.api_key else os.environ.get("HSREPLAYNET_API_KEY", None)
auth_token = args.auth_token if args.auth_token else os.environ.get("HSREPLAYNET_AUTH_TOKEN", None)

HEADERS = {
	"X-Api-Key": api_key,
	"Authorization": "Token %s" % auth_token,
}

metadata = open(args.metadata_path).read() if args.metadata_path else {}
response_one = requests.post(HOST, metadata, headers=HEADERS).json()

log = open(args.log_path).read()
zipped_log = encode(log.encode("utf8"), "zlib")

response_two = requests.put(response_one["put_url"], data=zipped_log)

print("Replay ID: %s" % response_one["upload_shortid"])

descriptor = requests.get(response_one["descriptor_url"]).json()
print(json.dumps(descriptor, sort_keys=True, indent=4))
