from locust import task, TaskSet
from locust.contrib.fasthttp import FastHttpUser
import random
import string


def generate_serial_numbers(count):
    return [''.join(random.choices(string.hexdigits.lower(), k=16)) for _ in range(count)]


SERIAL_NUMBERS = generate_serial_numbers(100000)


class DeviceBehavior(TaskSet):
    def get_test_data(self, serial_number):
        return {
            "update_state": {
                "serial_number": serial_number,
                "waked": random.choice(["0", "1"]),
                "location": "福田区",
                "memory_usage": f"{random.randint(1, 4)}/4"
            },
            "update_app_list": {
                "serial_number": serial_number,
                "apps": ["com.example.app1", "com.example.app2"]
            },
            "register": {
                "serial_number": serial_number,
                "fw_version": f"1.{random.randint(0, 5)}.{random.randint(0, 20)}"
            }
        }

    def make_request(self, method, path, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Connection"] = "close"
        kwargs["headers"] = headers
        return getattr(self.client, method)(path, **kwargs)

    @task(10)
    def update_state(self):
        serial_number = random.choice(SERIAL_NUMBERS)
        data = self.get_test_data(serial_number)["update_state"]
        self.make_request("post", "/api/update_state", json=data)

    @task(10)
    def update_app_list(self):
        serial_number = random.choice(SERIAL_NUMBERS)
        data = self.get_test_data(serial_number)["update_app_list"]
        self.make_request("post", "/api/update_app_list", json=data)

    @task(10)
    def get_messages(self):
        serial_number = random.choice(SERIAL_NUMBERS)
        self.make_request("get", "/api/messages", params={"serial_number": serial_number})

    @task(10)
    def reboot(self):
        serial_number = random.choice(SERIAL_NUMBERS)
        self.make_request("get", "/api/reboot", params={"serial_number": serial_number})

    @task(10)
    def install(self):
        serial_number = random.choice(SERIAL_NUMBERS)
        self.make_request("get", "/api/install", params={"serial_number": serial_number})

    @task(10)
    def uninstall(self):
        serial_number = random.choice(SERIAL_NUMBERS)
        self.make_request("get", "/api/uninstall", params={"serial_number": serial_number})

    @task(10)
    def app_on_start(self):
        serial_number = random.choice(SERIAL_NUMBERS)
        self.make_request("get", "/api/app_on_start", params={"serial_number": serial_number})


class DeviceUser(FastHttpUser):
    tasks = [DeviceBehavior]
    connection_timeout = 5.0
    network_timeout = 5.0
    max_retries = 1
