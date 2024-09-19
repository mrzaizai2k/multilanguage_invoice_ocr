#!/bin/bash
sleep 10
mongosh --host 0.0.0.0:27017 <<EOF
rs.initiate({
  _id: "test-change-streams",
  members: [
    { _id: 0, host: "0.0.0.0:27017" }
  ]
})
EOF