#!/bin/bash
cd ~/auto_stock/backend
# Extract keys handling potential Windows line endings
export SUPABASE_URL=$(grep '^SUPABASE_URL=' .env | cut -d '=' -f2 | tr -d '\r')
export SUPABASE_KEY=$(grep '^SUPABASE_KEY=' .env | cut -d '=' -f2 | tr -d '\r')

echo "Running update with URL: $SUPABASE_URL"
# Don't echo the key for security

sudo docker exec -e SUPABASE_URL="$SUPABASE_URL" -e SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_KEY" auto-stock-backend python update_dashboard_data.py
