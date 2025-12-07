import React, { useEffect, useState } from 'react';
import { Box, Typography, Stack, alpha } from '@mui/material';
import { TrendingUp, TrendingDown, AutoAwesome } from '@mui/icons-material';

interface MarketItem {
    symbol: string;
    name: string;
    price: number;
    change: number;
    aiSignal: 'BUY' | 'SELL' | 'HOLD';
    confidence: number;
}

const MOCK_DATA: MarketItem[] = [
    { symbol: 'SEC', name: '삼성전자', price: 72500, change: 1.2, aiSignal: 'BUY', confidence: 88 },
    { symbol: 'SKH', name: 'SK하이닉스', price: 132000, change: 2.5, aiSignal: 'BUY', confidence: 92 },
    { symbol: 'LGES', name: 'LG에너지솔루션', price: 415000, change: -0.5, aiSignal: 'HOLD', confidence: 65 },
    { symbol: 'POSCO', name: 'POSCO홀딩스', price: 450000, change: 3.1, aiSignal: 'BUY', confidence: 85 },
    { symbol: 'NAVER', name: 'NAVER', price: 205000, change: -1.2, aiSignal: 'SELL', confidence: 78 },
    { symbol: 'KAKAO', name: '카카오', price: 54000, change: -0.8, aiSignal: 'HOLD', confidence: 60 },
    { symbol: 'HYUNDAI', name: '현대차', price: 245000, change: 1.5, aiSignal: 'BUY', confidence: 82 },
    { symbol: 'KIA', name: '기아', price: 115000, change: 1.8, aiSignal: 'BUY', confidence: 84 },
    { symbol: 'KB', name: 'KB금융', price: 65000, change: 0.5, aiSignal: 'HOLD', confidence: 70 },
    { symbol: 'SHINHAN', name: '신한지주', price: 42000, change: 0.2, aiSignal: 'HOLD', confidence: 68 },
];

const LiveMarketTicker: React.FC = () => {
    return (
        <Box
            sx={{
                width: '100%',
                bgcolor: '#050912', // Very dark background
                borderBottom: `1px solid ${alpha('#00E5FF', 0.15)}`,
                overflow: 'hidden',
                position: 'relative',
                height: 48,
                display: 'flex',
                alignItems: 'center',
                zIndex: 100,
            }}
        >
            {/* AI Status Badge */}
            <Box
                sx={{
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    bottom: 0,
                    px: 2,
                    bgcolor: '#050912',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    zIndex: 2,
                    borderRight: `1px solid ${alpha('#00E5FF', 0.15)}`,
                    boxShadow: '10px 0 20px rgba(0,0,0,0.5)',
                }}
            >
                <AutoAwesome sx={{ color: '#00E5FF', fontSize: 18, animation: 'pulse 2s infinite' }} />
                <Typography
                    variant="caption"
                    sx={{
                        color: '#00E5FF',
                        fontWeight: 700,
                        fontFamily: '"JetBrains Mono", monospace',
                        display: { xs: 'none', sm: 'block' }
                    }}
                >
                    AI QUANT SIGNAL
                </Typography>
            </Box>

            {/* Scrolling Content */}
            <Box
                sx={{
                    display: 'flex',
                    animation: 'scroll 30s linear infinite',
                    '&:hover': {
                        animationPlayState: 'paused',
                    },
                    '@keyframes scroll': {
                        '0%': { transform: 'translateX(0)' },
                        '100%': { transform: 'translateX(-50%)' },
                    },
                    pl: { xs: 8, sm: 20 }, // Offset for the badge
                    whiteSpace: 'nowrap',
                }}
            >
                {/* Duplicate data for infinite scroll effect */}
                {[...MOCK_DATA, ...MOCK_DATA].map((item, index) => (
                    <Stack
                        key={index}
                        direction="row"
                        alignItems="center"
                        spacing={1.5}
                        sx={{
                            mx: 3,
                            py: 0.5,
                            opacity: 0.9,
                            transition: 'opacity 0.2s',
                            '&:hover': { opacity: 1, cursor: 'pointer' },
                        }}
                    >
                        <Typography variant="body2" sx={{ color: '#fff', fontWeight: 600, fontFamily: '"JetBrains Mono", monospace' }}>
                            {item.name}
                        </Typography>

                        <Stack direction="row" alignItems="center" spacing={0.5}>
                            {item.change >= 0 ? (
                                <TrendingUp sx={{ fontSize: 14, color: '#00FF88' }} />
                            ) : (
                                <TrendingDown sx={{ fontSize: 14, color: '#FF3366' }} />
                            )}
                            <Typography
                                variant="body2"
                                sx={{
                                    color: item.change >= 0 ? '#00FF88' : '#FF3366',
                                    fontWeight: 600,
                                    fontFamily: '"JetBrains Mono", monospace'
                                }}
                            >
                                {Math.abs(item.change)}%
                            </Typography>
                        </Stack>

                        <Box
                            sx={{
                                px: 1,
                                py: 0.2,
                                borderRadius: 0, // Sharp edges for terminal look
                                bgcolor:
                                    item.aiSignal === 'BUY' ? alpha('#00FF88', 0.1) :
                                        item.aiSignal === 'SELL' ? alpha('#FF3366', 0.1) :
                                            alpha('#888', 0.1),
                                border: `1px solid ${item.aiSignal === 'BUY' ? alpha('#00FF88', 0.3) :
                                    item.aiSignal === 'SELL' ? alpha('#FF3366', 0.3) :
                                        alpha('#888', 0.3)
                                    }`,
                            }}
                        >
                            <Typography
                                variant="caption"
                                sx={{
                                    color:
                                        item.aiSignal === 'BUY' ? '#00FF88' :
                                            item.aiSignal === 'SELL' ? '#FF3366' :
                                                '#aaa',
                                    fontWeight: 700,
                                    fontSize: '0.7rem',
                                    fontFamily: '"JetBrains Mono", monospace' // Enforce font
                                }}
                            >
                                {item.aiSignal} {item.confidence}%
                            </Typography>
                        </Box>
                    </Stack>
                ))}
            </Box>

            <style>
                {`
          @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.9); }
            100% { opacity: 1; transform: scale(1); }
          }
        `}
            </style>
        </Box>
    );
};

export default LiveMarketTicker;
