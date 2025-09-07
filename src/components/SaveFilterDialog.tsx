import React, { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  Alert,
  CircularProgress,
  Chip,
  Stack,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Divider
} from '@mui/material'
import {
  Save as SaveIcon,
  Cloud,
  Computer,
  CloudUpload,
  CloudDownload,
  Delete,
  CheckCircle,
  Info,
  Folder,
  AccessTime,
  FilterList
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'
import { authService } from '../services/auth'

interface SaveFilterDialogProps {
  open: boolean
  onClose: () => void
  filterData: {
    filters: any
    appliedFilters: any
    filteredStocks: any[]
    filterStats: any
  }
  onSaveComplete?: (saveType: 'local' | 'cloud', savedName: string) => void
}

const SaveFilterDialog: React.FC<SaveFilterDialogProps> = ({
  open,
  onClose,
  filterData,
  onSaveComplete
}) => {
  const [saveType, setSaveType] = useState<'local' | 'cloud'>('local')
  const [filterName, setFilterName] = useState('')
  const [description, setDescription] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleSaveTypeChange = (
    event: React.MouseEvent<HTMLElement>,
    newSaveType: 'local' | 'cloud' | null
  ) => {
    if (newSaveType !== null) {
      setSaveType(newSaveType)
      setError(null)
    }
  }

  const handleSave = async () => {
    if (!filterName.trim()) {
      setError('필터 이름을 입력해주세요.')
      return
    }

    setIsSaving(true)
    setError(null)
    setSuccess(null)

    try {
      const saveData = {
        name: filterName,
        description,
        filters: filterData.filters,
        appliedFilters: filterData.appliedFilters,
        filteredStocks: filterData.filteredStocks,
        filterStats: filterData.filterStats,
        timestamp: new Date().toISOString()
      }

      if (saveType === 'local') {
        // 로컬 스토리지에 저장
        const existingSaves = localStorage.getItem('savedFilters')
        const saves = existingSaves ? JSON.parse(existingSaves) : []
        
        // 중복 이름 체크
        if (saves.some((s: any) => s.name === filterName)) {
          setError('같은 이름의 필터가 이미 존재합니다.')
          setIsSaving(false)
          return
        }

        saves.push({
          ...saveData,
          id: `local_${Date.now()}`
        })

        localStorage.setItem('savedFilters', JSON.stringify(saves))
        setSuccess('로컬에 저장되었습니다.')
        
        setTimeout(() => {
          onSaveComplete?.('local', filterName)
          handleClose()
        }, 1500)

      } else {
        // Supabase (클라우드)에 저장
        const user = await authService.getCurrentUser()
        
        if (!user) {
          setError('클라우드 저장을 위해서는 로그인이 필요합니다.')
          setIsSaving(false)
          return
        }

        // investment_filters 테이블에 저장
        const { data, error: saveError } = await supabase
          .from('kw_investment_filters')
          .insert({
            user_id: user.id,
            name: filterName,
            description,
            filters: filterData.filters,
            applied_filters: filterData.appliedFilters,
            filter_stats: filterData.filterStats,
            filtered_stocks_count: filterData.filteredStocks.length,
            filtered_stocks: filterData.filteredStocks.slice(0, 100), // 상위 100개만 저장
            is_active: true
          })
          .select()
          .single()

        if (saveError) {
          console.error('Save error:', saveError)
          setError('클라우드 저장 중 오류가 발생했습니다.')
          setIsSaving(false)
          return
        }

        setSuccess('클라우드에 저장되었습니다.')
        
        setTimeout(() => {
          onSaveComplete?.('cloud', filterName)
          handleClose()
        }, 1500)
      }
    } catch (err) {
      console.error('Save error:', err)
      setError('저장 중 오류가 발생했습니다.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleClose = () => {
    setFilterName('')
    setDescription('')
    setError(null)
    setSuccess(null)
    onClose()
  }

  // 필터 요약 정보 생성
  const getFilterSummary = () => {
    const summary = []
    
    if (filterData.appliedFilters?.valuation) {
      summary.push('가치지표')
    }
    if (filterData.appliedFilters?.financial) {
      summary.push('재무지표')
    }
    if (filterData.appliedFilters?.sector) {
      summary.push('섹터')
    }
    
    return summary
  }

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SaveIcon />
        필터 설정 저장
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          {/* 현재 필터 정보 */}
          <Paper sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
            <Typography variant="subtitle2" gutterBottom>
              저장할 필터 정보
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
              {getFilterSummary().map((filter) => (
                <Chip 
                  key={filter}
                  label={filter} 
                  size="small" 
                  color="primary" 
                  variant="outlined"
                />
              ))}
            </Stack>
            <Typography variant="body2" color="text.secondary">
              필터링된 종목: {filterData.filteredStocks?.length || 0}개
            </Typography>
            <Typography variant="body2" color="text.secondary">
              전체 종목 중 {filterData.filterStats?.final || 0}개 선택
            </Typography>
          </Paper>

          {/* 저장 위치 선택 */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              저장 위치
            </Typography>
            <ToggleButtonGroup
              value={saveType}
              exclusive
              onChange={handleSaveTypeChange}
              fullWidth
            >
              <ToggleButton value="local">
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
                  <Computer />
                  <Typography variant="caption">로컬 저장</Typography>
                  <Typography variant="caption" color="text.secondary">
                    브라우저에 저장
                  </Typography>
                </Box>
              </ToggleButton>
              <ToggleButton value="cloud">
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
                  <Cloud />
                  <Typography variant="caption">클라우드 저장</Typography>
                  <Typography variant="caption" color="text.secondary">
                    영구 보관
                  </Typography>
                </Box>
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {/* 저장 정보 입력 */}
          <TextField
            fullWidth
            label="필터 이름"
            placeholder="예: 성장주 필터, 가치주 필터"
            value={filterName}
            onChange={(e) => setFilterName(e.target.value)}
            sx={{ mb: 2 }}
            required
            error={!!error && !filterName}
            helperText={!filterName && error ? '필터 이름은 필수입니다' : ''}
          />

          <TextField
            fullWidth
            label="설명 (선택사항)"
            placeholder="이 필터의 용도나 특징을 입력하세요"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />

          {/* 저장 위치별 안내 */}
          <Alert 
            severity="info" 
            icon={saveType === 'local' ? <Computer /> : <Cloud />}
            sx={{ mb: 2 }}
          >
            {saveType === 'local' ? (
              <>
                <strong>로컬 저장</strong>
                <Typography variant="body2">
                  • 현재 브라우저에만 저장됩니다<br />
                  • 브라우저 데이터 삭제 시 함께 삭제됩니다<br />
                  • 다른 기기에서는 사용할 수 없습니다
                </Typography>
              </>
            ) : (
              <>
                <strong>클라우드 저장</strong>
                <Typography variant="body2">
                  • 계정에 영구 저장됩니다<br />
                  • 모든 기기에서 접근 가능합니다<br />
                  • 로그인이 필요합니다
                </Typography>
              </>
            )}
          </Alert>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={isSaving}>
          취소
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={isSaving || !filterName}
          startIcon={isSaving ? <CircularProgress size={20} /> : 
                    saveType === 'local' ? <Computer /> : <CloudUpload />}
        >
          {isSaving ? '저장 중...' : 
           saveType === 'local' ? '로컬에 저장' : '클라우드에 저장'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default SaveFilterDialog