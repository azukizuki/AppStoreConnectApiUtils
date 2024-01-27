import argparse
from AppStoreConnectApiWrapper import AppStoreConnectApiWrapper

parser = argparse.ArgumentParser()
parser.add_argument("keyId", type=str, help="apple_auth_key_id")
parser.add_argument("issuerId", type=str, help="apple_auth_issuer_id")
parser.add_argument("p8filePath", type=str, help="apple p8filePath")
parser.add_argument("profileName",type=str,help="name of target provisioning profile")
args = parser.parse_args()

api = AppStoreConnectApiWrapper(args.keyId, args.issuerId, args.p8filePath)
api.update_provisioning_profile_all_devices(args.profileName)
