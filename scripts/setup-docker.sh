#!/bin/bash

# Exit on error
set -e

echo "Updating package list..."
sudo apt update

echo "Installing required packages..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

echo "Adding Docker's GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "Adding Docker's APT repository..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Updating package list to include Docker repository..."
sudo apt update

echo "Installing Docker..."
sudo apt install -y docker-ce docker-ce-cli containerd.io

echo "Starting and enabling Docker..."
sudo systemctl start docker
sudo systemctl enable docker

echo "Checking Docker version..."
docker --version

echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

echo "Applying executable permissions to Docker Compose..."
sudo chmod +x /usr/local/bin/docker-compose

echo "Verifying Docker Compose installation..."
docker-compose --version

echo "Adding current user to the Docker group..."
sudo usermod -aG docker $USER

echo "Setup complete! Please log out and log back in to apply Docker group changes."
