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
  GitHub,
  Terminal
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'

const FooterSection: React.FC = () => {
  const navigate = useNavigate()
  return (
    <Box
      sx={{
        bgcolor: '#020408',
        borderTop: '1px solid #1E2732',
        pt: 10,
        pb: 4,
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Decorative Top Line */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: 1,
          background: 'linear-gradient(90deg, transparent, #00E5FF, transparent)'
        }}
      />

      <Container maxWidth="lg">
        <Grid container spacing={6}>
          {/* Company Info */}
          <Grid item xs={12} md={4}>
            <Stack spacing={3}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <Terminal sx={{ color: '#00E5FF' }} />
                <Typography
                  variant="h5"
                  sx={{
                    fontWeight: 800,
                    color: '#fff',
                    fontFamily: '"JetBrains Mono", monospace',
                    letterSpacing: -1
                  }}
                >
                  KYY_QUANT
                </Typography>
              </Stack>

              <Typography
                variant="body2"
                sx={{
                  color: '#8F9EB3',
                  lineHeight: 1.8,
                  fontFamily: '"JetBrains Mono", monospace'
                }}
              >
                Advanced algorithmic trading infrastructure for the modern era.
                Replacing emotion with execution.
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
                      color: '#5C6B7F',
                      border: '1px solid #1E2732',
                      borderRadius: 0,
                      '&:hover': {
                        color: '#00E5FF',
                        borderColor: '#00E5FF',
                        bgcolor: alpha('#00E5FF', 0.1)
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
                color: '#fff',
                mb: 3,
                fontFamily: '"JetBrains Mono", monospace',
                fontSize: '1rem'
              }}
            >
              MODULES
            </Typography>
            <Stack spacing={2}>
              {[
                { label: 'MARKETPLACE', path: '/services' },
                { label: 'STRATEGY_BUILDER', path: '/services' },
                { label: 'BACKTEST_ENGINE', path: '/services' },
                { label: 'AUTO_EXECUTION', path: '/services' }
              ].map((item, index) => (
                <Link
                  key={index}
                  onClick={() => navigate(item.path)}
                  underline="none"
                  sx={{
                    color: '#8F9EB3',
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                    fontFamily: '"JetBrains Mono", monospace',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      color: '#00E5FF',
                      pl: 1
                    }
                  }}
                >
                  {'>'} {item.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: '#fff',
                mb: 3,
                fontFamily: '"JetBrains Mono", monospace',
                fontSize: '1rem'
              }}
            >
              COMMUNITY
            </Typography>
            <Stack spacing={2}>
              {[
                { label: 'ANNOUNCEMENTS', requireLogin: true },
                { label: 'FORUM', requireLogin: true },
                { label: 'DEV_DOCS', requireLogin: true },
                { label: 'API_STATUS', requireLogin: true }
              ].map((item, index) => (
                <Link
                  key={index}
                  onClick={() => navigate('/')}
                  underline="none"
                  sx={{
                    color: '#8F9EB3',
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                    fontFamily: '"JetBrains Mono", monospace',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      color: '#00E5FF',
                      pl: 1
                    }
                  }}
                >
                  {'>'} {item.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: '#fff',
                mb: 3,
                fontFamily: '"JetBrains Mono", monospace',
                fontSize: '1rem'
              }}
            >
              ENTITY
            </Typography>
            <Stack spacing={2}>
              {[
                { label: 'ABOUT_US', path: '/about' },
                { label: 'CAREERS', path: '/about' },
                { label: 'PARTNERS', path: '/contact' },
                { label: 'CONTACT_UPLINK', path: '/contact' }
              ].map((item, index) => (
                <Link
                  key={index}
                  onClick={() => navigate(item.path)}
                  underline="none"
                  sx={{
                    color: '#8F9EB3',
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                    fontFamily: '"JetBrains Mono", monospace',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      color: '#00E5FF',
                      pl: 1
                    }
                  }}
                >
                  {'>'} {item.label}
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
                color: '#fff',
                mb: 3,
                fontFamily: '"JetBrains Mono", monospace',
                fontSize: '1rem'
              }}
            >
              UPLINK
            </Typography>
            <Stack spacing={2}>
              <Stack direction="row" spacing={1} alignItems="flex-start">
                <Email sx={{ fontSize: 16, color: '#FFB800', mt: 0.5 }} />
                <Typography
                  variant="body2"
                  sx={{
                    color: '#8F9EB3',
                    fontSize: '0.85rem',
                    fontFamily: '"JetBrains Mono", monospace'
                  }}
                >
                  support@kyyquant.com
                </Typography>
              </Stack>
              <Stack direction="row" spacing={1} alignItems="flex-start">
                <Phone sx={{ fontSize: 16, color: '#FFB800', mt: 0.5 }} />
                <Typography
                  variant="body2"
                  sx={{
                    color: '#8F9EB3',
                    fontSize: '0.85rem',
                    fontFamily: '"JetBrains Mono", monospace'
                  }}
                >
                  02-1234-5678
                </Typography>
              </Stack>
              <Stack direction="row" spacing={1} alignItems="flex-start">
                <LocationOn sx={{ fontSize: 16, color: '#FFB800', mt: 0.5 }} />
                <Typography
                  variant="body2"
                  sx={{
                    color: '#8F9EB3',
                    fontSize: '0.85rem',
                    fontFamily: '"JetBrains Mono", monospace'
                  }}
                >
                  SEOUL_HQ
                  <br />
                  123 Teheran-ro
                </Typography>
              </Stack>
            </Stack>
          </Grid>
        </Grid>

        <Divider sx={{ my: 6, borderColor: '#1E2732' }} />

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
                  color: '#5C6B7F',
                  fontSize: '0.75rem',
                  fontFamily: '"JetBrains Mono", monospace',
                  '&:hover': { color: '#fff' }
                }}
              >
                TERMS_OF_SERVICE
              </Link>
              <Link
                href="#"
                underline="none"
                sx={{
                  color: '#5C6B7F',
                  fontSize: '0.75rem',
                  fontFamily: '"JetBrains Mono", monospace',
                  '&:hover': { color: '#fff' }
                }}
              >
                PRIVACY_PROTOCOL
              </Link>
            </Stack>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography
              variant="body2"
              sx={{
                color: '#5C6B7F',
                fontSize: '0.75rem',
                fontFamily: '"JetBrains Mono", monospace',
                textAlign: { xs: 'center', md: 'right' }
              }}
            >
              © 2024 KYYQUANT. SYSTEMS OPERATIONAL.
            </Typography>
          </Grid>
        </Grid>

        {/* Disclaimer */}
        <Box sx={{ mt: 4, pt: 4, borderTop: '1px solid #1E2732' }}>
          <Typography
            variant="caption"
            sx={{
              color: '#455060',
              fontSize: '0.7rem',
              lineHeight: 1.6,
              display: 'block',
              textAlign: 'center',
              fontFamily: '"JetBrains Mono", monospace'
            }}
          >
            [RISK_DISCLOSURE]: Not investment advice. Capital at risk. Past performance is not indicative of future results.
            System uptime guarantees subject to SLA protocols.
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}

export default FooterSection
