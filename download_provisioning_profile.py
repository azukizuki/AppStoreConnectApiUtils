import argparse
import base64
import csv
import os

from AppStoreConnectApiWrapper import AppStoreConnectApiWrapper

parser = argparse.ArgumentParser()
parser.add_argument("keyId", type=str, help="apple_auth_key_id")
parser.add_argument("issuerId", type=str, help="apple_auth_issuer_id")
parser.add_argument("p8filePath", type=str, help="apple p8filePath")
parser.add_argument("profileName",type=str,help="name of profile")
parser.add_argument("outputDir", type=str, help="directory to save")
args = parser.parse_args()

api = AppStoreConnectApiWrapper(args.keyId, args.issuerId, args.p8filePath)

profile = api.get_profile_by_name(args.profileName)
if profile is None:
    print("profile is None")
    exit(1)

content = profile["attributes"]["profileContent"]

file_path = args.outputDir+"/"+args.profileName+".mobileprovision"
with open(file_path, 'bw') as f:
    f.write(base64.b64decode(content))

