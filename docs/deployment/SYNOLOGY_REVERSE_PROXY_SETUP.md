# Synology Reverse Proxy Setup for api.bll-pro.com

## Step-by-Step Guide

### 1. Access Synology DSM Control Panel
1. Log into your Synology DSM
2. Open **Control Panel**
3. Navigate to **Application Portal** → **Reverse Proxy**

### 2. Create New Reverse Proxy Rule
Click **Create** and fill in the following settings:

#### General Tab:
- **Description**: Kiwoom Bridge API
- **Source:**
  - Protocol: HTTPS
  - Hostname: api.bll-pro.com
  - Port: 443
- **Destination:**
  - Protocol: HTTP
  - Hostname: localhost
  - Port: 8080

#### Custom Header Tab (Optional):
Add these headers if CORS issues persist:
- Create → WebSocket: No
- Add Headers:
  ```
  X-Real-IP: $remote_addr
  X-Forwarded-For: $proxy_add_x_forwarded_for
  X-Forwarded-Proto: https
  Host: $http_host
  ```

### 3. SSL Certificate Configuration
Since you already have certificates configured (as mentioned for N8N):

1. Go to **Control Panel** → **Security** → **Certificate**
2. Ensure the certificate for `*.bll-pro.com` or `api.bll-pro.com` is present
3. If not present, you can:
   - Use the existing certificate from Let's Encrypt
   - Or request a new certificate through DSM

### 4. Configure Certificate for the Service
1. In Certificate settings, click **Settings**
2. For the service **api.bll-pro.com**, select the appropriate certificate
3. Click **OK** to apply

### 5. Firewall Rules (if enabled)
Ensure port 443 is open for HTTPS traffic:
1. **Control Panel** → **Security** → **Firewall**
2. Check that HTTPS (port 443) is allowed

### 6. Apply Settings
1. Click **OK** to save the reverse proxy rule
2. The proxy should be active immediately

## Testing the Configuration

### Quick Test Commands:
```bash
# Test direct Docker access (should work)
curl http://YOUR_NAS_IP:8080/

# Test through Cloudflare + Synology (after setup)
curl https://api.bll-pro.com/

# Test the backtest endpoint
curl -X POST https://api.bll-pro.com/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{"strategy_id":"test","stock_codes":["005930"],"start_date":"2024-01-01","end_date":"2024-01-31","initial_capital":10000000}'
```

## Expected Flow:
1. User → `https://api.bll-pro.com` (Cloudflare)
2. Cloudflare → `https://YOUR_NAS_IP:443` (SSL/TLS Full mode)
3. Synology Reverse Proxy → `http://localhost:8080` (Docker container)
4. Docker Container (port 8080) → Kiwoom Bridge API (internal port 8001)

## Troubleshooting:

### If you get "502 Bad Gateway":
- Check if Docker container is running: `docker ps`
- Verify port mapping: Container should map 8080:8001
- Check Docker logs: `docker logs kiwoom-bridge`

### If you get "404 Not Found":
- Reverse proxy destination might be incorrect
- Verify the hostname is `localhost` not `127.0.0.1`

### If you get SSL/Certificate errors:
- Check certificate configuration in DSM
- Ensure Cloudflare SSL/TLS is set to "Full" mode

### If you still get HTML instead of JSON:
- The reverse proxy might be redirecting to DSM login page
- Check that the destination port (8080) is correct
- Ensure no authentication is required for the reverse proxy

## Notes:
- Port 8080 is used because it's a Cloudflare-supported port
- The Docker container internally uses port 8001 but exposes 8080
- SSL termination happens at Synology, internal traffic to Docker is HTTP