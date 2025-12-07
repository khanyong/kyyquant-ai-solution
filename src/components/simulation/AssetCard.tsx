import React from 'react';
import { Paper, Typography, Box, Chip, Tooltip } from '@mui/material';
import {
    TrendingUp,
    AccountBalance,
    Security,
    Warning,
    AttachMoney
} from '@mui/icons-material';
import { AssetProfile } from '../../utils/SimulationEngine';

interface AssetCardProps {
    asset: AssetProfile;
    onClick?: (asset: AssetProfile) => void;
    onDragStart?: (e: React.DragEvent, asset: AssetProfile) => void;
}

const AssetCard: React.FC<AssetCardProps> = ({ asset, onClick, onDragStart }) => {

    const getIcon = () => {
        switch (asset.category) {
            case 'equity': return <TrendingUp color="primary" />;
            case 'bond': return <AccountBalance color="secondary" />;
            case 'derivative': return <Warning color="error" />;
            case 'structured': return <AttachMoney color="success" />;
            default: return <Security />;
        }
    };

    const getRiskColor = (level: number) => {
        if (level <= 2) return '#4caf50'; // Green
        if (level === 3) return '#ff9800'; // Orange
        return '#f44336'; // Red
    };

    return (
        <Paper
            elevation={2}
            draggable={!!onDragStart}
            onDragStart={(e) => onDragStart && onDragStart(e, asset)}
            onClick={() => onClick && onClick(asset)}
            sx={{
                p: 2,
                mb: 1.5,
                cursor: onDragStart ? 'grab' : 'pointer',
                borderLeft: `4px solid ${getRiskColor(asset.riskLevel)}`,
                transition: 'transform 0.1s, box-shadow 0.1s',
                '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 3
                },
                '&:active': {
                    cursor: 'grabbing'
                }
            }}
        >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getIcon()}
                    <Typography variant="subtitle2" fontWeight="bold">
                        {asset.name}
                    </Typography>
                </Box>
                {asset.isTaxEfficient && (
                    <Tooltip title="연금계좌/ISA 등에서 절세 효과가 뛰어납니다">
                        <Chip label="절세상품" size="small" color="success" sx={{ height: 20, fontSize: '0.7rem' }} />
                    </Tooltip>
                )}
            </Box>

            <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                <Box>
                    <Typography variant="caption" color="text.secondary">수익률</Typography>
                    <Typography variant="body2" fontWeight="bold" color="primary.main">
                        {asset.expectedReturn}%
                    </Typography>
                </Box>
                <Box>
                    <Typography variant="caption" color="text.secondary">배당률</Typography>
                    <Typography variant="body2" fontWeight="bold" color="success.main">
                        {asset.dividendYield}%
                    </Typography>
                </Box>
                <Box>
                    <Typography variant="caption" color="text.secondary">위험도</Typography>
                    <Typography variant="body2" fontWeight="bold" sx={{ color: getRiskColor(asset.riskLevel) }}>
                        Lv.{asset.riskLevel}
                    </Typography>
                </Box>
            </Box>
        </Paper>
    );
};

export default AssetCard;
