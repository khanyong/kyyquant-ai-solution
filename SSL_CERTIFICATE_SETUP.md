# SSL 인증서 설정 가이드 - api.bll-pro.com

## 현재 상황
- 기존 인증서: workflow.bll-pro.com (RSA/ECC)
- 필요한 인증서: api.bll-pro.com

## 옵션 1: 멀티 도메인 인증서 생성 (권장)
여러 서브도메인을 하나의 인증서에 포함

### Synology DSM에서 Let's Encrypt 멀티 도메인 인증서 생성:

1. **Control Panel** → **Security** → **Certificate**
2. **Add** 클릭 → **Add a new certificate** 선택
3. **Get a certificate from Let's Encrypt** 선택
4. 도메인 설정:
   - Domain name: `bll-pro.com`
   - Email: 본인 이메일
   - Subject Alternative Name: `api.bll-pro.com;workflow.bll-pro.com`
     (세미콜론으로 구분하여 한 줄에 입력)
   
   **주의**: 커스텀 도메인에서는 와일드카드(*.bll-pro.com) 미지원
   - Synology DDNS 도메인만 와일드카드 가능

5. **인증 방법**:
   - HTTP-01 Challenge 사용 (포트 80 필요)
   - 인증서 생성 시 Cloudflare 프록시 일시 비활성화 (회색 구름)

## 옵션 2: 개별 인증서 생성
api.bll-pro.com 전용 인증서 생성

### Synology DSM에서 생성:

1. **Control Panel** → **Security** → **Certificate**
2. **Add** 클릭 → **Add a new certificate** 선택
3. **Get a certificate from Let's Encrypt** 선택
4. 도메인 설정:
   - Domain name: `api.bll-pro.com`
   - Email: 본인 이메일

5. **HTTP Challenge** 사용 가능 (단일 도메인):
   - 포트 80이 열려있어야 함
   - Cloudflare 프록시 일시적으로 비활성화 필요 (회색 구름)

## 옵션 3: 기존 workflow.bll-pro.com 인증서 재생성
모든 필요한 도메인을 포함하여 재생성

1. **Control Panel** → **Security** → **Certificate**
2. 기존 인증서 선택 → **Renew** 또는 **Replace**
3. Subject Alternative Names에 추가:
   - `workflow.bll-pro.com`
   - `api.bll-pro.com`
   - `*.bll-pro.com` (선택사항)

## Cloudflare DNS 설정 확인

인증서 생성 전 DNS 설정:
```
Type: A
Name: api
Content: YOUR_NAS_IP (128.134.229.105)
Proxy status: DNS only (회색 구름) - 인증서 생성 시
Proxy status: Proxied (오렌지 구름) - 인증서 생성 후
```

## 인증서 적용

1. 인증서 생성 완료 후
2. **Control Panel** → **Security** → **Certificate**
3. **Settings** 클릭
4. 서비스별 인증서 할당:
   - `api.bll-pro.com` → 새로 생성한 인증서 선택
   - 또는 와일드카드 인증서 선택

## 리버스 프록시에 적용

1. **Application Portal** → **Reverse Proxy**
2. api.bll-pro.com 규칙 생성/수정
3. Source:
   - Protocol: HTTPS
   - Hostname: api.bll-pro.com
   - Port: 443

## 테스트

```bash
# SSL 인증서 확인
openssl s_client -connect api.bll-pro.com:443 -servername api.bll-pro.com

# API 응답 확인
curl https://api.bll-pro.com/
```

## 주의사항

- Let's Encrypt 인증서는 90일마다 갱신 필요 (DSM이 자동 갱신)
- DNS Challenge 사용 시 Cloudflare 프록시 유지 가능
- HTTP Challenge 사용 시 일시적으로 프록시 비활성화 필요
- 와일드카드 인증서가 관리 편의성 면에서 유리