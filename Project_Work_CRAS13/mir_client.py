import requests
import json

from requests.auth import HTTPBasicAuth


# from requests.exceptions import RequestException


class APIClient:
    """
        :param base_url: REST server url
        :param username: REST API username
        :param password_digest: hexdigest of sha256 hashed REST API password
    """

    def __init__(self, base_url, username, password_digest):
        self.base_url = base_url
        self.auth = HTTPBasicAuth(username, password_digest)
        self.headers = {"Content-Type": "application/json",
                        "Accept-Language": "en_US"}

    def request(self, method, endpoint, body=None):
        url = self.base_url + endpoint
        response = requests.request(method, url, auth=self.auth,
                                    headers=self.headers, json=body)
        return response.json()

    def post_mission_queue(self, mission_id):
        body = {"mission_id": mission_id}
        return self.request("post", "/mission_queue", body=body)

    def get_mission_queue(self):
        return self.request("get", "/mission_queue")

    def get_missions(self):
        return self.request("get", "/missions")

    def get_mission_queue_id(self, mission_queue_id):
        return self.request("get", "/mission_queue/{}".format(mission_queue_id))

    def get_actions(self, mission_id):
        return self.request("get", "/missions/{}/actions".format(mission_id))

    def delete_mission_queue_id(self, mission_queue_id):
        return self.request("DELETE", "/mission_queue/{}".format(mission_queue_id))  # post

    def get_status(self):
        return self.request("get", "/status")

    def put_status(self, state_id):
        body = {"state_id": state_id}
        return self.request("put", "/status", body=body)

    def get_registers(self, register_id):
        return self.request("get", "/registers/{}".format(register_id))

    def put_registers(self, register_id, value):
        body = {"id": register_id, "value": value, "label": "string"}
        return self.request("put", "/registers/{}".format(register_id), body=body)

    def abort_all_missions(self):  # emergency stop
        return self.request("DELETE", "/mission_queue")
