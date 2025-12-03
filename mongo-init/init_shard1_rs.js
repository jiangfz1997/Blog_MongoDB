// initialize shard1 replica set
// members：mongo-shard1-1, mongo-shard1-2, mongo-shard1-3

(function () {
    print(">>> Initializing shard1 replica set");

    var config = {
        _id: "shard1",
        members: [
            {_id: 0, host: "mongo-shard1-1:27017"},
            {_id: 1, host: "mongo-shard1-2:27017"},
            {_id: 2, host: "mongo-shard1-3:27017"}
        ]
    };

    try {
        var status = rs.status();
        if (status.ok === 1) {
            print(">>> shard1 already initialized");
            return;
        }
    } catch (e) {
        print(">>> rs.status() failed, proceeding with rs.initiate");
    }

    try {
        rs.initiate(config);
        print(">>> shard1 initialization succeed");
    } catch (e2) {
        print(">>> Error during initialization: " + e2);
    }
})();
