import csv
import random
import string
from locust import HttpUser, task, between

USER_CREDENTIALS = []
TARGET_BLOGS = []
tags_list = ["tech", "mongodb", "locust", "python", "Database", "performance"]
expanded_tag_list = [
    "joy", "sadness", "reflection", "anxiety", "calm", "hope", "nostalgia",
    "photography", "gardening", "DIY", "fitness", "cooking", "reading",
    "writing", "gaming", "crafts", "hiking", "cycling",
    "movies", "tvshows", "books", "podcast", "anime", "comics", "review",
    "local", "global", "citylife", "mountains", "beach", "adventure",
    "roadtrip", "explore", "culture",
    "minimalism", "productivity", "health", "wellness", "relationships",
    "finance", "career", "personal", "inspiration", "challenge",
    "dessert", "coffee", "cocktails", "vegan", "recipe", "baking",
    "life", "fun", "happy", "science", "history", "nature", "sports",
    "education", "code"
]
OUTPUT_FILE = "created_blogs.csv"


try:
    with open("./load_test/created_users.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("access_token"):
                USER_CREDENTIALS.append(row)
    with open("./load_test/created_blogs.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("blog_id"):
                TARGET_BLOGS.append(row)
except FileNotFoundError:
    print("Error! Can not find created_users.csv or created_blogs.csv, please run the registration and blog creation scripts first!")
    exit(1)


class BlogViewer(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self):
        if USER_CREDENTIALS:
            self.user_data = random.choice(USER_CREDENTIALS)
            self.cookies = {"access_token": self.user_data["access_token"]}
        else:
            self.user_data = None
            self.cookies = {}
    @task
    def view_blog_post(self):
        blog_id = random.choice(TARGET_BLOGS)["blog_id"]

        with self.client.get(f"/blogs/{blog_id}", name="/blogs", cookies=self.cookies, catch_response=True) as response:
            if response.status_code in (200, 201):
                response.success()

            elif response.status_code == 401:
                response.failure(f"Auth Failed")
            else:
                response.failure(f"Post failed: {response.status_code} - {response.text}")

    @task(5)
    def like_blog_post(self):
        if not USER_CREDENTIALS:
            return

        blog_id = random.choice(TARGET_BLOGS)["blog_id"]
        with self.client.post(f"/blogs/{blog_id}/like", name="/blogs/like", cookies=self.cookies, catch_response=True) as response:
            if response.status_code in (200, 201):
                response.success()

            elif response.status_code == 401:
                response.failure(f"Auth Failed")
            else:
                response.failure(f"Like failed: {response.status_code} - {response.text}")

    @task(2)
    def comment_blog_post(self):
        if not USER_CREDENTIALS:
            return

        blog_id = random.choice(TARGET_BLOGS)["blog_id"]
        comment_content = "This is a load test comment " + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

        payload = {
            "blog_id": blog_id,
            "parent_id": None,
            "content": comment_content
        }

        with self.client.post(f"/comments", name="/comments", json=payload, cookies=self.cookies, catch_response=True) as response:
            if response.status_code in (200, 201):
                response.success()

            elif response.status_code == 401:
                response.failure(f"Auth Failed")
            else:
                response.failure(f"Comment failed: {response.status_code} - {response.text}")

    @task(10)
    def get_trending_post(self):
        params = {
            "limit": 10,
        }
        with self.client.get("/blogs/views/hottest", params=params, name="/blogs/views/hottest", catch_response=True) as response:
            if response.status_code in (200, 201):
                response.success()
            else:
                response.failure(f"Get trending failed: {response.status_code} - {response.text}")

