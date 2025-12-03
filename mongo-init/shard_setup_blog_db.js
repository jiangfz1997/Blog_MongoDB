// enable sharding in blog_db

// switch to correct database
var dbName = "blog_db";
var db = db.getSiblingDB(dbName);

print(">>> Enabling sharding on database: " + dbName);
sh.enableSharding(dbName);

// blogs
// shard key: { author_id: 1 }
print(">>> Sharding collection: " + dbName + ".blogs by { author_id: 1 }");

sh.shardCollection(
    dbName + ".blogs",
    {author_id: 1}
);

// comments
// shard key: { blog_id: 1 }
print(">>> Sharding collection: " + dbName + ".comments by { blog_id: 1 }");

sh.shardCollection(
    dbName + ".comments",
    {blog_id: 1}
);

print(">>> users collection is not sharded");

print(">>> Sharding setup succeed");
