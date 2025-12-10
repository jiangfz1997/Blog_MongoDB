import random
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
    def get_trending_post(self):
        params = {
            "page": 1,
            "limit": 5,
        }
        with self.client.get("/search/discover", params=params, name="/discover", catch_response=True) as response:
            if response.status_code in (200, 201):
                response.success()
            else:
                response.failure(f"Get trending failed: {response.status_code} - {response.text}")

