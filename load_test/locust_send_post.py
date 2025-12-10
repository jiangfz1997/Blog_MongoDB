import csv
import random
import string
from locust import HttpUser, task, between

USER_CREDENTIALS = []
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
except FileNotFoundError:
    exit(1)


class BlogCreator(HttpUser):
    wait_time = between(0.5, 2.0)

    @task
    def create_blog_post(self):
        if not USER_CREDENTIALS:
            return

        user = random.choice(USER_CREDENTIALS)
        access_token = user["access_token"]

        random_suffix = ''.join(random.choices(string.digits, k=6))

        payload = {
            "title": f"Database 101: start your database journey{random_suffix}",
            "content": f"This is the content of the blog post number {random_suffix}. " * random.randint(5, 10),
            "tags": self.generate_random_tags()
        }


        cookies = {
            "access_token": access_token
        }

        with self.client.post("/blogs", json=payload, cookies=cookies, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
                # try:
                #     data = response.json()
                #     blog_id = data.get("id")
                #     author_id = data.get("author_id")
                #     if blog_id and random.random() < 0.2:
                #         self.save_blog(blog_id, author_id)
                #     else:
                #         response.failure("Missing blog_id in response")
                # except Exception as e:
                #     response.failure(f"JSON decode failed: {e}")
            elif response.status_code == 401:
                response.failure(f"Auth Failed for user {user['user_id']}")
            else:
                response.failure(f"Post failed: {response.status_code} - {response.text}")


    def save_blog(self, blog_id, author_id):
        with open(OUTPUT_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([blog_id, author_id])

    def generate_random_tags(self):
        main_tag = random.sample(tags_list, random.randint(1, 3))
        extra_tag = random.sample(expanded_tag_list, random.randint(1,3))
        return main_tag + extra_tag