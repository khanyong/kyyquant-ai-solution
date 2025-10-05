import React from 'react'
import {
  Box,
  Container,
  Grid,
  Typography,
  Stack,
  Link,
  IconButton,
  Divider,
  alpha
} from '@mui/material'
import {
  Email,
  Phone,
  LocationOn,
  Facebook,
  Twitter,
  Instagram,
  YouTube,
  GitHub
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'

const FooterSection: React.FC = () => {
  const navigate = useNavigate()
  return (
    <Box
      sx={{
        background: `linear-gradient(180deg, #0A0E1A 0%, #000000 100%)`,
        borderTop: `1px solid ${alpha('#FFB800', 0.2)}`,
        pt: 8,
        pb: 4
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={6}>
          {/* Company Info */}
          <Grid item xs={12} md={4}>
            <Stack spacing={3}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 800,
                  background: 'linear-gradient(135deg, #FFB800 0%, #FFFFFF 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                KyyQuant
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: alpha('#FFFFFF', 0.7),
                  lineHeight: 1.8
                }}
              >
                AI 기반 퀀트 투자 플랫폼으로
                개인 투자자의 성공적인 투자를 지원합니다.
                데이터와 알고리즘으로 더 나은 투자 결정을 내리세요.
              </Typography>

              {/* Social Links */}
              <Stack direction="row" spacing={1}>
                {[
                  { icon: <Facebook />, url: '#' },
                  { icon: <Twitter />, url: '#' },
                  { icon: <Instagram />, url: '#' },
                  { icon: <YouTube />, url: '#' },
                  { icon: <GitHub />, url: '#' }
                ].map((social, index) => (
                  <IconButton
                    key={index}
                    href={social.url}
                    sx={{
                      color: alpha('#FFFFFF', 0.6),
                      border: `1px solid ${alpha('#FFFFFF', 0.2)}`,
                      '&:hover': {
                        color: '#FFB800',
                        borderColor: '#FFB800',
                        background: alpha('#FFB800', 0.1)
                      }
                    }}
                  >
                    {social.icon}
                  </IconButton>
                ))}
              </Stack>
            </Stack>
          </Grid>

          {/* Quick Links */}
          <Grid item xs={12} sm={6} md={2}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: '#FFFFFF',
                mb: 3
              }}
            >
              서비스
            </Typography>
            <Stack spacing={2}>
              {[
                { label: '전체 서비스', path: '/services' },
                { label: '전략 마켓플레이스', path: '/services' },
                { label: '전략 빌더', path: '/services' },
                { label: '백테스팅', path: '/services' },
                { label: '자동매매', path: '/services' }
              ].map((item, index) => (
                <Link
                  key={index}
                  onClick={() => navigate(item.path)}
                  underline="none"
                  sx={{
                    color: alpha('#FFFFFF', 0.7),
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      color: '#FFB800',
                      transform: 'translateX(5px)'
                    }
                  }}
                >
                  {item.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: '#FFFFFF',
                mb: 3
              }}
            >
              커뮤니티
            </Typography>
            <Stack spacing={2}>
              {[
                { label: '공지사항', requireLogin: true },
                { label: '자유게시판', requireLogin: true },
                { label: 'Q&A', requireLogin: true },
                { label: '전략 공유', requireLogin: true },
                { label: '백테스트 결과', requireLogin: true }
              ].map((item, index) => (
                <Link
                  key={index}
                  onClick={() => navigate('/')}
                  underline="none"
                  sx={{
                    color: alpha('#FFFFFF', 0.7),
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      color: '#FFB800',
                      transform: 'translateX(5px)'
                    }
                  }}
                >
                  {item.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: '#FFFFFF',
                mb: 3
              }}
            >
              회사
            </Typography>
            <Stack spacing={2}>
              {[
                { label: '회사 소개', path: '/about' },
                { label: '팀 소개', path: '/about' },
                { label: '채용', path: '/about' },
                { label: '파트너십', path: '/contact' },
                { label: '블로그', path: '/about' }
              ].map((item, index) => (
                <Link
                  key={index}
                  onClick={() => navigate(item.path)}
                  underline="none"
                  sx={{
                    color: alpha('#FFFFFF', 0.7),
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      color: '#FFB800',
                      transform: 'translateX(5px)'
                    }
                  }}
                >
                  {item.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: '#FFFFFF',
                mb: 3
              }}
            >
              지원
            </Typography>
            <Stack spacing={2}>
              {[
                { label: '고객센터', path: '/contact' },
                { label: 'FAQ', path: '/contact' },
                { label: '이용가이드', path: '/services' },
                { label: '문의하기', path: '/contact' },
                { label: 'API 문서', path: '/services' }
              ].map((item, index) => (
                <Link
                  key={index}
                  onClick={() => navigate(item.path)}
                  underline="none"
                  sx={{
                    color: alpha('#FFFFFF', 0.7),
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      color: '#FFB800',
                      transform: 'translateX(5px)'
                    }
                  }}
                >
                  {item.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          {/* Contact Info */}
          <Grid item xs={12} sm={6} md={2}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: '#FFFFFF',
                mb: 3
              }}
            >
              연락처
            </Typography>
            <Stack spacing={2}>
              <Stack direction="row" spacing={1} alignItems="flex-start">
                <Email sx={{ fontSize: 20, color: '#FFB800', mt: 0.3 }} />
                <Typography
                  variant="body2"
                  sx={{
                    color: alpha('#FFFFFF', 0.7),
                    fontSize: '0.9rem'
                  }}
                >
                  support@kyyquant.com
                </Typography>
              </Stack>
              <Stack direction="row" spacing={1} alignItems="flex-start">
                <Phone sx={{ fontSize: 20, color: '#FFB800', mt: 0.3 }} />
                <Typography
                  variant="body2"
                  sx={{
                    color: alpha('#FFFFFF', 0.7),
                    fontSize: '0.9rem'
                  }}
                >
                  02-1234-5678
                </Typography>
              </Stack>
              <Stack direction="row" spacing={1} alignItems="flex-start">
                <LocationOn sx={{ fontSize: 20, color: '#FFB800', mt: 0.3 }} />
                <Typography
                  variant="body2"
                  sx={{
                    color: alpha('#FFFFFF', 0.7),
                    fontSize: '0.9rem'
                  }}
                >
                  서울시 강남구
                  <br />
                  테헤란로 123
                </Typography>
              </Stack>
            </Stack>
          </Grid>
        </Grid>

        <Divider sx={{ my: 6, borderColor: alpha('#FFFFFF', 0.1) }} />

        {/* Bottom Section */}
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={3}
              sx={{
                textAlign: { xs: 'center', md: 'left' }
              }}
            >
              <Link
                href="#"
                underline="none"
                sx={{
                  color: alpha('#FFFFFF', 0.6),
                  fontSize: '0.85rem',
                  '&:hover': { color: '#FFB800' }
                }}
              >
                이용약관
              </Link>
              <Link
                href="#"
                underline="none"
                sx={{
                  color: alpha('#FFFFFF', 0.6),
                  fontSize: '0.85rem',
                  '&:hover': { color: '#FFB800' }
                }}
              >
                개인정보처리방침
              </Link>
              <Link
                href="#"
                underline="none"
                sx={{
                  color: alpha('#FFFFFF', 0.6),
                  fontSize: '0.85rem',
                  '&:hover': { color: '#FFB800' }
                }}
              >
                법적고지
              </Link>
            </Stack>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography
              variant="body2"
              sx={{
                color: alpha('#FFFFFF', 0.5),
                fontSize: '0.85rem',
                textAlign: { xs: 'center', md: 'right' }
              }}
            >
              © 2024 KyyQuant AI Solution. All rights reserved.
            </Typography>
          </Grid>
        </Grid>

        {/* Company Details */}
        <Box
          sx={{
            mt: 4,
            p: 3,
            borderRadius: 2,
            background: alpha('#1A1F3A', 0.3),
            border: `1px solid ${alpha('#FFFFFF', 0.05)}`
          }}
        >
          <Typography
            variant="body2"
            sx={{
              color: alpha('#FFFFFF', 0.5),
              fontSize: '0.8rem',
              lineHeight: 1.8,
              textAlign: 'center'
            }}
          >
            상호: KyyQuant AI Solution | 대표자: 홍길동 | 사업자등록번호: 123-45-67890
            <br />
            주소: 서울시 강남구 테헤란로 123 | 통신판매업신고: 2024-서울강남-12345
            <br />
            고객센터: 02-1234-5678 | 이메일: support@kyyquant.com
          </Typography>
        </Box>

        {/* Disclaimer */}
        <Box sx={{ mt: 4 }}>
          <Typography
            variant="caption"
            sx={{
              color: alpha('#FFFFFF', 0.4),
              fontSize: '0.75rem',
              lineHeight: 1.6,
              display: 'block',
              textAlign: 'center'
            }}
          >
            투자 권유 및 조언이 아닙니다. 투자의 최종 결정은 투자자 본인의 판단과 책임하에 이루어져야 하며,
            투자에 따른 손실은 투자자 본인에게 귀속됩니다.
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}

export default FooterSection
