# Setup Multilanguage Invoice OCR System on an EC2 Instance

This document provides step-by-step instructions to set up the Multilanguage Invoice OCR system on an AWS EC2 instance. The setup involves creating an EC2 instance, installing Docker and Docker Compose, cloning the repository, configuring environment variables, and running the application using Docker Compose.

## Table of Contents
1. [Create EC2 Instance](#create-ec2-instance)
2. [Setup Docker and Docker Compose](#setup-docker-and-docker-compose)
    - [1. Update your package list](#1-update-your-package-list)
    - [2. Install Docker](#2-install-docker)
    - [3. Install Docker Compose](#3-install-docker-compose)
    - [4. Optional: Add user to Docker group](#4-optional-add-your-user-to-the-docker-group)
    - [5. Verify Docker Installation](#5-verify-docker-installation)
    - [6. Reboot the EC2 instance](#6-reboot-the-ec2-instance-optional)
3. [Clone Code, Setup .env File, and Run](#clone-code-setup-env-file-and-run)
4. [SSH to EC2 instance](#ssh-to-ec2-instance)

---

## Create EC2 Instance

1. Open the EC2 console on AWS and click **Launch Instances**.
2. Configure the instance with the following settings:
    - **SSH Key**: Set up `.pem` key for SSH access.
    - **Security Group**: Allow access from all IP addresses.
    - **Spot Instance**: Use spot instances for cost savings (optional).
    - **Request type**: Persistant
    - **Interrupt behavior**: Choose Stop
    - **Operating System**: Select **Ubuntu 22.04**.
    - **Instance Type**: Choose **t3.large** (must be t3, do not use t2 - Paddle error)
    - **Memory**: Set 16GB for optimal performance.

---

## Setup Docker and Docker Compose

### 1. Update your package list
Ensure that your package manager is up-to-date:
```bash
sudo apt update
```

### 2. Install Docker
Install Docker using the official Docker repository:

- Install necessary packages:
    ```bash
    sudo apt install apt-transport-https ca-certificates curl software-properties-common -y 
    ```

- Add Docker's GPG key:
    ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    ```

- Add Docker’s official APT repository:
    ```bash
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

- Update your package list again to include Docker’s repository:
    ```bash
    sudo apt update
    ```

- Install Docker:
    ```bash
    sudo apt install docker-ce docker-ce-cli containerd.io -y 
    ```

- Start and enable Docker:
    ```bash
    sudo systemctl start docker
    sudo systemctl enable docker
    ```

- Check Docker version:
    ```bash
    docker --version
    ```

### 3. Install Docker Compose
Install the latest version of Docker Compose:

- Download Docker Compose binary:
    ```bash
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    ```

- Apply executable permissions:
    ```bash
    sudo chmod +x /usr/local/bin/docker-compose
    ```

- Verify Docker Compose installation:
    ```bash
    docker-compose --version
    ```

### 4. Optional: Add your user to the Docker group
This step allows you to run Docker commands without using `sudo`:

- Add your user to the `docker` group:
    ```bash
    sudo usermod -aG docker $USER
    ```

- Log out and log back in to apply the group changes:
    ```bash
    exit
    ssh ubuntu@<your_ec2_public_ip>
    ```

### 5. Verify Docker Installation
Run a test container to ensure everything is working:
```bash
docker run hello-world
```

### 6. Reboot the EC2 instance (optional)
If necessary, reboot your EC2 instance:
```bash
sudo reboot
```

---

## Clone Code, Setup .env File, and Run

### 1. Clone the repository
Clone the Multilanguage Invoice OCR code from GitHub:
```bash
git clone https://github.com/mrzaizai2k/multilanguage_invoice_ocr.git
```

### 2. Setup `.env` file

Navigate to the project directory and create the `.env` file:
```bash
touch .env
nano .env
```

Add the following environment variables to the `.env` file:
```bash
OPENAI_API_KEY=
EMAIL_USER=
EMAIL_PASSWORD=
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CLIENT_MAX_BODY_SIZE=5M
SERVER_IP=
```

#### Explanation:
- **`OPENAI_API_KEY`**: Your API key from OpenAI for accessing its services.
- **`EMAIL_USER`**: The email address used for sending notifications or communications from the application.
- **`EMAIL_PASSWORD`**: The password or app-specific password for the email account. It's typically a string like `wckzqeq.....`.
- **`SECRET_KEY`**: A secret key used to sign the JWT (JSON Web Token) for securing the application.
- **`ALGORITHM`**: The hashing algorithm for the JWT, set to `HS256` (HMAC using SHA-256).
- **`ACCESS_TOKEN_EXPIRE_MINUTES`**: The expiration time for the access token in minutes (e.g., 30 minutes).
- **`CLIENT_MAX_BODY_SIZE`**: Specifies the maximum allowed request body size (e.g., `5M` for 5 MB).
- **`SERVER_IP`**: The public IP address of your EC2 instance where the application will be accessible.

### 3. Run the application
Use Docker Compose to build and run the application:
```bash
docker-compose up -d
```

This command will start the application in detached mode, running in the background.


## SSH to EC2 instance

If you want to SSH to EC2 instance you can do this:
    
   ```shell
   chmod 400 /path/to/your-key.pem && \
   ssh -i /path/to/your-key.pem username@public-ip
   ```

## Setup elastic IPs

You should setup elastic Ip as this [tutorial](https://www.geeksforgeeks.org/allocate-elastic-ip-address-to-ec2-instance-in-aws/).
Because each instance running will have a different IP address, elastic IP help you fixed the IP Addess. Much better in production

## Setup https

1. You should by a domain: can be from [Hostinger](https://hpanel.hostinger.com/)
2. Then map your domain to your public IP as this [tutorial](https://srini-dev.hashnode.dev/adding-custom-domain-to-ec2-instance-with-nginx)
3. Because we are running docker nginx so it's a bit complicated. [reference](https://youtu.be/J9jKKeV1XVE?si=DhCVBHrH9ua82rAg)
- in `nginx/nginx.conf.template` remove the 443 server part first, so we can take the cert
- 

```
./init-letsencrypt.sh
docker compose up -d
```
Then check if cert is downloaded in nginx docker
```
docker exec -it nginx /bin/bash
cd /etc/letsencrypt/live/${DOMAIN_NAME}/chain.pem
// or

docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot     --email your-email@gmail.com --agree-tos --no-eff-email     -d your-domain.com
```
- Add the 443 server block to file `nginx/nginx.conf.template`
- run `docker restart nginx`

