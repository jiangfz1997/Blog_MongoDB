#!/bin/bash
set -e

apt-get update -qq && apt-get install -y wget tar

NODE_EXPORTER_VERSION="1.10.2"
cd /tmp
wget -q https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz
tar -xzf node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz
mv node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64/node_exporter /usr/local/bin/
chmod +x /usr/local/bin/node_exporter

/usr/local/bin/node_exporter --web.listen-address=":9100" &
echo "Node Exporter started on port 9100."

docker-entrypoint.sh mongod --bind_ip_all &
echo "MongoDB starting..."

until mongosh -u admin -p admin123 --authenticationDatabase admin --eval 'db.runCommand({ ping: 1 })' &>/dev/null; do
  echo "Waiting for MongoDB to accept connections..."
  sleep 2
done
echo "MongoDB is up!"

echo "Setting profiling level..."
mongosh -u admin -p admin123 --authenticationDatabase admin --eval 'db.setProfilingLevel(1)'
mongosh -u admin -p admin123 --authenticationDatabase admin --eval 'db.getSiblingDB("blog_db").setProfilingLevel(2)'
echo "Profiling configured successfully."

wait

