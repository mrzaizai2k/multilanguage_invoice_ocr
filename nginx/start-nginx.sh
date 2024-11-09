#!/bin/bash

# Substitute environment variables in the nginx template
envsubst '${CLIENT_MAX_BODY_SIZE} ${DOMAIN_NAME}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Start NGINX
exec nginx -g 'daemon off;'