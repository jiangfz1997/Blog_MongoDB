from locust import HttpUser, task, between
import random
import uuid
import string


def random_user():
    name = ''.join(random.choices(string.ascii_lowercase, k=6))
    domain = random.choice(["gmail.com", "outlook.com", "example.com"])
    return {
        "username": f"user_{name}",
        "email": f"{name}@{domain}",
        "password": uuid.uuid4().hex[:10]
    }


class BlogUser(HttpUser):
    wait_time = between(1, 5)
    # Testcase for user registration
    @task
    def register_user(self):
        self.client.post("/users/", json=random_user())

