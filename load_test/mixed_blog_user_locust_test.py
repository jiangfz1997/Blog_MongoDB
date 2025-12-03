import json
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from threading import Lock

from locust import HttpUser, task, between, events
from locust.clients import ResponseContextManager
from locust.exception import StopUser

# Load interpreter to create users and prefill posts
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    print(f"[INIT] Inject PROJECT_ROOT into sys.path: {PROJECT_ROOT}")

from prefill_posts import random_title, random_tags, random_paragraph, prefill_posts
from create_test_users import create_test_users


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    # Configs
    USER_COUNT = 1500
    BLOG_COUNT = 4000
    MAX_COMMENTS = 40
    MONGO_URI = "mongodb://localhost:27017"

    print("\n=== [PREP] START POPULATING TEST DATA ===")
    print(f"[PREP] USERS={USER_COUNT}, BLOGS={BLOG_COUNT}, COMMENTS<= {MAX_COMMENTS}")
    print(f"[PREP] MongoDB={MONGO_URI}\n")

    create_test_users(
        USER_COUNT,
        MONGO_URI,
    )

    prefill_posts(
        BLOG_COUNT,
        MAX_COMMENTS,
        MONGO_URI,
    )

    print("\n=== [PREP DONE] MongoDB test data ready ===\n")


# Write logs
@events.request.add_listener
def log_request(
        request_type,
        name,
        response_time,
        response_length,
        response,
        context,
        exception,
        **kwargs,
):
    url = None
    request_body = None
    response_text = None
    status_code = None

    if response is not None:
        try:
            url = response.request.url
        except Exception:
            url = kwargs.get("url")

        status_code = response.status_code

        # request_body
        try:
            request_body = response.request.body
        except Exception:
            request_body = None

        # encode to utf-8
        if isinstance(request_body, bytes):
            try:
                request_body = request_body.decode("utf-8", errors="replace")
            except Exception:
                request_body = repr(request_body)

        # process response_text
        try:
            response_text = response.text
        except Exception:
            response_text = None

    record = {
        "ts": time.time(),
        "type": request_type,
        "name": name,
        "url": url,
        "response_time_ms": response_time,
        "response_length": response_length,
        "status_code": status_code,
        "failure": str(exception) if exception else None,
        "request_body": request_body,
        "response_text": response_text,
    }

    # write to Log file
    try:
        with open("locust_requests.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[log_request] write error: {e}")


# Shared pool recourses
_USERS_POOL: List[Dict[str, Any]] = []
_USERS_POOL_LOCK = Lock()

_BLOG_ID_POOL: List[str] = []
_BLOG_POOL_LOCK = Lock()

_ROOT_COMMENT_POOL: List[str] = []
_ROOT_COMMENT_POOL_LOCK = Lock()


def _load_users_pool() -> None:
    """
    load user pool from users_pool.json
    """
    global _USERS_POOL
    if _USERS_POOL:
        return

    with _USERS_POOL_LOCK:
        if _USERS_POOL:
            return

    here = Path(__file__).resolve().with_name("users_pool.json")

    if here.exists():
        with here.open("r", encoding="utf-8") as f:
            _USERS_POOL = json.load(f)
        print(f"[INIT] Loaded {len(_USERS_POOL)} users from {here}")
    else:
        raise RuntimeError("users_pool.json not found in the script directory.")


def _pick_random(seq: List[Any]) -> Optional[Any]:
    if not seq:
        return None
    return random.choice(seq)



