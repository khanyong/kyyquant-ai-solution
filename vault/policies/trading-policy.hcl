# Trading Application Policy

# API Keys - Read access for authenticated users
path "secret/data/api-keys/{{identity.entity.id}}/*" {
  capabilities = ["read", "list"]
}

# Trading strategies - Full access to own strategies
path "secret/data/strategies/{{identity.entity.id}}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Shared market data - Read only
path "secret/data/market-data/*" {
  capabilities = ["read", "list"]
}

# Backtest results - Read/Write for own results
path "secret/data/backtest-results/{{identity.entity.id}}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Encryption keys - Read only for app encryption key
path "transit/decrypt/app-encryption" {
  capabilities = ["update"]
}

path "transit/encrypt/app-encryption" {
  capabilities = ["update"]
}

# Database credentials - Dynamic database credentials
path "database/creds/trading-app" {
  capabilities = ["read"]
}

# AWS credentials for S3 access
path "aws/creds/trading-s3-role" {
  capabilities = ["read"]
}

# Audit logs - No access
path "audit/*" {
  capabilities = ["deny"]
}

# System paths - No access
path "sys/*" {
  capabilities = ["deny"]
}