import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Grid,
  Alert,
  Stack,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  InputAdornment,
  Paper
} from '@mui/material'
import {
  AccountBalance,
  Add,
  Delete,
  Edit,
  Save,
  Cancel,
  CheckCircle,
  Warning,
  Info,
  Science,
  TrendingUp,
  ContentCopy
} from '@mui/icons-material'
import { supabase } from '../../lib/supabase'
import { ApiKeyService } from '../../services/apiKeyService'

interface Account {
  id: string
  provider: string
  account_number: string
  account_name: string
  is_test_mode: boolean
  is_primary: boolean
  created_at: string
}

const AccountConnectEnhanced: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info', text: string } | null>(null)
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [currentUser, setCurrentUser] = useState<any>(null)
  
  // 새 계좌 입력 상태
  const [newAccount, setNewAccount] = useState({
    provider: 'kiwoom',
    account_number: '',
    account_name: '',
    is_test_mode: true,
    account_password: '' // 계좌 비밀번호 (선택)
  })

  useEffect(() => {
    loadUserAndAccounts()
  }, [])

  const loadUserAndAccounts = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (user) {
        setCurrentUser(user)
        await loadAccounts(user.id)
      }
    } catch (error) {
      console.error('Failed to load user:', error)
    }
  }

  const loadAccounts = async (userId: string) => {
    try {
      // account_number 타입의 API 키들을 가져옴
      const { data, error } = await supabase
        .from('user_api_keys')
        .select('*')
        .eq('user_id', userId)
        .eq('key_type', 'account_number')
        .order('created_at', { ascending: false })

      if (error) throw error

      if (data) {
        const accounts: Account[] = data.map(key => ({
          id: key.id,
          provider: key.provider,
          account_number: atob(key.encrypted_value), // Base64 디코딩
          account_name: key.key_name,
          is_test_mode: key.is_test_mode,
          is_primary: false, // 추후 구현
          created_at: key.created_at
        }))
        setAccounts(accounts)
      }
    } catch (error) {
      console.error('Failed to load accounts:', error)
      setMessage({ type: 'error', text: '계좌 정보를 불러오는데 실패했습니다.' })
    }
  }

  const handleAddAccount = async () => {
    if (!newAccount.account_number || !newAccount.account_name) {
      setMessage({ type: 'error', text: '계좌번호와 계좌명을 입력해주세요.' })
      return
    }

    setLoading(true)
    try {
      // 계좌번호 저장
      const accountResult = await ApiKeyService.saveApiKey(currentUser.id, {
        provider: newAccount.provider,
        keyType: 'account_number',
        keyName: newAccount.account_name,
        keyValue: newAccount.account_number,
        isTestMode: newAccount.is_test_mode
      })

      if (!accountResult.success) {
        throw new Error('계좌번호 저장 실패')
      }

      // 계좌 비밀번호 저장 (선택사항)
      if (newAccount.account_password) {
        await ApiKeyService.saveApiKey(currentUser.id, {
          provider: newAccount.provider,
          keyType: 'account_password',
          keyName: newAccount.account_name,
          keyValue: newAccount.account_password,
          isTestMode: newAccount.is_test_mode
        })
      }

      setMessage({ 
        type: 'success', 
        text: `${newAccount.is_test_mode ? '모의투자' : '실전투자'} 계좌가 등록되었습니다.` 
      })
      
      setShowAddDialog(false)
      setNewAccount({
        provider: 'kiwoom',
        account_number: '',
        account_name: '',
        is_test_mode: true,
        account_password: ''
      })
      
      await loadAccounts(currentUser.id)
    } catch (error: any) {
      console.error('Failed to add account:', error)
      setMessage({ type: 'error', text: error.message || '계좌 등록에 실패했습니다.' })
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteAccount = async (accountId: string) => {
    if (!window.confirm('이 계좌를 삭제하시겠습니까?')) return

    try {
      const { error } = await supabase
        .from('user_api_keys')
        .delete()
        .eq('id', accountId)

      if (error) throw error

      setMessage({ type: 'success', text: '계좌가 삭제되었습니다.' })
      await loadAccounts(currentUser.id)
    } catch (error) {
      console.error('Failed to delete account:', error)
      setMessage({ type: 'error', text: '계좌 삭제에 실패했습니다.' })
    }
  }

  const copyAccountNumber = (accountNumber: string) => {
    navigator.clipboard.writeText(accountNumber)
    setMessage({ type: 'info', text: '계좌번호가 복사되었습니다.' })
  }

  // 모의투자/실전투자 계좌 분리
  const testAccounts = accounts.filter(a => a.is_test_mode)
  const liveAccounts = accounts.filter(a => !a.is_test_mode)

  return (
    <Box>
      <Stack spacing={3}>
        {/* 헤더 */}
        <Card>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="h6">
                <AccountBalance sx={{ mr: 1, verticalAlign: 'middle' }} />
                계좌 연동 관리
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setShowAddDialog(true)}
              >
                계좌 추가
              </Button>
            </Stack>
          </CardContent>
        </Card>

        {message && (
          <Alert 
            severity={message.type} 
            onClose={() => setMessage(null)}
          >
            {message.text}
          </Alert>
        )}

        {/* 안내 메시지 */}
        <Alert severity="info" icon={<Info />}>
          <Typography variant="body2">
            키움증권 계좌번호를 등록하면 자동매매 시 해당 계좌로 주문이 실행됩니다.
            모의투자와 실전투자 계좌를 각각 등록할 수 있습니다.
          </Typography>
        </Alert>

        {/* 모의투자 계좌 섹션 */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <Science sx={{ mr: 1 }} />
              모의투자 계좌
              <Chip label={`${testAccounts.length}개`} size="small" sx={{ ml: 1 }} />
            </Typography>

            {testAccounts.length === 0 ? (
              <Alert severity="info">
                등록된 모의투자 계좌가 없습니다. 계좌를 추가해주세요.
              </Alert>
            ) : (
              <List>
                {testAccounts.map((account, index) => (
                  <React.Fragment key={account.id}>
                    <ListItem>
                      <ListItemText
                        primary={
                          <Stack direction="row" spacing={1} alignItems="center">
                            <Typography variant="subtitle1">{account.account_name}</Typography>
                            <Chip label="모의투자" size="small" color="info" />
                          </Stack>
                        }
                        secondary={
                          <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              {account.account_number}
                            </Typography>
                            <IconButton 
                              size="small" 
                              onClick={() => copyAccountNumber(account.account_number)}
                            >
                              <ContentCopy fontSize="small" />
                            </IconButton>
                          </Stack>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          color="error"
                          onClick={() => handleDeleteAccount(account.id)}
                        >
                          <Delete />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < testAccounts.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </CardContent>
        </Card>

        {/* 실전투자 계좌 섹션 */}
        <Card sx={{ borderColor: 'warning.main', borderWidth: 1, borderStyle: 'solid' }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <TrendingUp sx={{ mr: 1 }} />
              실전투자 계좌
              <Chip label={`${liveAccounts.length}개`} size="small" sx={{ ml: 1 }} />
            </Typography>

            {liveAccounts.length === 0 ? (
              <Alert severity="warning">
                등록된 실전투자 계좌가 없습니다. 실전 거래를 위해서는 계좌를 등록해야 합니다.
              </Alert>
            ) : (
              <List>
                {liveAccounts.map((account, index) => (
                  <React.Fragment key={account.id}>
                    <ListItem>
                      <ListItemText
                        primary={
                          <Stack direction="row" spacing={1} alignItems="center">
                            <Typography variant="subtitle1">{account.account_name}</Typography>
                            <Chip label="실전투자" size="small" color="warning" />
                          </Stack>
                        }
                        secondary={
                          <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              {account.account_number}
                            </Typography>
                            <IconButton 
                              size="small" 
                              onClick={() => copyAccountNumber(account.account_number)}
                            >
                              <ContentCopy fontSize="small" />
                            </IconButton>
                          </Stack>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          color="error"
                          onClick={() => handleDeleteAccount(account.id)}
                        >
                          <Delete />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < liveAccounts.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </CardContent>
        </Card>

        {/* 계좌 형식 안내 */}
        <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
          <Typography variant="subtitle2" gutterBottom>
            <Info sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
            계좌번호 입력 형식
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • 키움증권: 8자리-2자리 (예: 12345678-01)<br />
            • 한국투자증권: 8자리-2자리 (예: 87654321-01)<br />
            • 계좌 비밀번호는 자동매매 시 필요할 수 있습니다 (선택사항)
          </Typography>
        </Paper>
      </Stack>

      {/* 계좌 추가 다이얼로그 */}
      <Dialog open={showAddDialog} onClose={() => setShowAddDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>계좌 추가</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={newAccount.is_test_mode}
                  onChange={(e) => setNewAccount({ ...newAccount, is_test_mode: e.target.checked })}
                />
              }
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  {newAccount.is_test_mode ? <Science /> : <TrendingUp />}
                  <Typography>
                    {newAccount.is_test_mode ? '모의투자 계좌' : '실전투자 계좌'}
                  </Typography>
                </Stack>
              }
            />

            <TextField
              fullWidth
              label="계좌명"
              value={newAccount.account_name}
              onChange={(e) => setNewAccount({ ...newAccount, account_name: e.target.value })}
              placeholder="예: 키움 모의투자 계좌"
              required
            />

            <TextField
              fullWidth
              label="계좌번호"
              value={newAccount.account_number}
              onChange={(e) => setNewAccount({ ...newAccount, account_number: e.target.value })}
              placeholder="예: 12345678-01"
              required
              helperText="하이픈(-)을 포함하여 입력하세요"
            />

            <TextField
              fullWidth
              label="계좌 비밀번호 (선택)"
              type="password"
              value={newAccount.account_password}
              onChange={(e) => setNewAccount({ ...newAccount, account_password: e.target.value })}
              helperText="자동매매 시 필요할 수 있습니다"
            />

            {newAccount.is_test_mode ? (
              <Alert severity="info">
                모의투자 계좌는 실제 자금이 거래되지 않습니다.
              </Alert>
            ) : (
              <Alert severity="warning">
                실전투자 계좌는 실제 자금이 거래됩니다. 신중하게 사용하세요.
              </Alert>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAddDialog(false)}>취소</Button>
          <Button 
            variant="contained"
            onClick={handleAddAccount}
            disabled={loading || !newAccount.account_number || !newAccount.account_name}
          >
            추가
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default AccountConnectEnhanced