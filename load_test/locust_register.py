import csv
from locust import HttpUser, task, between
import random
import string
import os

OUTPUT_FILE = "created_users.csv"

AVATAR_URLS = [
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Felix',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Aneka',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Milo',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Lia',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Christopher',
]
class RegisterUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["user_id", "email", "access_token"])

    @task
    def register(self):
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"user_{random_str}@exp.com"
        password = "password123"
        payload = {
            "email": email,
            "password": password,
            "username": f"User_{random_str}",
            "avatar_url": random.choice(AVATAR_URLS)
        }

        with self.client.post("/users/register", json=payload, catch_response=True) as response:
            if response.status_code == 201:
                try:
                    data = response.json()
                    user_data = data.get("user", {})
                    user_id = user_data.get("id") or user_data.get("_id")

                    access_token = response.cookies.get("access_token")

                    if user_id and access_token:
                        self.save_user(user_id, email, access_token)
                        response.success()
                    else:
                        response.failure("Missing user_id or access_token in response")
                except Exception as e:
                    response.failure(f"JSON decode failed: {e}")
            else:
                response.failure(f"Status {response.status_code}: {response.text}")

    def save_user(self, user_id, email, token):
        with open(OUTPUT_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([user_id, email, token])