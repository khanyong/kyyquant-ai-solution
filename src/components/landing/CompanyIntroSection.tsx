import React from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Stack,
  alpha,
  useTheme
} from '@mui/material'
import {
  TrendingUp,
  Security,
  Speed,
  AutoGraph
} from '@mui/icons-material'

const CompanyIntroSection: React.FC = () => {
  const theme = useTheme()

  return (
    <Box sx={{ py: 12, bgcolor: '#050912' }}>
      <Container maxWidth="lg">
        {/* Section Header */}
        <Stack spacing={2} alignItems="center" textAlign="center" sx={{ mb: 10 }}>
          <Box
            sx={{
              border: '1px solid #FFB800',
              px: 2,
              py: 0.5,
              bgcolor: alpha('#FFB800', 0.1)
            }}
          >
            <Typography
              variant="caption"
              sx={{
                color: '#FFB800',
                fontWeight: 700,
                fontFamily: '"JetBrains Mono", monospace',
                letterSpacing: 2
              }}
            >
              SYSTEM_IDENTITY
            </Typography>
          </Box>
          <Typography
            variant="h2"
            sx={{
              fontWeight: 800,
              color: '#fff',
              fontFamily: '"JetBrains Mono", monospace',
              textTransform: 'uppercase',
              letterSpacing: -2
            }}
          >
            QUANTUM_CORE
          </Typography>
          <Typography
            variant="h6"
            sx={{
              maxWidth: 700,
              color: '#8F9EB3',
              lineHeight: 1.6,
              fontWeight: 400,
              fontFamily: '"JetBrains Mono", monospace'
            }}
          >
            Democratizing institutional-grade algorithmic trading infrastructure.
          </Typography>
        </Stack>

        {/* Mission & Vision */}
        <Grid container spacing={4} sx={{ mb: 12 }}>
          <Grid item xs={12} md={6}>
            <Box
              sx={{
                p: 5,
                height: '100%',
                bgcolor: '#0A0E1A',
                border: `1px solid ${alpha('#FFB800', 0.3)}`,
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.3s ease',
                '&:hover': {
                  borderColor: '#FFB800',
                  boxShadow: `0 0 30px ${alpha('#FFB800', 0.1)}`,
                }
              }}
            >
              {/* Decorative Header Line */}
              <Box sx={{ position: 'absolute', top: 0, left: 0, width: '100%', height: 2, bgcolor: '#FFB800' }} />

              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  mb: 3,
                  color: '#FFB800',
                  fontFamily: '"JetBrains Mono", monospace',
                  letterSpacing: -1
                }}
              >
                MISSION_DIRECTIVE
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: '#B0BEC5',
                  lineHeight: 1.8,
                  fontSize: '1rem',
                  fontFamily: '"JetBrains Mono", monospace'
                }}
              >
                To equip every individual with the data-driven precision of a hedge fund. We replace emotional trading with algorithmic certainty, providing the tools to analyze, execute, and profit from market inefficiencies.
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Box
              sx={{
                p: 5,
                height: '100%',
                bgcolor: '#0A0E1A',
                border: `1px solid ${alpha('#B388FF', 0.3)}`,
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.3s ease',
                '&:hover': {
                  borderColor: '#B388FF',
                  boxShadow: `0 0 30px ${alpha('#B388FF', 0.1)}`,
                }
              }}
            >
              {/* Decorative Header Line */}
              <Box sx={{ position: 'absolute', top: 0, left: 0, width: '100%', height: 2, bgcolor: '#B388FF' }} />

              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  mb: 3,
                  color: '#B388FF',
                  fontFamily: '"JetBrains Mono", monospace',
                  letterSpacing: -1
                }}
              >
                TERMINAL_VISION
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: '#B0BEC5',
                  lineHeight: 1.8,
                  fontSize: '1rem',
                  fontFamily: '"JetBrains Mono", monospace'
                }}
              >
                To eliminate the information asymmetry between retail and institutional capitals. We envision a future where sophisticated AI and big data analytics are the standard for all market participants, ensuring a level playing field.
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Core Values */}
        <Grid container spacing={3}>
          {[
            {
              icon: <AutoGraph sx={{ fontSize: 32 }} />,
              title: 'AI_ANALYTICS',
              description: 'Deep learning models scanning for optimal patterns.',
              color: '#00E5FF'
            },
            {
              icon: <TrendingUp sx={{ fontSize: 32 }} />,
              title: 'VERIFIED_TESTING',
              description: '10+ years of tick data for robust validation.',
              color: '#4CAF50'
            },
            {
              icon: <Speed sx={{ fontSize: 32 }} />,
              title: 'LOW_LATENCY',
              description: 'Millisecond execution via direct exchange uplinks.',
              color: '#FF6B00'
            },
            {
              icon: <Security sx={{ fontSize: 32 }} />,
              title: 'SECURE_VAULT',
              description: 'Enterprise-grade encryption for all data streams.',
              color: '#B388FF'
            }
          ].map((value, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Box
                sx={{
                  p: 4,
                  height: '100%',
                  bgcolor: '#050912',
                  border: `1px solid ${alpha(value.color, 0.2)}`,
                  textAlign: 'left',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    borderColor: value.color,
                    boxShadow: `0 0 20px ${alpha(value.color, 0.1)}`
                  }
                }}
              >
                <Box
                  sx={{
                    color: value.color,
                    mb: 2,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1
                  }}
                >
                  {value.icon}
                </Box>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    mb: 1,
                    color: '#fff',
                    fontFamily: '"JetBrains Mono", monospace',
                    fontSize: '1rem'
                  }}
                >
                  {value.title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: '#8F9EB3',
                    lineHeight: 1.6,
                    fontFamily: '"JetBrains Mono", monospace',
                    fontSize: '0.8rem'
                  }}
                >
                  {value.description}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>

        {/* Company Info - Schematic Style */}
        <Box
          sx={{
            mt: 12,
            p: 5,
            bgcolor: alpha('#1A1F3A', 0.3),
            border: '1px dashed #2C3E50',
            position: 'relative'
          }}
        >
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  mb: 3,
                  color: '#FFB800',
                  fontFamily: '"JetBrains Mono", monospace'
                }}
              >
                ENTITY_METADATA
              </Typography>
              <Stack spacing={2}>
                {[
                  { label: 'ENTITY_NAME', value: 'KyyQuant AI Solution' },
                  { label: 'CEO', value: 'James Hong' },
                  { label: 'ESTABLISHED', value: '2020.01' },
                  { label: 'PRIMARY_OP', value: 'Algorithmic Trading Platform' }
                ].map((item, index) => (
                  <Stack
                    key={index}
                    direction="row"
                    spacing={2}
                    sx={{
                      py: 1.5,
                      borderBottom: '1px solid #1E2732'
                    }}
                  >
                    <Typography
                      variant="body2"
                      sx={{
                        minWidth: 120,
                        color: '#5C6B7F',
                        fontFamily: '"JetBrains Mono", monospace'
                      }}
                    >
                      {item.label}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#fff',
                        fontFamily: '"JetBrains Mono", monospace'
                      }}
                    >
                      {item.value}
                    </Typography>
                  </Stack>
                ))}
              </Stack>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  mb: 3,
                  color: '#FFB800',
                  fontFamily: '"JetBrains Mono", monospace'
                }}
              >
                SYSTEM_LOGS
              </Typography>
              <Stack spacing={2}>
                {[
                  { year: '2024', event: 'Auto-Execution module upgraded to v3.0' },
                  { year: '2023', event: 'AI Backtest Engine v2.0 deployed' },
                  { year: '2022', event: 'Active User Base > 1,000 Nodes' },
                  { year: '2020', event: 'System Initialization (Founded)' }
                ].map((item, index) => (
                  <Stack
                    key={index}
                    direction="row"
                    spacing={2}
                    sx={{
                      alignItems: 'center'
                    }}
                  >
                    <Typography
                      variant="body2"
                      sx={{
                        minWidth: 50,
                        fontWeight: 700,
                        color: '#FFB800',
                        fontFamily: '"JetBrains Mono", monospace'
                      }}
                    >
                      {item.year}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{ color: '#5C6B7F', fontFamily: '"JetBrains Mono", monospace' }}
                    >
                      {'>>'}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#B0BEC5',
                        fontFamily: '"JetBrains Mono", monospace'
                      }}
                    >
                      {item.event}
                    </Typography>
                  </Stack>
                ))}
              </Stack>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  )
}

export default CompanyIntroSection
