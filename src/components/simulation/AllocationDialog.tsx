import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    TextField,
    Box,
    Slider,
    InputAdornment
} from '@mui/material';
import { AssetProfile } from '../../utils/SimulationEngine';

interface AllocationDialogProps {
    open: boolean;
    onClose: () => void;
    onConfirm: (amount: number) => void;
    asset: AssetProfile | null;
    remainingCash: number;
}

const AllocationDialog: React.FC<AllocationDialogProps> = ({ open, onClose, onConfirm, asset, remainingCash }) => {
    const [amount, setAmount] = useState<number>(0);
    const [percent, setPercent] = useState<number>(0);

    useEffect(() => {
        if (open) {
            setAmount(0);
            setPercent(0);
        }
    }, [open]);

    const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = Number(e.target.value);
        if (val >= 0 && val <= remainingCash) {
            setAmount(val);
            setPercent((val / remainingCash) * 100);
        }
    };

    const handleSliderChange = (_: Event, newValue: number | number[]) => {
        const p = newValue as number;
        setPercent(p);
        setAmount(Math.floor(remainingCash * (p / 100)));
    };

    if (!asset) return null;

    return (
        <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
            <DialogTitle>투자 금액 설정</DialogTitle>
            <DialogContent>
                <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                        {asset.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        남은 투자 가능 금액: {remainingCash.toLocaleString()}원
                    </Typography>
                </Box>

                <Box sx={{ mb: 4 }}>
                    <Typography gutterBottom>비중 설정 ({percent.toFixed(0)}%)</Typography>
                    <Slider
                        value={percent}
                        onChange={handleSliderChange}
                        aria-labelledby="allocation-slider"
                        valueLabelDisplay="auto"
                    />
                </Box>

                <TextField
                    fullWidth
                    label="투자 금액"
                    value={amount}
                    onChange={handleAmountChange}
                    type="number"
                    InputProps={{
                        endAdornment: <InputAdornment position="end">원</InputAdornment>,
                    }}
                    helperText={`최대 ${remainingCash.toLocaleString()}원까지 투자 가능`}
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>취소</Button>
                <Button onClick={() => onConfirm(amount)} variant="contained" disabled={amount <= 0}>
                    확인
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AllocationDialog;
