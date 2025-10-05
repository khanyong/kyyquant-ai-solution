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
  TrendingUp
} from '@mui/icons-material'

const UserReviewsSection: React.FC = () => {
  const reviews = [
    {
      id: 1,
      name: '김*수',
      role: '직장인 투자자',
      avatar: 'K',
      rating: 5,
      verified: true,
      returnRate: 87.5,
      period: '6개월',
      review: '백테스팅 기능이 정말 강력합니다. 감으로 하던 투자를 이제는 데이터로 검증하고 실행할 수 있어서 수익률이 크게 개선됐어요. 특히 자동매매 기능 덕분에 퇴근 후에도 기회를 놓치지 않습니다.',
      color: '#4CAF50'
    },
    {
      id: 2,
      name: '박*영',
      role: '전업 투자자',
      avatar: 'P',
      rating: 5,
      verified: true,
      returnRate: 142.3,
      period: '1년',
      review: '10년 넘게 투자했지만 퀀트 전략은 처음이었습니다. KyyQuant 덕분에 코딩 없이도 복잡한 전략을 만들 수 있었고, 커뮤니티에서 고수들의 노하우를 배우며 실력이 많이 늘었어요.',
      color: '#FF9800'
    },
    {
      id: 3,
      name: '이*민',
      role: '초보 투자자',
      avatar: 'L',
      rating: 5,
      verified: true,
      returnRate: 34.2,
      period: '3개월',
      review: '투자 초보라 걱정했는데, 전략 템플릿과 튜토리얼이 정말 친절해서 금방 배울 수 있었습니다. 소액으로 시작했는데 벌써 수익이 나고 있어요!',
      color: '#00BCD4'
    },
    {
      id: 4,
      name: '최*호',
      role: '개발자',
      avatar: 'C',
      rating: 5,
      verified: true,
      returnRate: 95.8,
      period: '8개월',
      review: 'API 연동이 정말 편리합니다. 제 전략을 코드로 구현할 수도 있고, GUI로 빠르게 테스트할 수도 있어서 개발자 친화적이에요. 데이터 품질도 우수합니다.',
      color: '#9C27B0'
    },
    {
      id: 5,
      name: '정*아',
      role: '주부 투자자',
      avatar: 'J',
      rating: 5,
      verified: true,
      returnRate: 52.1,
      period: '5개월',
      review: '육아하면서 투자하기 어려웠는데, 자동매매로 시간 투자 없이도 수익을 낼 수 있게 됐어요. UI도 깔끔하고 사용하기 편해서 만족합니다.',
      color: '#E91E63'
    }
  ]

  return (
    <Box
      sx={{
        py: 12,
        background: '#0A0E1A',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Background Effects */}
      <Box
        sx={{
          position: 'absolute',
          top: '20%',
          right: '-10%',
          width: '600px',
          height: '600px',
          background: 'radial-gradient(circle, rgba(255, 184, 0, 0.06) 0%, transparent 70%)',
          pointerEvents: 'none'
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: '20%',
          left: '-10%',
          width: '600px',
          height: '600px',
          background: 'radial-gradient(circle, rgba(179, 136, 255, 0.06) 0%, transparent 70%)',
          pointerEvents: 'none'
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        {/* Section Header */}
        <Stack spacing={2} alignItems="center" textAlign="center" sx={{ mb: 10 }}>
          <Typography
            variant="overline"
            sx={{
              color: '#FFB800',
              fontWeight: 700,
              letterSpacing: 2,
              fontSize: '0.9rem'
            }}
          >
            USER REVIEWS
          </Typography>
          <Typography
            variant="h2"
            sx={{
              fontWeight: 800,
              background: 'linear-gradient(135deg, #FFFFFF 0%, #FFB800 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            실제 사용자들의 이야기
          </Typography>
          <Typography
            variant="h6"
            sx={{
              maxWidth: 700,
              color: alpha('#FFFFFF', 0.7),
              lineHeight: 1.8,
              fontWeight: 300
            }}
          >
            KyyQuant와 함께 성공적인 투자를 하고 있는 사용자들의 생생한 후기
          </Typography>
        </Stack>

        {/* Reviews Grid */}
        <Grid container spacing={3}>
          {reviews.map((review, index) => (
            <Grid item xs={12} md={index < 2 ? 6 : 4} key={review.id}>
              <Card
                sx={{
                  height: '100%',
                  background: alpha('#1A1F3A', 0.6),
                  backdropFilter: 'blur(20px)',
                  border: `1px solid ${alpha(review.color, 0.2)}`,
                  borderRadius: 3,
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    borderColor: alpha(review.color, 0.5),
                    boxShadow: `0 20px 60px ${alpha(review.color, 0.3)}`,
                    '& .quote-icon': {
                      transform: 'scale(1.1) rotate(-5deg)',
                    }
                  }
                }}
              >
                {/* Quote Icon */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: -20,
                    right: -20,
                    opacity: 0.1
                  }}
                >
                  <FormatQuote
                    className="quote-icon"
                    sx={{
                      fontSize: 120,
                      color: review.color,
                      transition: 'transform 0.3s ease'
                    }}
                  />
                </Box>

                {/* Top Bar */}
                <Box
                  sx={{
                    height: 3,
                    background: `linear-gradient(90deg, ${review.color} 0%, transparent 100%)`,
                  }}
                />

                <CardContent sx={{ p: 4, position: 'relative' }}>
                  {/* User Info */}
                  <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
                    <Avatar
                      sx={{
                        width: 56,
                        height: 56,
                        background: alpha(review.color, 0.2),
                        border: `3px solid ${alpha(review.color, 0.4)}`,
                        color: review.color,
                        fontSize: '1.5rem',
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
                            color: '#FFFFFF'
                          }}
                        >
                          {review.name}
                        </Typography>
                        {review.verified && (
                          <Verified
                            sx={{
                              fontSize: 18,
                              color: '#4CAF50'
                            }}
                          />
                        )}
                      </Stack>
                      <Typography
                        variant="body2"
                        sx={{
                          color: alpha('#FFFFFF', 0.6),
                          mb: 1
                        }}
                      >
                        {review.role}
                      </Typography>
                      <Rating
                        value={review.rating}
                        readOnly
                        size="small"
                        sx={{
                          '& .MuiRating-iconFilled': {
                            color: '#FFB800'
                          }
                        }}
                      />
                    </Box>
                  </Stack>

                  {/* Return Rate Badge */}
                  <Box
                    sx={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 1,
                      px: 2,
                      py: 1,
                      mb: 3,
                      borderRadius: 2,
                      background: alpha(review.color, 0.15),
                      border: `1px solid ${alpha(review.color, 0.3)}`
                    }}
                  >
                    <TrendingUp sx={{ color: review.color, fontSize: 18 }} />
                    <Typography
                      variant="body1"
                      sx={{
                        fontWeight: 700,
                        color: review.color
                      }}
                    >
                      +{review.returnRate}%
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        color: alpha('#FFFFFF', 0.6)
                      }}
                    >
                      {review.period} 수익률
                    </Typography>
                  </Box>

                  {/* Review Text */}
                  <Typography
                    variant="body1"
                    sx={{
                      color: alpha('#FFFFFF', 0.85),
                      lineHeight: 1.8,
                      fontStyle: 'italic'
                    }}
                  >
                    "{review.review}"
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Bottom Stats */}
        <Box
          sx={{
            mt: 8,
            p: 5,
            borderRadius: 3,
            background: `linear-gradient(135deg, ${alpha('#FFB800', 0.1)} 0%, ${alpha('#1A1F3A', 0.8)} 100%)`,
            border: `1px solid ${alpha('#FFB800', 0.3)}`,
            textAlign: 'center'
          }}
        >
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Typography
                variant="h3"
                sx={{
                  fontWeight: 900,
                  color: '#FFB800',
                  mb: 1
                }}
              >
                4.8/5.0
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: alpha('#FFFFFF', 0.7)
                }}
              >
                평균 평점
              </Typography>
              <Rating
                value={4.8}
                readOnly
                precision={0.1}
                sx={{
                  mt: 1,
                  '& .MuiRating-iconFilled': {
                    color: '#FFB800'
                  }
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography
                variant="h3"
                sx={{
                  fontWeight: 900,
                  color: '#4CAF50',
                  mb: 1
                }}
              >
                98.5%
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: alpha('#FFFFFF', 0.7)
                }}
              >
                고객 만족도
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography
                variant="h3"
                sx={{
                  fontWeight: 900,
                  color: '#00E5FF',
                  mb: 1
                }}
              >
                2,500+
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: alpha('#FFFFFF', 0.7)
                }}
              >
                활성 사용자
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  )
}

export default UserReviewsSection
