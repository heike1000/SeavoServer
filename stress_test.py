from locust import task, TaskSet
from locust.contrib.fasthttp import FastHttpUser
import random
import string


def generate_serial_numbers(count):
    return [''.join(random.choices(string.hexdigits.lower(), k=16)) for _ in range(count)]

SERIAL_NUMBERS = generate_serial_numbers(10000)


class DeviceBehavior(TaskSet):
    def get_test_data(self, serial_number):
        return {
            "update_state": {
                "serial_number": serial_number,
                "waked": random.choice([0, 1]),
                "longitude": str(random.uniform(-180, 180)),
                "latitude": str(random.uniform(-90, 90)),
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

    # @task(5)
    # def register(self):
    #     self.serial_number = random.choice(SERIAL_NUMBERS)
    #     data = self.get_test_data(self.serial_number)["register"]
    #     self.client.post("/api/register", json=data)

    @task(10)
    def update_state(self):
        self.serial_number = random.choice(SERIAL_NUMBERS)
        data = self.get_test_data(self.serial_number)["update_state"]
        self.client.post("/api/update_state", json=data)

    @task(10)
    def update_app_list(self):
        self.serial_number = random.choice(SERIAL_NUMBERS)
        data = self.get_test_data(self.serial_number)["update_app_list"]
        self.client.post("/api/update_app_list", json=data)

    @task(10)
    def get_messages(self):
        self.serial_number = random.choice(SERIAL_NUMBERS)
        self.client.get("/api/messages", params={"serial_number": self.serial_number})

    @task(10)
    def reboot(self):
        self.serial_number = random.choice(SERIAL_NUMBERS)
        self.client.get("/api/reboot", params={"serial_number": self.serial_number})

    @task(10)
    def install(self):
        self.serial_number = random.choice(SERIAL_NUMBERS)
        self.client.get("/api/install", params={"serial_number": self.serial_number})

    @task(10)
    def uninstall(self):
        self.serial_number = random.choice(SERIAL_NUMBERS)
        self.client.get("/api/uninstall", params={"serial_number": self.serial_number})

    @task(10)
    def app_on_start(self):
        self.serial_number = random.choice(SERIAL_NUMBERS)
        self.client.get("/api/app_on_start", params={"serial_number": self.serial_number})


class DeviceUser(FastHttpUser):
    tasks = [DeviceBehavior]
    connection_timeout = 5.0
    network_timeout = 5.0
    max_retries = 1