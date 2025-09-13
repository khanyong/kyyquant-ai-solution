#!/bin/bash

# Vault Setup Script for KYY Quant AI Solution

echo "Setting up HashiCorp Vault for Trading Application..."

# Start Vault server
vault server -config=vault-config.hcl &
VAULT_PID=$!
sleep 5

# Initialize Vault
vault operator init -key-shares=5 -key-threshold=3 > init-keys.txt

# Unseal Vault (using first 3 keys from init)
vault operator unseal $(grep 'Key 1:' init-keys.txt | awk '{print $NF}')
vault operator unseal $(grep 'Key 2:' init-keys.txt | awk '{print $NF}')
vault operator unseal $(grep 'Key 3:' init-keys.txt | awk '{print $NF}')

# Login with root token
export VAULT_TOKEN=$(grep 'Initial Root Token:' init-keys.txt | awk '{print $NF}')

# Enable required secret engines
echo "Enabling secret engines..."
vault secrets enable -path=secret kv-v2
vault secrets enable transit
vault secrets enable database
vault secrets enable aws

# Configure Transit encryption
echo "Configuring encryption..."
vault write -f transit/keys/app-encryption

# Configure database secret engine
echo "Configuring database connections..."
vault write database/config/postgresql \
    plugin_name=postgresql-database-plugin \
    allowed_roles="trading-app" \
    connection_url="postgresql://{{username}}:{{password}}@localhost:5432/trading_db" \
    username="vault" \
    password="vault-password"

# Create database role
vault write database/roles/trading-app \
    db_name=postgresql \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"

# Configure AWS secret engine
echo "Configuring AWS integration..."
vault write aws/config/root \
    access_key=YOUR_AWS_ACCESS_KEY \
    secret_key=YOUR_AWS_SECRET_KEY \
    region=ap-northeast-2

# Create AWS role for S3 access
vault write aws/roles/trading-s3-role \
    credential_type=iam_user \
    policy_document=-<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::trading-bucket/*"
    }
  ]
}
EOF

# Enable authentication methods
echo "Configuring authentication..."
vault auth enable jwt
vault auth enable userpass

# Configure JWT auth for application
vault write auth/jwt/config \
    oidc_discovery_url="https://your-supabase-project.supabase.co" \
    oidc_client_id="your-client-id" \
    oidc_client_secret="your-client-secret"

# Create JWT role
vault write auth/jwt/role/trading-user \
    bound_audiences="your-client-id" \
    user_claim="sub" \
    role_type="jwt" \
    policies="trading-policy" \
    ttl=1h

# Apply policies
echo "Applying security policies..."
vault policy write trading-policy policies/trading-policy.hcl

# Create sample API keys (encrypted)
echo "Storing initial secrets..."
vault kv put secret/api-keys/shared \
    kiwoom_app_key="encrypted_app_key" \
    kiwoom_app_secret="encrypted_app_secret" \
    openai_api_key="encrypted_openai_key" \
    perplexity_api_key="encrypted_perplexity_key"

# Enable audit logging
echo "Enabling audit logging..."
vault audit enable file file_path=/vault/logs/audit.log

# Create AppRole for application authentication
vault auth enable approle
vault write auth/approle/role/trading-app \
    token_policies="trading-policy" \
    token_ttl=1h \
    token_max_ttl=4h

# Get RoleID and SecretID for application
ROLE_ID=$(vault read -field=role_id auth/approle/role/trading-app/role-id)
SECRET_ID=$(vault write -field=secret_id -f auth/approle/role/trading-app/secret-id)

echo "==============================================="
echo "Vault Setup Complete!"
echo "==============================================="
echo "Root Token: $(grep 'Initial Root Token:' init-keys.txt | awk '{print $NF}')"
echo "Role ID: $ROLE_ID"
echo "Secret ID: $SECRET_ID"
echo "==============================================="
echo "IMPORTANT: Store init-keys.txt securely and delete from server!"
echo "==============================================="