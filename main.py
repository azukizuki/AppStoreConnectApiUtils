import argparse
import csv
import json
import random
import time

import requests
from authlib.jose import jwt

from AppStoreConnectApiWrapper import AppStoreConnectApiWrapper

target_device_list = []

def parse_tsv():
    with open(args.csvPath, "r") as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            target_device_list.append(row)


EXPIRE_TIME = int(round(time.time() + (19.0 * 60.0)))

parser = argparse.ArgumentParser()
parser.add_argument("keyId", type=str, help="apple_auth_key_id")
parser.add_argument("issuerId", type=str, help="apple_auth_issuer_id")
parser.add_argument("p8filePath", type=str, help="apple p8filePath")
parser.add_argument("-csvPath", type=str, help="firebaseAppDistribution csv path")
args = parser.parse_args()

api = AppStoreConnectApiWrapper(args.keyId, args.issuerId, args.p8filePath)

api.update_provisioning_profile_all_devices("SWEAT_DEV")
