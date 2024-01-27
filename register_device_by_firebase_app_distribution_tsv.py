import argparse
import csv

from AppStoreConnectApiWrapper import AppStoreConnectApiWrapper

parser = argparse.ArgumentParser()
parser.add_argument("keyId", type=str, help="apple_auth_key_id")
parser.add_argument("issuerId", type=str, help="apple_auth_issuer_id")
parser.add_argument("p8filePath", type=str, help="apple p8filePath")
parser.add_argument("firebaseTsvPath",type=str,help="filePath of firebase app distribution udid tsv file")
args = parser.parse_args()

api = AppStoreConnectApiWrapper(args.keyId, args.issuerId, args.p8filePath)

registered_devices = api.get_device_list()
if registered_devices is None:
    print("デバイスリストの取得に失敗")
    exit(1)

print(registered_devices)

with open(args.firebaseTsvPath) as f:
    reader = csv.DictReader(f, delimiter="\t")
    for item in reader:
        already_registered = False
        for device in registered_devices["data"]:
            if device["attributes"]["udid"].lower() == item["Device ID"].lower():
                already_registered = True
                break
        if not already_registered:
            print(f"{item}を登録するよ")
            api.register_device(item["Device Name"], item["Device ID"])
