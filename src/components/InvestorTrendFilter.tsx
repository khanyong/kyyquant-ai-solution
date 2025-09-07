import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Stack,
  Chip,
  Button
} from '@mui/material';

interface InvestorFilters {
  foreign: {
    enabled: boolean;
    trend: 'accumulating' | 'distributing' | 'neutral';
    days: number;
    minAmount: number;
  };
  institution: {
    enabled: boolean;
    trend: 'accumulating' | 'distributing' | 'neutral';
    days: number;
    minAmount: number;
  };
  individual: {
    enabled: boolean;
    trend: 'accumulating' | 'distributing' | 'neutral';
    days: number;
    minAmount: number;
  };
}

interface InvestorTrendFilterProps {
  initialFilters?: InvestorFilters;
  onFilterChange: (filters: InvestorFilters) => void;
  onApplyFilter: () => void;
}

const InvestorTrendFilter: React.FC<InvestorTrendFilterProps> = ({
  initialFilters,
  onFilterChange,
  onApplyFilter
}) => {
  const defaultFilters: InvestorFilters = {
    foreign: {
      enabled: false,
      trend: 'neutral',
      days: 20,
      minAmount: 0
    },
    institution: {
      enabled: false,
      trend: 'neutral',
      days: 20,
      minAmount: 0
    },
    individual: {
      enabled: false,
      trend: 'neutral',
      days: 20,
      minAmount: 0
    }
  };

  const [filters, setFilters] = React.useState<InvestorFilters>(
    initialFilters || defaultFilters
  );

  const handleFilterChange = (
    investorType: keyof InvestorFilters,
    field: string,
    value: any
  ) => {
    const newFilters = {
      ...filters,
      [investorType]: {
        ...filters[investorType],
        [field]: value
      }
    };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const investorTypes = [
    { key: 'foreign' as const, label: '외국인' },
    { key: 'institution' as const, label: '기관' },
    { key: 'individual' as const, label: '개인' }
  ];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        투자자 동향 필터
      </Typography>
      
      <Stack spacing={2}>
        {investorTypes.map(({ key, label }) => (
          <Card key={key} variant="outlined">
            <CardContent>
              <Stack spacing={2}>
                <Stack direction="row" alignItems="center" justifyContent="space-between">
                  <Typography variant="subtitle1">{label}</Typography>
                  <Chip
                    label={filters[key].enabled ? '활성' : '비활성'}
                    color={filters[key].enabled ? 'primary' : 'default'}
                    onClick={() => handleFilterChange(key, 'enabled', !filters[key].enabled)}
                  />
                </Stack>

                {filters[key].enabled && (
                  <Stack spacing={2}>
                    <FormControl fullWidth size="small">
                      <InputLabel>동향</InputLabel>
                      <Select
                        value={filters[key].trend}
                        label="동향"
                        onChange={(e) => handleFilterChange(key, 'trend', e.target.value)}
                      >
                        <MenuItem value="accumulating">순매수 (축적)</MenuItem>
                        <MenuItem value="distributing">순매도 (분산)</MenuItem>
                        <MenuItem value="neutral">중립</MenuItem>
                      </Select>
                    </FormControl>

                    <Stack direction="row" spacing={2}>
                      <TextField
                        label="기간 (일)"
                        type="number"
                        size="small"
                        value={filters[key].days}
                        onChange={(e) => handleFilterChange(key, 'days', parseInt(e.target.value))}
                        inputProps={{ min: 1, max: 60 }}
                      />
                      
                      <TextField
                        label="최소 금액 (억원)"
                        type="number"
                        size="small"
                        value={filters[key].minAmount}
                        onChange={(e) => handleFilterChange(key, 'minAmount', parseFloat(e.target.value))}
                        inputProps={{ min: 0, step: 0.1 }}
                      />
                    </Stack>
                  </Stack>
                )}
              </Stack>
            </CardContent>
          </Card>
        ))}

        <Button
          variant="contained"
          onClick={onApplyFilter}
          fullWidth
        >
          필터 적용
        </Button>
      </Stack>
    </Box>
  );
};

export default InvestorTrendFilter;