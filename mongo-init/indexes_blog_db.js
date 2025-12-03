// Create index for blog_db

var dbName = "blog_db";
var db = db.getSiblingDB(dbName);

print(">>> Creating indexes for database: " + dbName);

// blog index
var blogs = db.blogs;

print(">>> Creating indexes on blogs");

blogs.createIndex(
    {author_id: 1, created_at: -1},
    {name: "idx_blogs_author_createdAt"}
);

blogs.createIndex(
    {created_at: -1},
    {name: "idx_blogs_createdAt_desc"}
);

blogs.createIndex(
    {view_count: -1},
    {name: "idx_blogs_viewCount_desc"}
);

blogs.createIndex(
    {tags: 1},
    {name: "idx_blogs_tags"}
);


// comment index
var comments = db.comments;

print(">>> Creating indexes on comments");


comments.createIndex(
    {blog_id: 1, is_root: 1, created_at: 1},
    {name: "idx_comments_blog_root_createdAt"}
);


comments.createIndex(
    {root_id: 1, is_root: 1, created_at: 1},
    {name: "idx_comments_root_rootFlag_createdAt"}
);


// user index
var users = db.users;

print(">>> Creating indexes on users");


users.createIndex(
    {email: 1},
    {
        name: "uidx_users_email",
        unique: true,
        sparse: false
    }
);


users.createIndex(
    {username: 1},
    {
        name: "uidx_users_username",
        unique: true,
        sparse: false
    }
);

print(">>> Indexes creation succeed");
