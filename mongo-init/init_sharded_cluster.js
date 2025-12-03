// add shard1 and shard2 to cluster

(function () {
    print(">>> Configuring sharded cluster");

    //   check if shard existed
    function shardExists(shardName) {
        var res = db.adminCommand({listShards: 1});
        if (res.ok !== 1) {
            print(">>> listShards failed: " + tojson(res));
            return false;
        }
        return res.shards.some(function (s) {
            return s._id === shardName;
        });
    }


    //   add shard1
    if (shardExists("shard1")) {
        print(">>> shard1 already exists");
    } else {
        var shard1Conn = "shard1/mongo-shard1-1:27017,mongo-shard1-2:27017,mongo-shard1-3:27017";
        print(">>> Adding shard1: " + shard1Conn);
        var res1 = sh.addShard(shard1Conn);
        print(">>> add Shard shard1 result: " + JSON.stringify(res1));
    }


    //   add shard2
    if (shardExists("shard2")) {
        print(">>> shard2 already exists");
    } else {
        var shard2Conn = "shard2/mongo-shard2-1:27017,mongo-shard2-2:27017,mongo-shard2-3:27017";
        print(">>> Adding shard2: " + shard2Conn);
        var res2 = sh.addShard(shard2Conn);
        print(">>> add Shard shard2 result: " + JSON.stringify(res2));
    }

    print(">>> Sharded cluster succeed");
})();
