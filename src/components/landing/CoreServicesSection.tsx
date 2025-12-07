import React from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Stack,
  alpha,
  Button
} from '@mui/material'
import {
  FilterAlt,
  Architecture,
  Assessment,
  Speed,
  TrendingUp,
  Analytics,
  ArrowForward,
  Terminal,
  Memory
} from '@mui/icons-material'

const CoreServicesSection: React.FC = () => {
  const services = [
    {
      icon: <FilterAlt sx={{ fontSize: 40 }} />,
      title: 'QUANT FILTER',
      subtitle: 'INVESTMENT UNIVERSE',
      description: 'Automatically screens high-quality stocks using 30+ financial and technical indicators.',
      features: [
        'PER, PBR, ROE METRICS',
        'REAL-TIME SCREENING',
        'CUSTOM PRESETS',
        'BACKTEST SYNC'
      ],
      color: '#00E5FF', // Cyan
    },
    {
      icon: <Architecture sx={{ fontSize: 40 }} />,
      title: 'STRATEGY BUILDER',
      subtitle: 'NO-CODE LOGIC BUILDER',
      description: 'Design complex trading algorithms without writing a single line of code.',
      features: [
        'DRAG & DROP INTERFACE',
        '50+ TECH INDICATORS',
        'MULTI-CONDITION LOGIC',
        'AUTO OPTIMIZATION'
      ],
      color: '#00FF88', // Neon Green
    },
    {
      icon: <Assessment sx={{ fontSize: 40 }} />,
      title: 'BACKTEST ENGINE',
      subtitle: 'HISTORICAL SIMULATION',
      description: 'Validate your strategy with 10 years of historical data in seconds.',
      features: [
        '10Y+ TICK DATA',
        'MDD/CAGR ANALYSIS',
        'SLIPPAGE ESTIMATION',
        'LOG VISUALIZATION'
      ],
      color: '#EA00FF', // Neon Purple
    }
  ]

  return (
    <Box
      sx={{
        py: 12,
        bgcolor: '#050912',
        position: 'relative',
        overflow: 'hidden',
        borderTop: `1px solid ${alpha('#00E5FF', 0.1)}`
      }}
    >
      {/* Grid Background Pattern */}
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `
            linear-gradient(rgba(0, 229, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
          opacity: 0.5,
          zIndex: 0
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        {/* Section Header */}
        <Stack spacing={2} sx={{ mb: 10 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Terminal sx={{ color: '#00E5FF', fontSize: 20 }} />
            <Typography
              variant="caption"
              sx={{
                color: '#00E5FF',
                fontFamily: '"JetBrains Mono", monospace',
                fontWeight: 700,
                letterSpacing: 2,
              }}
            >
              SYSTEM MODULES
            </Typography>
          </Box>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 800,
              color: '#fff',
              fontFamily: '"JetBrains Mono", monospace',
              textTransform: 'uppercase',
              letterSpacing: -1
            }}
          >
            CORE CAPABILITIES
          </Typography>
          <Box sx={{ width: 60, height: 4, bgcolor: '#00E5FF', mb: 2 }} />
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
            Deploy institutional-grade tools. From universe selection to execution.
          </Typography>
        </Stack>

        {/* Services Grid */}
        <Grid container spacing={4}>
          {services.map((service, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Box
                sx={{
                  height: '100%',
                  bgcolor: alpha('#0A0E1A', 0.8),
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${alpha(service.color, 0.3)}`,
                  position: 'relative',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: service.color,
                    boxShadow: `0 0 30px ${alpha(service.color, 0.15)}`,
                    transform: 'translateY(-5px)',
                    '& .icon-box': {
                      bgcolor: alpha(service.color, 0.2),
                      color: service.color
                    }
                  }
                }}
              >
                {/* Decorative corner markers */}
                <Box sx={{ position: 'absolute', top: 0, left: 0, width: 10, height: 10, borderTop: `2px solid ${service.color}`, borderLeft: `2px solid ${service.color}` }} />
                <Box sx={{ position: 'absolute', top: 0, right: 0, width: 10, height: 10, borderTop: `2px solid ${service.color}`, borderRight: `2px solid ${service.color}` }} />
                <Box sx={{ position: 'absolute', bottom: 0, left: 0, width: 10, height: 10, borderBottom: `2px solid ${service.color}`, borderLeft: `2px solid ${service.color}` }} />
                <Box sx={{ position: 'absolute', bottom: 0, right: 0, width: 10, height: 10, borderBottom: `2px solid ${service.color}`, borderRight: `2px solid ${service.color}` }} />

                <CardContent sx={{ p: 4 }}>
                  {/* Icon */}
                  <Box
                    className="icon-box"
                    sx={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 70,
                      height: 70,
                      bgcolor: alpha(service.color, 0.1),
                      border: `1px solid ${alpha(service.color, 0.3)}`,
                      color: service.color,
                      mb: 3,
                      transition: 'all 0.3s ease'
                    }}
                  >
                    {service.icon}
                  </Box>

                  {/* Title */}
                  <Typography
                    variant="caption"
                    sx={{
                      color: service.color,
                      fontWeight: 700,
                      letterSpacing: 1,
                      display: 'block',
                      mb: 1,
                      fontFamily: '"JetBrains Mono", monospace'
                    }}
                  >
                    {service.subtitle}
                  </Typography>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 800,
                      color: '#FFFFFF',
                      mb: 2,
                      fontFamily: '"JetBrains Mono", monospace',
                      letterSpacing: -1
                    }}
                  >
                    {service.title}
                  </Typography>

                  {/* Description */}
                  <Typography
                    variant="body2"
                    sx={{
                      color: '#8F9EB3',
                      lineHeight: 1.7,
                      mb: 4,
                      minHeight: 48
                    }}
                  >
                    {service.description}
                  </Typography>

                  {/* Features List */}
                  <Stack spacing={1.5} sx={{ mb: 4 }}>
                    {service.features.map((feature, idx) => (
                      <Stack
                        key={idx}
                        direction="row"
                        spacing={1.5}
                        alignItems="center"
                      >
                        <Box sx={{ width: 4, height: 4, bgcolor: service.color }} />
                        <Typography
                          variant="body2"
                          sx={{
                            color: '#fff',
                            fontSize: '0.85rem',
                            fontFamily: '"JetBrains Mono", monospace'
                          }}
                        >
                          {feature}
                        </Typography>
                      </Stack>
                    ))}
                  </Stack>

                  <Button
                    endIcon={<ArrowForward />}
                    sx={{
                      color: service.color,
                      fontWeight: 700,
                      fontFamily: '"JetBrains Mono", monospace',
                      p: 0,
                      '&:hover': {
                        bgcolor: 'transparent',
                        textDecoration: 'underline'
                      }
                    }}
                  >
                    ACCESS MODULE
                  </Button>
                </CardContent>
              </Box>
            </Grid>
          ))}
        </Grid>

        {/* Additional Features */}
        <Box sx={{ mt: 15 }}>
          <Typography
            variant="h5"
            sx={{
              fontWeight: 700,
              mb: 4,
              color: '#fff',
              textAlign: 'center',
              fontFamily: '"JetBrains Mono", monospace'
            }}
          >
            &gt;&gt; ADDITIONAL PARAMETERS
          </Typography>
          <Grid container spacing={2}>
            {[
              {
                icon: <Speed />,
                title: 'LATENCY',
                value: '< 50ms',
                desc: 'Execution speed'
              },
              {
                icon: <Memory />,
                title: 'CAPACITY',
                value: 'UNLIMITED',
                desc: 'Strategies per account'
              },
              {
                icon: <Analytics />,
                title: 'ANALYTICS',
                value: 'REAL-TIME',
                desc: 'Portfolio tracking'
              }
            ].map((feature, index) => (
              <Grid item xs={12} sm={4} key={index}>
                <Box
                  sx={{
                    p: 3,
                    bgcolor: alpha('#1A1F3A', 0.3),
                    border: `1px solid ${alpha('#fff', 0.1)}`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 3,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      borderColor: '#00E5FF',
                      transform: 'translateX(5px)'
                    }
                  }}
                >
                  <Box
                    sx={{
                      color: '#00E5FF',
                      '& svg': { fontSize: 32 }
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#8F9EB3',
                        fontFamily: '"JetBrains Mono", monospace'
                      }}
                    >
                      {feature.title}
                    </Typography>
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 700,
                        color: '#FFFFFF',
                        fontFamily: '"JetBrains Mono", monospace',
                        lineHeight: 1.2
                      }}
                    >
                      {feature.value}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#5C6B7F' }}>
                      {feature.desc}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Container>
    </Box>
  )
}

export default CoreServicesSection
