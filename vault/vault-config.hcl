# HashiCorp Vault Configuration for KYY Quant AI Solution

# Storage backend configuration
storage "postgresql" {
  connection_url = "postgres://user:password@localhost:5432/vault"
  table          = "vault_kv_store"
  max_parallel   = 128
}

# Listener configuration
listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/vault/certs/vault.crt"
  tls_key_file  = "/vault/certs/vault.key"
}

# API address
api_addr = "https://vault.yourdomain.com:8200"
cluster_addr = "https://vault.yourdomain.com:8201"

# UI
ui = true

# Logging
log_level = "info"
log_format = "json"

# Telemetry
telemetry {
  prometheus_retention_time = "0s"
  disable_hostname = true
}

# Seal configuration (using AWS KMS for auto-unseal)
seal "awskms" {
  region     = "ap-northeast-2"
  kms_key_id = "your-kms-key-id"
}