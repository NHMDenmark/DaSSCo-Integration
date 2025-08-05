#!/bin/bash

# Exit immediately on error
set -e

# Log file
LOG_FILE="/var/log/ssl_renewal.log"

# Timestamp
echo "===== SSL Renewal started: $(date) =====" | tee -a $LOG_FILE

# Renew certificates
echo "Running certbot renew..." | tee -a $LOG_FILE
certbot renew --quiet --no-self-upgrade | tee -a $LOG_FILE

# Reload Nginx to apply new certificates
echo "Reloading Nginx..." | tee -a $LOG_FILE
service nginx reload

echo "===== SSL Renewal completed: $(date) =====" | tee -a $LOG_FILE