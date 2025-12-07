import React from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  CardContent,
  Stack,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  alpha
} from '@mui/material'
import {
  CheckCircle,
  ArrowForward,
  Star,
  Terminal,
  Security,
  Speed
} from '@mui/icons-material'

interface PricingSectionProps {
  onLoginClick: () => void
}

const PricingSection: React.FC<PricingSectionProps> = ({ onLoginClick }) => {
  const plans = [
    {
      name: 'OBSERVER',
      price: 'FREE',
      period: '',
      description: 'Public access level. Basic market data access.',
      features: [
        '10 Backtest Cycles / Mo',
        'Basic Asset Filtering',
        '3 Algorithm Slots',
        'Daily Market Report',
        'Read-Only Community Access'
      ],
      color: '#90CAF9',
      popular: false,
      icon: <Terminal sx={{ color: '#90CAF9' }} />
    },
    {
      name: 'OPERATOR',
      price: '₩49,000',
      period: '/ MO',
      description: 'Professional trading clearance. Full system control.',
      features: [
        'Unlimited Backtesting',
        'Advanced Quantum Filters',
        'Unlimited Strategies',
        'Real-time Alpha Signals',
        'Auto-Execution Link',
        'Portfolio Analytics',
        'Priority Uplink'
      ],
      color: '#00E5FF', // Cyan
      popular: true,
      icon: <Speed sx={{ color: '#00E5FF' }} />
    },
    {
      name: 'INSTITUTIONAL',
      price: 'CONTACT',
      period: '',
      description: 'Enterprise-grade infrastructure for funds.',
      features: [
        'Operator Features Included',
        'Dedicated Server Node',
        'Direct Market Access API',
        'Custom Algorithm Dev',
        'Dedicated Account Manager',
        'On-site Training',
        'White-label Solution',
        'SLA Guarantee'
      ],
      color: '#B388FF', // Purple
      popular: false,
      icon: <Security sx={{ color: '#B388FF' }} />
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
      {/* Background Matrix Effect */}
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background: `
            radial-gradient(circle at 50% 50%, ${alpha('#00E5FF', 0.05)} 0%, transparent 50%),
            linear-gradient(rgba(0, 255, 136, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 136, 0.02) 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 50px 50px, 50px 50px',
          opacity: 0.5,
          pointerEvents: 'none'
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
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
              SYSTEM_ACCESS
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
            TERMINAL ACCESS LEVEL
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
            Select your clearance level. Upgrade capability available at any time.
          </Typography>
        </Stack>

        {/* Pricing Cards */}
        <Grid container spacing={4} alignItems="stretch">
          {plans.map((plan, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Box
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  bgcolor: plan.popular ? alpha(plan.color, 0.05) : '#0A0E1A',
                  border: `1px solid ${plan.popular ? plan.color : alpha(plan.color, 0.3)}`,
                  position: 'relative',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: plan.popular ? 'translateY(-10px)' : 'translateY(-5px)',
                    borderColor: plan.color,
                    boxShadow: `0 0 30px ${alpha(plan.color, 0.15)}`,
                  }
                }}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      right: 0,
                      bgcolor: plan.color,
                      color: '#000',
                      py: 0.5,
                      px: 2,
                      fontSize: '0.7rem',
                      fontWeight: 800,
                      fontFamily: '"JetBrains Mono", monospace'
                    }}
                  >
                    RECOMMENDED
                  </Box>
                )}

                <CardContent sx={{ p: 4, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                  {/* Header */}
                  <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
                    <Box sx={{ p: 1, border: `1px solid ${plan.color}`, color: plan.color, display: 'flex' }}>
                      {plan.icon}
                    </Box>
                    <Box>
                      <Typography
                        variant="h5"
                        sx={{
                          fontWeight: 700,
                          color: plan.color,
                          fontFamily: '"JetBrains Mono", monospace',
                          letterSpacing: 1
                        }}
                      >
                        {plan.name}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#5C6B7F', fontFamily: '"JetBrains Mono", monospace' }}>
                        ACCESS_LEVEL_{index + 1}
                      </Typography>
                    </Box>
                  </Stack>

                  {/* Price */}
                  <Box sx={{ mb: 4, py: 2, borderBottom: `1px solid ${alpha('#fff', 0.1)}` }}>
                    <Stack direction="row" alignItems="baseline" spacing={1}>
                      <Typography
                        variant="h3"
                        sx={{
                          fontWeight: 800,
                          color: '#fff',
                          fontFamily: '"JetBrains Mono", monospace'
                        }}
                      >
                        {plan.price}
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{
                          color: '#8F9EB3',
                          fontFamily: '"JetBrains Mono", monospace'
                        }}
                      >
                        {plan.period}
                      </Typography>
                    </Stack>
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#5C6B7F',
                        mt: 1,
                        fontSize: '0.8rem',
                        fontFamily: '"JetBrains Mono", monospace'
                      }}
                    >
                      {plan.description}
                    </Typography>
                  </Box>

                  {/* Features List */}
                  <List sx={{ mb: 4, flexGrow: 1 }}>
                    {plan.features.map((feature, idx) => (
                      <ListItem key={idx} sx={{ px: 0, py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 30 }}>
                          <Box sx={{ width: 6, height: 6, bgcolor: plan.color }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={feature}
                          primaryTypographyProps={{
                            variant: 'body2',
                            sx: { color: '#B0BEC5', fontFamily: '"JetBrains Mono", monospace', fontSize: '0.9rem' }
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>

                  {/* CTA Button */}
                  <Button
                    variant={plan.popular ? 'contained' : 'outlined'}
                    fullWidth
                    endIcon={<ArrowForward />}
                    onClick={onLoginClick}
                    sx={{
                      py: 1.5,
                      borderRadius: 0,
                      fontFamily: '"JetBrains Mono", monospace',
                      fontWeight: 700,
                      ...(plan.popular ? {
                        bgcolor: plan.color,
                        color: '#000',
                        '&:hover': {
                          bgcolor: alpha(plan.color, 0.8),
                          boxShadow: `0 0 20px ${alpha(plan.color, 0.4)}`
                        }
                      } : {
                        borderColor: plan.color,
                        color: plan.color,
                        '&:hover': {
                          borderColor: plan.color,
                          bgcolor: alpha(plan.color, 0.1)
                        }
                      })
                    }}
                  >
                    INITIALIZE_{plan.name}
                  </Button>
                </CardContent>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  )
}

export default PricingSection
