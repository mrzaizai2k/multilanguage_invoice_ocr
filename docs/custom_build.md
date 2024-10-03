# Custom Build Instructions

This guide will walk you through setting up the system by building each part using Docker.

## Table of Contents
1. [Set Up MongoDB Database](#set-up-mongodb-database)
2. [Run Backend (FastAPI)](#run-backend-fastapi)
3. [Run Frontend](#run-frontend)
4. [Set Up NGINX](#set-up-nginx)

---

## Set Up MongoDB Database

You can set up a MongoDB database using Docker. Refer to the official MongoDB [documentation](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-community-with-docker/?msockid=12d1fdc9a4da62680b18e9ffa5036390).

For GUI management, download [MongoDB Compass](https://www.mongodb.com/try/download/compass).

Useful resources:
- [Python Change Streams](https://www.mongodb.com/developer/languages/python/python-change-streams/#how-to-set-up-a-local-cluster)
- [Replica Sets with PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/connection-targets/#replica-sets)
- [Deploying MongoDB Cluster with Docker](https://www.mongodb.com/resources/products/compatibilities/deploying-a-mongodb-cluster-with-docker#:~:text=Create%20a%20Docker%20network.%20Start%20three%20instances%20of,you%20will%20be%20able%20to%20experiment%20with%20it.?msockid=34c38bc4da6f68c918d898c8db6e69e0)

### Step-by-Step MongoDB Setup

1. Create a Docker network for your app:
   ```bash
   docker network create app-network
   ```

2. Run MongoDB:
   ```bash
   mkdir -p data/test-change-streams

   docker run -d \
      --name mongodb \
      -v /data/test-change-streams:/data/db \
      -p 27017:27017 \
      --network app-network \
      mongo:latest \
      mongod --replSet test-change-streams --logpath /data/db/mongodb.log --dbpath /data/db --port 27017

   docker exec -it mongodb mongosh --eval "rs.initiate()"
   
   docker exec -it mongodb mongosh --eval "rs.reconfig({_id: 'test-change-streams', members: [{ _id : 0, host : 'mongodb:27017'}]}, {force: true})"

   docker exec -it mongodb mongosh --eval "rs.status()"
   ```

---

## Run Backend (FastAPI)

1. Build the FastAPI Docker image:
   ```bash
   docker build -t multilanguage_invoice_ocr-fastapi .
   ```

2. Run the backend container:
   ```bash
   docker run -d --env-file .env \
      -v $(pwd)/config:/app/config \
      -v $(pwd)/src:/app/src \
      -p 8149:8149 \
      --network app-network \
      multilanguage_invoice_ocr-fastapi:latest
   ```

---

## Run Frontend

1. Navigate to the frontend directory:
   ```bash
   cd jwt-auth-frontend/
   ```

2. Build the frontend Docker image:
   ```bash
   docker build -t jwt-auth-frontend .
   ```

3. Run the frontend container:
   ```bash
   docker run -d \
      --name jwt-frontend-container \
      --network app-network \
      -p 3000:3000 \
      -v $(pwd)/src:/app/src \
      jwt-auth-frontend
   ```

---

## Set Up NGINX

Follow the steps outlined in this [guide](https://dev.to/theinfosecguy/how-to-deploy-a-fastapi-application-using-docker-on-aws-4m61) to set up NGINX.

1. Navigate to the `nginx` directory:
   ```bash
   cd nginx
   ```

2. Run the NGINX container:
   ```bash
   docker run -d \
      --name nginx \
      --network app-network \
      -p 80:80 \
      -v $(pwd)/nginx/nginx.conf.template:/etc/nginx/nginx.conf.template:ro \
      -e CLIENT_MAX_BODY_SIZE=${CLIENT_MAX_BODY_SIZE} \
      -e SERVER_IP=${SERVER_IP} \
      nginx
   ```

