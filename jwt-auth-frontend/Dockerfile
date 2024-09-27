# Use an official Node.js image as the base image
FROM node:18.17.1-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code to the container (except node_modules)
COPY . .

# Expose the port that the app will run on
EXPOSE 3000

# Start the application using npm
CMD ["npm", "start"]
