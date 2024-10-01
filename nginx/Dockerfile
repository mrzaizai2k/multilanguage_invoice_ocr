FROM nginx:latest

# Copy the startup script into the container
COPY start-nginx.sh /start-nginx.sh

# Set execute permission on the startup script
RUN chmod +x /start-nginx.sh

# Use the startup script to replace the default entrypoint
ENTRYPOINT ["/start-nginx.sh"]
