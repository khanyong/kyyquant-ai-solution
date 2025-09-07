import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Stack,
  Alert,
  CircularProgress,
  Paper,
  Divider,
  TextField,
  InputAdornment,
  Grid
} from '@mui/material'
import {
  CloudDownload,
  Computer,
  Delete,
  Folder,
  AccessTime,
  FilterList,
  Search,
  Star,
  StarBorder,
  Info
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'
import { authService } from '../services/auth'

interface SavedFilter {
  id: string
  name: string
  description?: string
  filters: any
  appliedFilters: any
  filteredStocks?: any[]
  filterStats: any
  timestamp: string
  created_at?: string
  is_favorite?: boolean
  usage_count?: number
}

interface LoadFilterDialogProps {
  open: boolean
  onClose: () => void
  onLoadFilter: (filter: SavedFilter) => void
}

const LoadFilterDialog: React.FC<LoadFilterDialogProps> = ({
  open,
  onClose,
  onLoadFilter
}) => {
  const [activeTab, setActiveTab] = useState(0) // 0: 로컬, 1: 클라우드
  const [localFilters, setLocalFilters] = useState<SavedFilter[]>([])
  const [cloudFilters, setCloudFilters] = useState<SavedFilter[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFilter, setSelectedFilter] = useState<SavedFilter | null>(null)

  useEffect(() => {
    if (open) {
      loadFilters()
    }
  }, [open, activeTab])

  const loadFilters = async () => {
    setIsLoading(true)
    setError(null)

    try {
      if (activeTab === 0) {
        // 로컬 필터 로드
        const savedFilters = localStorage.getItem('savedFilters')
        if (savedFilters) {
          const filters = JSON.parse(savedFilters)
          setLocalFilters(filters.sort((a: any, b: any) => 
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          ))
        } else {
          setLocalFilters([])
        }
      } else {
        // 클라우드 필터 로드
        const user = await authService.getCurrentUser()
        if (!user) {
          setError('클라우드 필터를 보려면 로그인이 필요합니다.')
          setCloudFilters([])
          return
        }

        const { data, error: fetchError } = await supabase
          .from('kw_investment_filters')
          .select('*')
          .eq('user_id', user.id)
          .eq('is_active', true)
          .order('created_at', { ascending: false })

        if (fetchError) {
          console.error('Fetch error:', fetchError)
          setError('클라우드 필터를 불러오는 중 오류가 발생했습니다.')
          setCloudFilters([])
        } else {
          setCloudFilters(data || [])
        }
      }
    } catch (err) {
      console.error('Load error:', err)
      setError('필터를 불러오는 중 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteFilter = async (filterId: string, isLocal: boolean) => {
    if (!window.confirm('이 필터를 삭제하시겠습니까?')) {
      return
    }

    try {
      if (isLocal) {
        // 로컬 필터 삭제
        const savedFilters = localStorage.getItem('savedFilters')
        if (savedFilters) {
          const filters = JSON.parse(savedFilters)
          const updatedFilters = filters.filter((f: any) => f.id !== filterId)
          localStorage.setItem('savedFilters', JSON.stringify(updatedFilters))
          setLocalFilters(updatedFilters)
        }
      } else {
        // 클라우드 필터 삭제 (soft delete)
        const { error: deleteError } = await supabase
          .from('kw_investment_filters')
          .update({ is_active: false })
          .eq('id', filterId)

        if (deleteError) {
          console.error('Delete error:', deleteError)
          setError('필터 삭제 중 오류가 발생했습니다.')
        } else {
          setCloudFilters(cloudFilters.filter(f => f.id !== filterId))
        }
      }
    } catch (err) {
      console.error('Delete error:', err)
      setError('필터 삭제 중 오류가 발생했습니다.')
    }
  }

  const handleToggleFavorite = async (filterId: string, currentStatus: boolean) => {
    try {
      const { error: updateError } = await supabase
        .from('kw_investment_filters')
        .update({ is_favorite: !currentStatus })
        .eq('id', filterId)

      if (updateError) {
        console.error('Update error:', updateError)
      } else {
        setCloudFilters(cloudFilters.map(f => 
          f.id === filterId ? { ...f, is_favorite: !currentStatus } : f
        ))
      }
    } catch (err) {
      console.error('Favorite error:', err)
    }
  }

  const handleLoadFilter = async (filter: SavedFilter) => {
    // 클라우드 필터인 경우 사용 횟수 업데이트
    if (activeTab === 1) {
      await supabase
        .from('kw_investment_filters')
        .update({ 
          usage_count: (filter.usage_count || 0) + 1,
          last_used_at: new Date().toISOString()
        })
        .eq('id', filter.id)
    }

    onLoadFilter(filter)
    onClose()
  }

  const getFilteredList = () => {
    const list = activeTab === 0 ? localFilters : cloudFilters
    if (!searchQuery) return list

    return list.filter(f => 
      f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.description?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }

  const getFilterSummary = (filter: SavedFilter) => {
    const summary = []
    
    if (filter.appliedFilters?.valuation) summary.push('가치지표')
    if (filter.appliedFilters?.financial) summary.push('재무지표')
    if (filter.appliedFilters?.sector) summary.push('섹터')
    
    return summary
  }

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Folder />
            저장된 필터 불러오기
          </Box>
          <TextField
            size="small"
            placeholder="필터 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              )
            }}
            sx={{ width: 250 }}
          />
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
            <Tab 
              icon={<Computer />} 
              label={`로컬 (${localFilters.length})`} 
              iconPosition="start"
            />
            <Tab 
              icon={<CloudDownload />} 
              label={`클라우드 (${cloudFilters.length})`} 
              iconPosition="start"
            />
          </Tabs>
        </Box>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        ) : getFilteredList().length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center', bgcolor: 'background.default' }}>
            <FilterList sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              저장된 필터가 없습니다
            </Typography>
            <Typography variant="body2" color="text.secondary">
              투자설정에서 필터를 적용한 후 저장하세요
            </Typography>
          </Paper>
        ) : (
          <List sx={{ maxHeight: 400, overflow: 'auto' }}>
            {getFilteredList().map((filter) => (
              <React.Fragment key={filter.id}>
                <ListItem
                  button
                  selected={selectedFilter?.id === filter.id}
                  onClick={() => setSelectedFilter(filter)}
                  onDoubleClick={() => handleLoadFilter(filter)}
                >
                  <ListItemIcon>
                    <FilterList />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {filter.name}
                        {filter.is_favorite && (
                          <Star sx={{ fontSize: 16, color: 'warning.main' }} />
                        )}
                        {filter.usage_count && filter.usage_count > 0 && (
                          <Chip 
                            label={`${filter.usage_count}회 사용`} 
                            size="small" 
                            variant="outlined"
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        {filter.description && (
                          <Typography variant="body2" color="text.secondary">
                            {filter.description}
                          </Typography>
                        )}
                        <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                          {getFilterSummary(filter).map((type) => (
                            <Chip 
                              key={type}
                              label={type} 
                              size="small" 
                              variant="outlined"
                              color="primary"
                            />
                          ))}
                          <Chip 
                            label={`${filter.filterStats?.final || filter.filter_stats?.final || filter.filtered_stocks_count || 0}개 종목`} 
                            size="small" 
                            variant="filled"
                            color="success"
                          />
                        </Stack>
                        <Typography variant="caption" color="text.secondary">
                          <AccessTime sx={{ fontSize: 12, mr: 0.5 }} />
                          {new Date(filter.timestamp || filter.created_at || Date.now()).toLocaleString('ko-KR')}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Stack direction="row" spacing={1}>
                      {activeTab === 1 && (
                        <IconButton
                          size="small"
                          onClick={() => handleToggleFavorite(filter.id, !!filter.is_favorite)}
                        >
                          {filter.is_favorite ? <Star color="warning" /> : <StarBorder />}
                        </IconButton>
                      )}
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteFilter(filter.id, activeTab === 0)}
                      >
                        <Delete />
                      </IconButton>
                    </Stack>
                  </ListItemSecondaryAction>
                </ListItem>
                <Divider variant="inset" component="li" />
              </React.Fragment>
            ))}
          </List>
        )}

        {selectedFilter && (
          <Paper sx={{ p: 2, mt: 2, bgcolor: 'background.default' }}>
            <Typography variant="subtitle2" gutterBottom>
              선택된 필터 상세
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography variant="caption" color="text.secondary">
                  전체 종목
                </Typography>
                <Typography variant="h6">
                  {selectedFilter.filterStats?.total || 0}
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="caption" color="text.secondary">
                  필터링 후
                </Typography>
                <Typography variant="h6" color="primary.main">
                  {selectedFilter.filterStats?.final || 0}
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="caption" color="text.secondary">
                  선택률
                </Typography>
                <Typography variant="h6" color="success.main">
                  {selectedFilter.filterStats?.total ? 
                    Math.round((selectedFilter.filterStats.final / selectedFilter.filterStats.total) * 100) : 0}%
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          취소
        </Button>
        <Button
          onClick={() => selectedFilter && handleLoadFilter(selectedFilter)}
          variant="contained"
          disabled={!selectedFilter}
          startIcon={<CloudDownload />}
        >
          불러오기
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default LoadFilterDialog