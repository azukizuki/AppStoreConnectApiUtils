import time
from authlib.jose import jwt
import requests


class AppStoreConnectApiWrapper:
    EXPIRE_TIME = int(round(time.time() + (20.0 * 60.0)))
    ENDPOINT_DEVICES = "https://api.appstoreconnect.apple.com/v1/devices"
    ENDPOINT_PROFILES = "https://api.appstoreconnect.apple.com/v1/profiles"

    def __init__(self, keyId: str, issuerId: str, p8FilePath: str):
        self.__header = {}
        self.__payload = {}
        self.__private_key = None
        self.__keyId = keyId
        self.__issuerId = issuerId
        self.__p8FilePath = p8FilePath

    def __update_header(self):
        self.__header = {
            "alg": "ES256",
            "kid": self.__keyId,
            "type": "JWT"
        }

        self.__payload = {
            "iss": self.__issuerId,
            "exp": self.EXPIRE_TIME,
            "aud": "appstoreconnect-v1"
        }
        with open(self.__p8FilePath, "r") as file:
            private_key = file.read()

        token = jwt.encode(self.__header, self.__payload, private_key)
        auth_jwt = "Bearer " + token.decode()
        self.__header = {"Authorization": auth_jwt}

    def get_device_list(self):
        try:
            self.__update_header()
            response = requests.get(self.ENDPOINT_DEVICES, headers=self.__header)
            if not response.ok:
                print(response.text)
                return None
            return response.json()
        except requests.exceptions as e:
            print(e)
            return None

    def get_profile_liat(self, filter_name: str = "*"):
        try:
            self.__update_header()
            response = requests.get(self.ENDPOINT_PROFILES, params={"filter[name]": filter_name}, headers=self.__header)
            if not response.ok:
                print(response.text)
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_profile(self, provisioning_profile_id: str):
        try:
            self.__update_header()
            response = requests.get(f"https://api.appstoreconnect.apple.com/v1/profiles/{provisioning_profile_id}",
                                    headers=self.__header)
            if not response.ok:
                print(response.text)
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_certificates_of_related_provisioning_profile(self, provisioning_profile_id: str):
        try:
            self.__update_header()
            response = requests.get(
                f'https://api.appstoreconnect.apple.com/v1/profiles/{provisioning_profile_id}/certificates',
                headers=self.__header)
            if not response.ok:
                print(response.text)
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_bundle_id_of_related_provisioning_profile(self, provisioning_profile_id: str):
        try:
            self.__update_header()
            response = requests.get(
                f"https://api.appstoreconnect.apple.com/v1/profiles/{provisioning_profile_id}/bundleId",
                headers=self.__header)
            if not response.ok:
                print(response.text)
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_devices_of_related_provisioning_profile(self, provisioning_profile_id: str):
        try:
            self.__update_header()
            response = requests.get(
                f"https://api.appstoreconnect.apple.com/v1/profiles/{provisioning_profile_id}/devices",
                headers=self.__header)
            if not response.ok:
                print(response.text)
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def register_device(self, deviceName: str, deviceUdid: str, devicePlatform: str) -> bool:
        try:
            self.__update_header()
            payload = {
                "data": {
                    "type": "devices",
                    "attributes": {
                        "name": deviceName,
                        "platform": devicePlatform,
                        "udid": deviceUdid
                    }
                }
            }
            response = requests.post(self.ENDPOINT_DEVICES, headers=self.__header, json=payload)
            if not response.ok:
                print(response.text)
                return None
            return response.json()

        except requests.exceptions.RequestException as e:
            print(e)
            return False

    def delete_profile(self, provisioning_profile_id: str):
        response = requests.delete(f"https://api.appstoreconnect.apple.com/v1/profiles/{provisioning_profile_id}",
                                   headers=self.__header)
        if not response.status_code == 204:
            print(response.text)
            return False

        return True

    def duplicate_provisioning_profile(self, provisioning_profile_id: str, duplicate_name: str):

        src_profile_info = self.get_profile(provisioning_profile_id)
        if src_profile_info is None:
            return None

        related_certificates = self.get_certificates_of_related_provisioning_profile(provisioning_profile_id)
        related_bundle_ids = self.get_bundle_id_of_related_provisioning_profile(provisioning_profile_id)
        related_devices = self.get_devices_of_related_provisioning_profile(provisioning_profile_id)

        if related_certificates is None or related_bundle_ids is None or related_devices is None:
            return None

        backup_request_body = {
            "data": {
                "type": "profiles",
                "attributes": {
                    "name": duplicate_name,
                    "profileType": src_profile_info[ "data" ][ "attributes" ][ "profileType" ]
                },
                "relationships": {
                    "bundleId": {
                        "data": {
                            "type": "bundleIds",
                            "id": related_bundle_ids[ "data" ][ "id" ]
                        }
                    },
                    "devices": {
                        "data": [
                            {"type": "devices", "id": device_id[ "id" ]} for device_id in related_devices[ "data" ]
                        ]
                    },
                    "certificates": {
                        "data": [
                            {"type": "certificates", "id": certificate_id[ "id" ]} for certificate_id in
                            related_certificates[ "data" ]
                        ]
                    }
                }
            }
        }
        try:
            create_profile_res = requests.post(self.ENDPOINT_PROFILES, headers=self.__header, json=backup_request_body)
            if not create_profile_res.ok:
                print(create_profile_res.text)
                return None
            return create_profile_res.json()

        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def update_provisioning_profile_all_devices(self, provisioning_profile_name: str):
        try:
            self.__update_header()
            list = self.get_profile_liat(provisioning_profile_name)
            if list is None:
                return None

            if len(list[ "data" ]) <= 0:
                return None

            target_profile = None
            for profile in list["data"]:
                if profile["attributes"]["name"] == provisioning_profile_name:
                    target_profile = profile

            if target_profile is None:
                print("名前に合致するProvisioningProfileが存在しません")
                return None

            target_profile_id = target_profile[ "id" ]

            duplicate_result = self.duplicate_provisioning_profile(target_profile[ "id" ],
                                                                   "backup_" + target_profile[ "attributes" ][ "name" ])
            if duplicate_result is None:
                return None

            # get related info
            related_certificates = self.get_certificates_of_related_provisioning_profile(target_profile_id)
            related_bundle_ids = self.get_bundle_id_of_related_provisioning_profile(target_profile_id)
            all_devices = self.get_device_list()
            if related_certificates is None or related_bundle_ids is None or all_devices is None:
                return None

            # delete original
            delete_res = self.delete_profile(target_profile[ "id" ])
            print(delete_res)
            if not delete_res:
                return None

            body = {
                "data": {
                    "type": "profiles",
                    "attributes": {
                        "name": target_profile[ "attributes" ][ "name" ],
                        "profileType": target_profile[ "attributes" ][ "profileType" ]
                    },
                    "relationships": {
                        "bundleId": {
                            "data": {
                                "type": "bundleIds",
                                "id": related_bundle_ids[ "data" ][ "id" ]
                            }
                        },
                        "devices": {
                            "data": [
                                {"type": "devices", "id": device_id[ "id" ]} for device_id in all_devices[ "data" ]
                            ]
                        },
                        "certificates": {
                            "data": [
                                {"type": "certificates", "id": certificate_id[ "id" ]} for certificate_id in
                                related_certificates[ "data" ]
                            ]
                        }
                    }
                }
            }
            create_profile_res = requests.post(self.ENDPOINT_PROFILES, headers=self.__header, json=body)

            if not create_profile_res.ok:
                print(create_profile_res.text)
                return None

            self.delete_profile(duplicate_result["data"]["id"])

            return create_profile_res.json()
        except Exception as e:
            print(e)
            return None
