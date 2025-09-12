# 대체 인증서 생성 방법

## 방법 1: acme.sh 사용 (권장)
Synology DSM의 Let's Encrypt 대신 acme.sh 스크립트 사용

### SSH로 NAS 접속 후:
```bash
# acme.sh 설치
wget -O -  https://get.acme.sh | sh

# 인증서 발급 (standalone 모드)
~/.acme.sh/acme.sh --issue -d bll-pro.com -d api.bll-pro.com -d workflow.bll-pro.com --standalone --httpport 80

# 또는 webroot 모드 (Web Station 사용 시)
~/.acme.sh/acme.sh --issue -d bll-pro.com -d api.bll-pro.com -d workflow.bll-pro.com -w /volume1/web
```

## 방법 2: 기존 workflow 인증서 교체
기존 workflow.bll-pro.com 인증서를 새로 생성하되, 모든 도메인 포함

1. **Control Panel** → **Security** → **Certificate**
2. workflow.bll-pro.com 인증서 선택 → **Replace**
3. Domain name: `workflow.bll-pro.com`
4. Subject Alternative Name: `bll-pro.com;api.bll-pro.com`

## 방법 3: 개별 도메인으로 시도
한 번에 모든 도메인이 아닌 개별적으로 시도

1. 먼저 `api.bll-pro.com`만으로 시도:
   - Domain name: `api.bll-pro.com`
   - Subject Alternative Name: (비워둠)

2. 성공하면 나중에 교체하여 다른 도메인 추가

## 방법 4: DNS-01 Challenge 사용

1. Synology에서 인증서 생성 시작
2. DNS Challenge 선택 (가능한 경우)
3. 제공된 TXT 레코드를 Cloudflare에 추가:
   ```
   Type: TXT
   Name: _acme-challenge.bll-pro.com
   Content: [Let's Encrypt가 제공한 값]
   ```
4. 각 도메인마다 TXT 레코드 추가:
   - `_acme-challenge.api.bll-pro.com`
   - `_acme-challenge.workflow.bll-pro.com`

## 방법 5: 수동 인증서 생성 후 업로드

### certbot 사용 (로컬 PC에서):
```bash
# certbot 설치 후
certbot certonly --manual --preferred-challenges dns -d bll-pro.com -d api.bll-pro.com -d workflow.bll-pro.com

# 생성된 인증서 파일을 Synology에 수동 업로드
```

### Synology에 업로드:
1. **Control Panel** → **Security** → **Certificate**
2. **Add** → **Import certificate**
3. 파일 업로드:
   - Private Key: `privkey.pem`
   - Certificate: `cert.pem`
   - Intermediate Certificate: `chain.pem`

## 문제 진단

### 1. 실제 응답 확인:
```bash
# Let's Encrypt가 보는 것과 동일한 확인
curl -H "Host: api.bll-pro.com" http://128.134.229.105/.well-known/acme-challenge/test
```

### 2. nginx 설정 확인:
Let's Encrypt 챌린지 경로가 제대로 설정되어 있는지 확인
```nginx
location /.well-known/acme-challenge/ {
    root /var/lib/letsencrypt/;
}
```

### 3. 포트 80 독점 프로세스 확인:
```bash
sudo netstat -tlnp | grep :80
```

## 임시 해결책: 자체 서명 인증서

긴급한 경우 자체 서명 인증서로 임시 운영:
1. **Control Panel** → **Security** → **Certificate**
2. **Add** → **Create certificate**
3. Create a self-signed certificate 선택

이후 Cloudflare SSL 모드를 "Full"에서 "Flexible"로 변경하면 작동
(보안상 권장하지 않음, 임시 방편)