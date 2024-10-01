#!/bin/bash
# Substitute environment variables in the nginx template and create the final config
envsubst '${CLIENT_MAX_BODY_SIZE} ${SERVER_IP}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Start NGINX
nginx -g 'daemon off;'
