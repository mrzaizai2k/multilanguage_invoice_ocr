#!/bin/bash

# Determine which config to use based on DEBUG value
if [ "$DEBUG" = "True" ]; then
    CONFIG_PATH="/etc/nginx/dev/nginx.conf.template"
else
    CONFIG_PATH="/etc/nginx/prod/nginx.conf.template"
fi

# Substitute environment variables in the nginx template
envsubst '${CLIENT_MAX_BODY_SIZE} ${SERVER_IP}' < $CONFIG_PATH > /etc/nginx/nginx.conf

# Start NGINX
exec nginx -g 'daemon off;'