class MixedBlogUser(HttpUser):
    """
    Simulate a mixed User: Browse hottest list, blog details, write comments, write blogs, hit likes, and reply to comments
    - Request login and post with cookies
    - relogin if timeout
    """

    # CPU relief
    wait_time = between(0.2, 1.0)

    # account in use
    creds: Dict[str, Any] | None = None
    logged_in: bool = False


    def on_start(self) -> None:
        """
        Pick an account from the users pool, then login, then fill the initial blog/comment pool
        """
        _load_users_pool()
        self.creds = _pick_random(_USERS_POOL)
        if not self.creds:
            raise StopUser("No user credentials available in users_pool.json")

        if not self.login():
            raise StopUser("Initial login failed")

        # initialize blog pool
        self.ensure_blog_pool()
        # initialize root comment pool
        self.ensure_root_comments_pool()

    #
    def login(self) -> bool:
        """
        Call /users/login for login
        authenticate with cookie
        """
        assert self.creds is not None

        payload = {
            "email": self.creds["email"],
            "password": self.creds["password"],
        }

        resp: ResponseContextManager = self.client.post(
            "/users/login",
            json=payload,
            name="/users/login",
        )

        if resp.status_code == 200:
            self.logged_in = True
            return True
        else:
            print(
                f"[ensure_blog_pool] Init blog pool failed (status={resp.status_code}): {resp.text}"
            )
            self.logged_in = False
            return False

    def request_with_relogin(
            self,
            method: str,
            url: str,
            *,
            name: Optional[str] = None,
            **kwargs,
    ) -> ResponseContextManager:
        if name is None:
            name = url

        method = method.lower()
        client_method = getattr(self.client, method)

        # Initial request
        resp: ResponseContextManager = client_method(url, name=name, **kwargs)

        if resp.status_code == 401:
            # relogin on 401
            if self.login():
                resp = client_method(url, name=name + " (retry)", **kwargs)

        return resp



    # Shared recourses initialization
    def ensure_blog_pool(self) -> None:
        """
        blog_id pool init：
        pull some blog_id from /blogs/views/hottest
        """
        global _BLOG_ID_POOL
        if _BLOG_ID_POOL:
            return

        with _BLOG_POOL_LOCK:
            if _BLOG_ID_POOL:
                return

            params = {"limit": 50}
            resp = self.request_with_relogin(
                "get",
                "/blogs/views/hottest",
                params=params,
                name="/blogs/views/hottest",
            )

            if resp.status_code != 200:
                print(
                    f"[ensure_blog_pool] Init blog pool failed "
                    f"(status={resp.status_code}): {resp.text}"
                )
                return

            try:
                data = resp.json()
            except Exception as e:
                print("[ensure_blog_pool] JSON parse error:", e)
                return

            if not isinstance(data, list):
                print("[ensure_blog_pool] unexpected schema, expected list:", data)
                return

            collected = 0
            for item in data:
                blog_id = item.get("id")
                if isinstance(blog_id, str) and len(blog_id) >= 24:
                    _BLOG_ID_POOL.append(blog_id)
                    collected += 1

            print(f"[ensure_blog_pool] collected {collected} blog_ids")

    def ensure_root_comments_pool(self, max_blogs: int = 5) -> None:
        """
        comment pool init：
        pull some comment_id from /comments/blog/{blog_id} where blog_id is previously pull into the pool
        """
        global _ROOT_COMMENT_POOL
        if _ROOT_COMMENT_POOL:
            return

        if not _BLOG_ID_POOL:
            return

        with _ROOT_COMMENT_POOL_LOCK:
            if _ROOT_COMMENT_POOL:
                return

            sample_blog_ids = random.sample(
                _BLOG_ID_POOL, min(max_blogs, len(_BLOG_ID_POOL))
            )

            for blog_id in sample_blog_ids:
                params = {
                    "page": 1,
                    "size": 50,
                    "replies_page": 1,
                    "replies_size": 5,
                }
                resp = self.request_with_relogin(
                    "get",
                    f"/comments/blog/{blog_id}",
                    params=params,
                    name="/comments/blog/{blog_id}[init]",
                )
                if resp.status_code != 200:
                    continue

                data = resp.json()
                items = data.get("items") if isinstance(data, dict) else None
                if not isinstance(items, list):
                    continue

                for c in items:
                    cid = c.get("id")
                    if isinstance(cid, str) and len(cid) >= 24:
                        _ROOT_COMMENT_POOL.append(cid)

            if _ROOT_COMMENT_POOL:
                print(
                    f"[INIT] Collected {len(_ROOT_COMMENT_POOL)} root comment ids for pool"
                )



    # Utilities
    def get_random_blog_id(self) -> Optional[str]:
        if not _BLOG_ID_POOL:
            self.ensure_blog_pool()
        return _pick_random(_BLOG_ID_POOL)

    def get_random_root_comment_id(self) -> Optional[str]:
        if not _ROOT_COMMENT_POOL:
            self.ensure_root_comments_pool()
        return _pick_random(_ROOT_COMMENT_POOL)


    # Tasks
    @task(4)
    def browse_discover_blogs(self) -> None:
        """
        /search/blogs search blogs by keywords, the result page with preview, user chose to
        """
        params = {
            "page": random.randint(1, 20),
            "size": 10,
        }
        words = [
            "MongoDB", "Sharding", "ReplicaSet", "Performance", "Testing", "FastAPI",
            "Locust", "JWT", "Index", "Aggregation", "Benchmark", "Scalability",
            "Experiment", "Cluster", "Query", "Latency", "Throughput", "Design", "fsdf",
            "dw", "s", "ser2", "t", "ed", "op", "ed", "san", "esed", "sdf", "9"
        ]

        params["keyword"] = random.choice(words)

        resp = self.request_with_relogin(
            "get",
            "/search/blogs",
            params=params,
            name="/search/blogs",
        )

        if resp.status_code != 200:
            # Search failed
            return

        # validate JSON
        # parse
        try:
            data = resp.json()
        except Exception:
            return

        # fields
        if (
                not isinstance(data, dict)
                or "blogs" not in data
                or not isinstance(data["blogs"], dict)
        ):
            return

        items = data["blogs"].get("items")
        if not isinstance(items, list) or not items:
            return

        # preview all blogs
        for blog in items:
            blog_id = blog.get("blog_id")
            if not isinstance(blog_id, str) or len(blog_id) < 24:
                continue

            self.request_with_relogin(
                "get",
                f"/blogs/{blog_id}/preview",
                name="/blogs/[id]/preview",
            )

    @task(3)
    def view_hottest_blogs_and_tags(self) -> None:
        # view hottest blog
        self.request_with_relogin(
            "get",
            "/blogs/views/hottest",
            params={"limit": 10},
            name="/blogs/views/hottest",
        )

        # view hottest tag
        self.request_with_relogin(
            "get",
            "/blogs/tags/hottest",
            params={"limit": 10},
            name="/blogs/tags/hottest",
        )

    @task(4)
    def read_blog_detail_and_comments(self) -> None:
        blog_id = self.get_random_blog_id()
        if not blog_id:
            return

        # Blog deltail
        self.request_with_relogin(
            "get",
            f"/blogs/{blog_id}",
            name="/blogs/[blog_id]",
        )

        # list the comments
        params = {
            "page": random.randint(1, 10),
            "size": 10,
            "replies_page": random.randint(1, 5),
            "replies_size": 5,
        }
        self.request_with_relogin(
            "get",
            f"/comments/blog/{blog_id}",
            params=params,
            name="/comments/blog/[blog_id]",
        )



    @task(2)
    def toggle_like_blog(self) -> None:
        blog_id = self.get_random_blog_id()
        if not blog_id:
            return

        self.request_with_relogin(
            "post",
            f"/blogs/{blog_id}/like",
            name="/blogs/[blog_id]/like",
        )

    @task(3)
    def create_comment_or_reply(self) -> None:
        """
        creat comments where 70% to write on root and 30% to reply to comments
        """
        blog_id = self.get_random_blog_id()
        if not blog_id:
            return

        if random.random() < 0.7:
            parent_id = None
        else:
            parent_id = self.get_random_root_comment_id()

        payload = {
            "blog_id": blog_id,
            "parent_id": parent_id,
            "content": f"Locust mixed user comment: {random.randint(1, 1_000_000)}",
        }

        resp = self.request_with_relogin(
            "post",
            "/comments",
            json=payload,
            name="/comments (create)",
        )

        # for root comment created, add to resources pool
        if resp.status_code == 201:
            try:
                data = resp.json()
            except Exception:
                data = None

            if isinstance(data, dict) and data.get("is_root"):
                cid = data.get("id")
                if isinstance(cid, str) and len(cid) >= 24:
                    with _ROOT_COMMENT_POOL_LOCK:
                        _ROOT_COMMENT_POOL.append(cid)

    @task(1)
    def create_blog_post(self) -> None:
        payload = {
            "title": random_title(),
            "content": random_paragraph(),
            "tags": random_tags(),
        }

        resp = self.request_with_relogin(
            "post",
            "/blogs",
            json=payload,
            name="/blogs (create)",
        )

        # add new blog_id to the shared pool
        if resp.status_code == 201:
            try:
                data = resp.json()
            except Exception:
                data = None

            if isinstance(data, dict):
                bid = data.get("id")
                if isinstance(bid, str) and len(bid) >= 24:
                    with _BLOG_POOL_LOCK:
                        _BLOG_ID_POOL.append(bid)

    @task(2)
    def view_my_and_author_blogs(self) -> None:
        self.request_with_relogin(
            "get",
            "/blogs/author/me",
            params={"page": 1, "size": 10},
            name="/blogs/author/me",
        )

        # pick a random blog
        blog_id = self.get_random_blog_id()
        if not blog_id:
            return

        resp = self.request_with_relogin(
            "get",
            f"/blogs/{blog_id}",
            name="/blogs/[id] (detail for author)",
        )
        if resp.status_code != 200:
            return

        # get author_id from blog
        try:
            detail = resp.json()
        except Exception:
            return

        if not isinstance(detail, dict):
            return

        author_id = detail.get("author_id")
        if not isinstance(author_id, str) or len(author_id) < 10:
            return

        # load first page
        resp2 = self.request_with_relogin(
            "get",
            f"/blogs/author/{author_id}",
            params={"page": 1, "size": 10, "exclude_blog_id": blog_id},
            name="/blogs/author/[author_id]",
        )

        if resp2.status_code != 200:
            return

        # preview is call on all blogs on the returned list
        try:
            data = resp2.json()
        except Exception:
            return

        items = data.get("items")
        if not isinstance(items, list) or not items:
            return

        for blog in items:
            bid = blog.get("id")
            if isinstance(bid, str) and len(bid) >= 24:
                self.request_with_relogin(
                    "get",
                    f"/blogs/{bid}/preview",
                    name="/blogs/[id]/preview (author list)",
                )