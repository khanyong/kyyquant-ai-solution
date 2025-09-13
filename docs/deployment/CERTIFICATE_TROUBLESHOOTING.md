# Let's Encrypt 인증서 생성 문제 해결

## 오류: "Please check if your IP address, reverse proxy rules, and firewall settings are correctly configured"

### 해결 방법:

## 1. Cloudflare 프록시 일시 비활성화

1. [Cloudflare Dashboard](https://dash.cloudflare.com) 접속
2. bll-pro.com 도메인 선택
3. **DNS** 메뉴 클릭
4. 다음 레코드들의 프록시 상태 변경:
   - `bll-pro.com` - 오렌지 구름 → 회색 구름 (DNS only)
   - `api.bll-pro.com` - 오렌지 구름 → 회색 구름 (DNS only)  
   - `workflow.bll-pro.com` - 오렌지 구름 → 회색 구름 (DNS only)

## 2. Synology 포트 확인

### 포트 80이 열려있는지 확인:
1. **Control Panel** → **External Access** → **Router Configuration**
2. 포트 80이 NAS로 포워딩되어 있는지 확인
3. 없다면 추가:
   - External Port: 80
   - Internal Port: 80
   - Protocol: TCP

### 방화벽 확인:
1. **Control Panel** → **Security** → **Firewall**
2. 방화벽이 활성화된 경우:
   - 포트 80 (HTTP) 허용 규칙 확인
   - 포트 443 (HTTPS) 허용 규칙 확인

## 3. 인증서 재생성

1. Cloudflare 프록시를 비활성화한 후 5분 대기 (DNS 전파 시간)
2. Synology DSM에서 인증서 생성 재시도:
   - Domain name: `bll-pro.com`
   - Subject Alternative Name: `api.bll-pro.com;workflow.bll-pro.com`
3. Done 클릭

## 4. 성공 후 Cloudflare 프록시 재활성화

인증서 생성 성공 후:
1. Cloudflare Dashboard로 돌아가서
2. 모든 레코드를 다시 **Proxied** (오렌지 구름)로 변경
3. 변경사항 저장

## 대안: DNS-01 Challenge 사용

HTTP-01이 계속 실패하면 DNS Challenge 방법 사용:

1. Synology에서 인증서 생성 시 **DNS-01** 선택
2. Let's Encrypt가 제공하는 TXT 레코드 값 복사
3. Cloudflare DNS에 TXT 레코드 추가:
   - Type: TXT
   - Name: `_acme-challenge.bll-pro.com`
   - Content: [Let's Encrypt가 제공한 값]
4. 추가로 각 서브도메인에 대해:
   - `_acme-challenge.api.bll-pro.com`
   - `_acme-challenge.workflow.bll-pro.com`
5. DNS 전파 후 인증서 생성 계속 진행

## 포트 확인 명령어

로컬에서 포트 80이 열려있는지 테스트:
```bash
# Windows에서
telnet khanyong.asuscomm.com 80

# 또는 curl 사용
curl -I http://khanyong.asuscomm.com
```

## 주의사항

- Let's Encrypt는 도메인 소유권 확인을 위해 실제 서버에 접근해야 함
- Cloudflare 프록시가 활성화되어 있으면 Cloudflare IP로 연결되어 실패
- 인증서는 90일마다 자동 갱신되며, 갱신 시에도 같은 과정 필요 (자동화 가능)