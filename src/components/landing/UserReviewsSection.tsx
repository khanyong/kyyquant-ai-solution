import React from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Stack,
  Avatar,
  Rating,
  alpha,
  Chip
} from '@mui/material'
import {
  FormatQuote,
  Verified,
  TrendingUp,
  Terminal
} from '@mui/icons-material'

const UserReviewsSection: React.FC = () => {
  const reviews = [
    {
      id: 1,
      name: 'USER_KIM',
      role: 'OFFICE_WORKER',
      avatar: 'K',
      rating: 5,
      returnRate: 87.5,
      review: 'Backtesting capability is highly precise. Replaced gut-feeling trading with data verification. Auto-execution is seamless.',
      color: '#4CAF50'
    },
    {
      id: 2,
      name: 'USER_PARK',
      role: 'FULL_TIME_TRADER',
      avatar: 'P',
      rating: 5,
      returnRate: 142.3,
      review: 'First time using quant strategies after 10 years of manual trading. Visual Builder allows complex logic without coding.',
      color: '#FF9800'
    },
    {
      id: 3,
      name: 'USER_LEE',
      role: 'NOVICE',
      avatar: 'L',
      rating: 5,
      returnRate: 34.2,
      review: 'Templates and tutorials are excellent. Generating profit with small initial capital. Highly recommended for beginners.',
      color: '#00BCD4'
    },
    {
      id: 4,
      name: 'USER_CHOI',
      role: 'DEV_OPS',
      avatar: 'C',
      rating: 5,
      returnRate: 95.8,
      review: 'API documentation is clean. Easy to implement custom logic and test via the GUI. High data integrity.',
      color: '#9C27B0'
    },
    {
      id: 5,
      name: 'USER_JEONG',
      role: 'INVESTOR',
      avatar: 'J',
      rating: 5,
      returnRate: 52.1,
      review: 'Managing assets while busy with other tasks is now possible. The dashboard provides clear visibility.',
      color: '#E91E63'
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
              FIELD_REPORTS
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
            OPERATOR LOGS
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
            Decrypting transmission logs from active operators in the field.
          </Typography>
        </Stack>

        {/* Reviews Grid */}
        <Grid container spacing={3}>
          {reviews.map((review, index) => (
            <Grid item xs={12} md={index < 2 ? 6 : 4} key={review.id}>
              <Box
                sx={{
                  height: '100%',
                  bgcolor: '#0A0E1A',
                  border: `1px solid ${alpha(review.color, 0.3)}`,
                  position: 'relative',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: review.color,
                    boxShadow: `0 0 20px ${alpha(review.color, 0.15)}`,
                    transform: 'translateY(-5px)'
                  }
                }}
              >
                <CardContent sx={{ p: 4, position: 'relative' }}>

                  {/* Header with Avatar and Name */}
                  <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
                    <Avatar
                      sx={{
                        width: 40,
                        height: 40,
                        bgcolor: 'transparent',
                        border: `1px solid ${review.color}`,
                        color: review.color,
                        fontFamily: '"JetBrains Mono", monospace',
                        fontSize: '1rem',
                        fontWeight: 700
                      }}
                    >
                      {review.avatar}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Typography
                          variant="h6"
                          sx={{
                            fontWeight: 700,
                            color: review.color,
                            fontFamily: '"JetBrains Mono", monospace',
                            fontSize: '1rem'
                          }}
                        >
                          {review.name}
                        </Typography>
                        <Verified sx={{ fontSize: 16, color: review.color }} />
                      </Stack>
                      <Typography
                        variant="caption"
                        sx={{
                          color: '#5C6B7F',
                          fontFamily: '"JetBrains Mono", monospace'
                        }}
                      >
                        ID: {review.role}
                      </Typography>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography
                        variant="h5"
                        sx={{
                          fontWeight: 700,
                          color: '#fff',
                          fontFamily: '"JetBrains Mono", monospace'
                        }}
                      >
                        +{review.returnRate}%
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#5C6B7F', fontFamily: '"JetBrains Mono", monospace' }}>YIELD</Typography>
                    </Box>
                  </Stack>

                  <Box sx={{ borderTop: '1px dashed #2C3E50', my: 2 }} />

                  {/* Review Text */}
                  <Typography
                    variant="body2"
                    sx={{
                      color: '#B0BEC5',
                      lineHeight: 1.7,
                      fontFamily: '"JetBrains Mono", monospace',
                      mb: 2
                    }}
                  >
                    "{review.review}"
                  </Typography>

                  {/* Rating */}
                  <Rating
                    value={review.rating}
                    readOnly
                    size="small"
                    icon={<Terminal fontSize="inherit" />}
                    emptyIcon={<Terminal fontSize="inherit" />}
                    sx={{
                      '& .MuiRating-iconFilled': {
                        color: review.color
                      },
                      '& .MuiRating-iconEmpty': {
                        color: '#2C3E50'
                      }
                    }}
                  />

                </CardContent>
              </Box>
            </Grid>
          ))}
        </Grid>

        {/* Bottom Aggregated Stats */}
        <Box
          sx={{
            mt: 8,
            p: 4,
            bgcolor: alpha('#1A1F3A', 0.5),
            border: `1px solid ${alpha('#FFB800', 0.3)}`,
            textAlign: 'center'
          }}
        >
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={4}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#FFB800', fontFamily: '"JetBrains Mono", monospace' }}>
                4.8 / 5.0
              </Typography>
              <Typography variant="caption" sx={{ color: '#5C6B7F', fontFamily: '"JetBrains Mono", monospace' }}>
                SYSTEM_RATING
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#4CAF50', fontFamily: '"JetBrains Mono", monospace' }}>
                98.5%
              </Typography>
              <Typography variant="caption" sx={{ color: '#5C6B7F', fontFamily: '"JetBrains Mono", monospace' }}>
                RETENTION_RATE
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#00E5FF', fontFamily: '"JetBrains Mono", monospace' }}>
                2,500+
              </Typography>
              <Typography variant="caption" sx={{ color: '#5C6B7F', fontFamily: '"JetBrains Mono", monospace' }}>
                ACTIVE_OPERATORS
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  )
}

export default UserReviewsSection
