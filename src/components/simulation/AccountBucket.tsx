import React from 'react';
import { Paper, Typography, Box, List, ListItem, IconButton, Chip } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { AssetProfile, AssetAllocation } from '../../utils/SimulationEngine';

interface AccountBucketProps {
    title: string;
    type: string;
    color: string;
    assets: AssetAllocation[];
    onDrop: (asset: AssetProfile) => void;
    onRemove: (id: string) => void;
}

const AccountBucket: React.FC<AccountBucketProps> = ({ title, color, assets, onDrop, onRemove }) => {
    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        const data = e.dataTransfer.getData('application/json');
        if (data) {
            const asset = JSON.parse(data) as AssetProfile;
            onDrop(asset);
        }
    };

    const totalAmount = assets.reduce((sum, item) => sum + item.amount, 0);

    return (
        <Paper
            elevation={3}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            sx={{
                p: 2,
                minHeight: 180,
                borderTop: `6px solid ${color}`,
                bgcolor: 'background.paper',
                transition: 'background-color 0.2s',
                '&:hover': {
                    bgcolor: 'rgba(0,0,0,0.02)'
                }
            }}
        >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="subtitle1" fontWeight="bold">
                    {title}
                </Typography>
                <Chip
                    label={`${(totalAmount / 10000).toLocaleString()}만원`}
                    size="small"
                    color="primary"
                    variant="outlined"
                />
            </Box>

            <List dense>
                {assets.map((item, index) => (
                    <ListItem
                        key={`${item.asset.id}-${index}`}
                        secondaryAction={
                            <IconButton edge="end" size="small" onClick={() => onRemove(item.asset.id)}>
                                <Delete fontSize="small" />
                            </IconButton>
                        }
                        sx={{
                            border: '1px solid #eee',
                            borderRadius: 1,
                            mb: 1,
                            bgcolor: 'background.default'
                        }}
                    >
                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                            <Box sx={{ flexGrow: 1 }}>
                                <Typography variant="body2" fontWeight="bold">
                                    {item.asset.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    수익 {item.asset.expectedReturn}% / 배당 {item.asset.dividendYield}%
                                </Typography>
                            </Box>
                            <Box sx={{ mr: 2, textAlign: 'right' }}>
                                <Typography variant="body2" fontWeight="bold" color="primary">
                                    {(item.amount / 10000).toLocaleString()}만원
                                </Typography>
                            </Box>
                        </Box>
                    </ListItem>
                ))}

                {assets.length === 0 && (
                    <Box sx={{ py: 4, textAlign: 'center', color: 'text.secondary', border: '2px dashed #eee', borderRadius: 2 }}>
                        <Typography variant="caption">상품을 여기에 드래그하세요</Typography>
                    </Box>
                )}
            </List>
        </Paper>
    );
};

export default AccountBucket;
