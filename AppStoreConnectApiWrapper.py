import time
from authlib.jose import jwt
import requests

class AppStoreConnectApiWrapper:
    """
    AppStoreConnectApiWrapper class provides methods to interact with the App Store Connect API.

    Attributes:
        EXPIRE_TIME: int - The expiration time of the JWT token.
        ENDPOINT_DEVICES: str - The API endpoint for retrieving device information.
        ENDPOINT_PROFILES: str - The API endpoint for retrieving profile information.

    Methods:
        __init__(self, keyId: str, issuerId: str, p8FilePath: str)
        get_device_list(self)
        get_profile_list(self, filter_name: str = None)
        get_profile_by_name(self, profile_name: str)
        get_profile(self, provisioning_profile_id: str)
        get_certificates_of_related_provisioning_profile(self, provisioning_profile_id: str)
        get_bundle_id_of_related_provisioning_profile(self, provisioning_profile_id: str)
        get_devices_of_related_provisioning_profile(self, provisioning_profile_id: str)
        register_device(self, deviceName: str, deviceUdid: str, devicePlatform: str) -> bool
        delete_profile(self, provisioning_profile_id: str)
        duplicate_provisioning_profile"""
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
        """
        Retrieves the device list from the endpoint.
        :return: the device list as a JSON object, or None if there's an error
        """
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

    def get_profile_list(self, filter_name: str = None):
        """
        :param filter_name: The name to filter the profiles by. Default is None.
        :return: The JSON response containing the profile list, or None if there was an error.

        This method is used to get a list of profiles. It sends a GET request to the profiles endpoint
        with an optional filter name parameter. If the filter name is provided, it adds the filter to the
        request parameters. It then checks the response status and returns the JSON response if successful,
        or None if there was an error. If there is an exception during the request, it prints the error and
        returns None.

        Example usage:
            get_profile_list() -> '{"profiles": [...]}'  # Return JSON response with the list of profiles
            get_profile_list("John") -> '{"profiles": [...]}'  # Return JSON response with filtered profiles
            get_profile_list("NonExisting") -> None  # Return None when no profiles match the filter
            get_profile_list("InvalidName") -> None  # Return None when there was an error during the request
        """
        try:
            self.__update_header()
            if filter_name is None:
                response = requests.get(self.ENDPOINT_PROFILES, headers=self.__header)
            else:
                response = requests.get(self.ENDPOINT_PROFILES, params={"filter[name]": filter_name}, headers=self.__header)

            if not response.ok:
                print(response.text)
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_profile_by_name(self, profile_name: str):
        """
        Retrieves a profile by its name.

        :param profile_name: The name of the profile to retrieve.
        :type profile_name: str
        :return: The profile object matching the specified name. None if the profile could not be found.
        :rtype: dict or None
        """
        profiles = self.get_profile_list()
        if profiles is None:
            print("Profile取得に失敗しました")
            return None

        for profile in profiles["data"]:
            if profile["attributes"]["name"] == profile_name:
                return profile
        return None

    def get_profile(self, provisioning_profile_id: str):
        """
        Retrieve a provisioning profile from App Store Connect API.

        :param provisioning_profile_id: ID of the provisioning profile to retrieve.
        :type provisioning_profile_id: str
        :return: JSON representation of the retrieved provisioning profile.
        :rtype: dict or None if the retrieval fails.
        """
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
        """
        Method to get the certificates associated with a provisioning profile.

        :param provisioning_profile_id: The ID of the provisioning profile.
        :return: A JSON object containing the certificates related to the provisioning profile.
        """
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
        """
        Retrieves the bundle identifier of the provisioning profile with the specified ID.

        :param provisioning_profile_id: The ID of the provisioning profile.
        :return: The bundle identifier of the provisioning profile, or None if an error occurs.
        """
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
        """
        Method: get_devices_of_related_provisioning_profile

        Fetches the list of devices associated with the specified provisioning profile.

        :param provisioning_profile_id: The ID of the provisioning profile for which to retrieve the associated devices.
        :type provisioning_profile_id: str
        :return: The list of devices associated with the provisioning profile. Returns None if an error occurs.
        :rtype: dict or None

        Example Usage:
            >> provisioning_profile_id = "12345678"
            >> devices = get_devices_of_related_provisioning_profile(provisioning_profile_id)
            >> print(devices)
            >> {'data': [{'id': 'device1', 'name': 'Device 1'}, {'id': 'device2', 'name': 'Device 2'}]}
        """
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
        """
        Register a device.

        :param deviceName: The name of the device.
        :param deviceUdid: The UDID (Unique Device Identifier) of the device.
        :param devicePlatform: The platform of the device (e.g. iOS, Android).
        :return: True if the device was registered successfully, False if an exception occurred or if the response was not OK.
        """
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
        """
        Delete a provisioning profile.

        :param provisioning_profile_id: The identifier of the provisioning profile to delete.
        :type provisioning_profile_id: str
        :return: True if the profile was successfully deleted, False otherwise.
        :rtype: bool

        This method sends a DELETE request to the App Store Connect API to delete the provisioning profile with the specified identifier. If the request is successful and the profile is deleted
        *, the method will return True. Otherwise, it will return False and print the error response.

        Example usage:
            >> delete_profile("abc123")
            >> True

        Note:
            - This method requires the 'provisioning_profile_id' parameter to be a valid string identifier of an existing provisioning profile.
            - This method relies on the 'requests' module to make the HTTP request.
        """
        response = requests.delete(f"https://api.appstoreconnect.apple.com/v1/profiles/{provisioning_profile_id}",
                                   headers=self.__header)
        if not response.status_code == 204:
            print(response.text)
            return False

        return True

    def duplicate_provisioning_profile(self, provisioning_profile_id: str, duplicate_name: str):
        """
        :param provisioning_profile_id: The ID of the provisioning profile to be duplicated.
        :param duplicate_name: The name of the duplicated provisioning profile.
        :return: The response JSON from the create profile request, or None if an error occurs.

        This method duplicates a provisioning profile by creating a new profile with the specified duplicate name and copying the attributes, bundle IDs, devices, and certificates from the source
        * profile.

        The method first retrieves the information of the source profile using the provisioning profile ID. If the source profile is not found, None is returned.

        Next, it retrieves the certificates, bundle IDs, and devices related to the source profile. If any of these related entities is not found, None is returned.

        Then, it constructs the request body for creating a duplicate profile based on the retrieved information. The duplicate profile will have the specified duplicate name and the same profile
        * type as the source profile. It will also have relationships with the same bundle IDs, devices, and certificates.

        The method sends a POST request to the endpoint for creating profiles with the request body. If the request is successful, the response JSON is returned. Otherwise, None is returned
        *.

        If an error occurs during the request or response handling, the error is printed and None is returned.
        """
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
        """
        :param provisioning_profile_name: The name of the provisioning profile to update all devices for.
        :return: The result of updating the provisioning profile with all devices. Returns None if there was an error.
        """
        try:
            self.__update_header()
            list = self.get_profile_list(provisioning_profile_name)
            if list is None:
                return None

            if len(list[ "data" ]) <= 0:
                return None

            target_profile = None
            for profile in list[ "data" ]:
                if profile[ "attributes" ][ "name" ] == provisioning_profile_name:
                    target_profile = profile

            if target_profile is None:
                print("provisioning profile not found")
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

            self.delete_profile(duplicate_result[ "data" ][ "id" ])

            return create_profile_res.json()
        except Exception as e:
            print(e)
            return None
