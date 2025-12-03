// initialize config server replica set: cfg
// members: mongo-cfg1, mongo-cfg2, mongo-cfg3

(function () {
  print(">>> Initializing config server replica set cfg");

  var config = {
    _id: "cfg",
    configsvr: true,
    members: [
      { _id: 0, host: "mongo-cfg1:27017" },
      { _id: 1, host: "mongo-cfg2:27017" },
      { _id: 2, host: "mongo-cfg3:27017" }
    ]
  };

  try {
    var status = rs.status();
    if (status.ok === 1) {
      print(">>> Config RS cfg already initialized");
      return;
    }
  } catch (e) {
    print(">>> rs.status() failed, proceeding with rs.initiate");
  }

  try {
    rs.initiate(config);
    print(">>> Config RS cfg initiated succeed");
  } catch (e2) {
    print(">>> Error during initialization: " + e2);
  }
})();
