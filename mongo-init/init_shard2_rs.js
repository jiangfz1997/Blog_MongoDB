// initialize shard2 replica set
// member: mongo-shard2-1, mongo-shard2-2, mongo-shard2-3

(function () {
    print(">>> Initializing shard2 replica set");

    var config = {
        _id: "shard2",
        members: [
            {_id: 0, host: "mongo-shard2-1:27017"},
            {_id: 1, host: "mongo-shard2-2:27017"},
            {_id: 2, host: "mongo-shard2-3:27017"}
        ]
    };

    try {
        var status = rs.status();
        if (status.ok === 1) {
            print(">>> shard2 already initialized");
            return;
        }
    } catch (e) {
        print(">>> rs.status() failed, proceeding with rs.initiate");
    }

    try {
        rs.initiate(config);
        print(">>> shard2 initiated succeed");
    } catch (e2) {
        print(">>> Error during initialization: " + e2);
    }
})();
