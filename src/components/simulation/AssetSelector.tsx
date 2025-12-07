import React, { useState } from 'react';
import { Box, Tabs, Tab, Typography } from '@mui/material';
import AssetCard from './AssetCard';
import { SIMULATION_ASSETS } from '../../constants/simulationAssets';
import { AssetProfile } from '../../utils/SimulationEngine';

interface AssetSelectorProps {
    onDragStart: (e: React.DragEvent, asset: AssetProfile) => void;
    onAssetClick?: (asset: AssetProfile) => void;
    darkTheme?: boolean;
}

const AssetSelector: React.FC<AssetSelectorProps> = ({ onDragStart, onAssetClick }) => {
    const [category, setCategory] = useState<string>('all');

    const filteredAssets = category === 'all'
        ? SIMULATION_ASSETS
        : SIMULATION_ASSETS.filter(a => a.category === category);

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Tabs
                value={category}
                onChange={(_, v) => setCategory(v)}
                variant="scrollable"
                scrollButtons="auto"
                sx={{ mb: 2, minHeight: 40 }}
            >
                <Tab label="전체" value="all" />
                <Tab label="주식형" value="equity" />
                <Tab label="채권형" value="bond" />
                <Tab label="배당/인컴" value="structured" />
                <Tab label="고수익/파생" value="derivative" />
            </Tabs>

            <Box sx={{ flexGrow: 1, overflowY: 'auto', pr: 1 }}>
                {filteredAssets.map(asset => (
                    <AssetCard
                        key={asset.id}
                        asset={asset}
                        onDragStart={onDragStart}
                        onClick={onAssetClick}
                    />
                ))}

                {filteredAssets.length === 0 && (
                    <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 4 }}>
                        해당 카테고리의 상품이 없습니다.
                    </Typography>
                )}
            </Box>
        </Box>
    );
};

export default AssetSelector;
