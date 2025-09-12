import React, { useState, useEffect } from 'react'
import {
  Container,
  Paper,
  Tabs,
  Tab,
  Box,
  Typography,
  Button,
  TextField,
  Grid,
  Alert,
  Card,
  CardContent,
  Stack,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  InputAdornment,
  Tooltip
} from '@mui/material'
import {
  Person,
  Key,
  AccountBalance,
  Settings,
  Security,
  Notifications,
  Visibility,
  VisibilityOff,
  Add,
  Delete,
  Edit,
  Save,
  Cancel,
  CheckCircle,
  Warning,
  ContentCopy,
  VpnKey
} from '@mui/icons-material'
import { useAppSelector } from '../hooks/redux'
import { supabase } from '../lib/supabase'
import AccountConnect from '../components/trading/AccountConnect'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

interface ApiKey {
  id: string
  provider: string
  key_type: string
  key_name: string
  masked_value: string
  is_active: boolean
  is_test_mode: boolean
  last_used_at: string
  created_at: string
}

const MyPage: React.FC = () => {
  const user = useAppSelector(state => state.auth.user)
  const [tabValue, setTabValue] = useState(0)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const [currentAuthUser, setCurrentAuthUser] = useState<any>(null)
  
  // 프로필 상태
  const [profile, setProfile] = useState({
    display_name: '',
    email: '',
    phone_number: '',
    birth_date: '',
    investor_type: 'beginner',
    risk_tolerance: 'moderate',
    preferred_market: 'both'
  })
  
  // API 키 상태
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [showApiKeyDialog, setShowApiKeyDialog] = useState(false)
  const [newApiKey, setNewApiKey] = useState({
    provider: 'kiwoom',
    key_type: 'app_key',
    key_name: '',
    key_value: '',
    is_test_mode: false
  })
  const [showApiKeyValue, setShowApiKeyValue] = useState<{ [key: string]: boolean }>({})
  
  // 보안 설정
  const [securitySettings, setSecuritySettings] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
    two_factor_enabled: false
  })
  
  // 알림 설정
  const [notificationSettings, setNotificationSettings] = useState({
    email_notifications: true,
    sms_notifications: false,
    push_notifications: true
  })
  
  useEffect(() => {
    if (user) {
      loadAuthUser()
      loadProfile()
      loadApiKeys()
      loadSettings()
    }
  }, [user])
  
  const loadAuthUser = async () => {
    const { data: { user: authUser } } = await supabase.auth.getUser()
    if (authUser) {
      setCurrentAuthUser(authUser)
    }
  }
  
  const loadProfile = async () => {
    try {
      const { data, error } = await supabase
        .from('user_profiles_extended')
        .select('*')
        .eq('user_id', user?.id)
        .single()
      
      if (data) {
        setProfile(prev => ({
          ...prev,
          ...data,
          email: currentAuthUser?.email || ''
        }))
      } else if (!error) {
        // If no extended profile exists, use basic info
        setProfile(prev => ({
          ...prev,
          display_name: user?.name || '',
          email: currentAuthUser?.email || ''
        }))
      }
    } catch (error) {
      console.error('Failed to load profile:', error)
    }
  }
  
  const loadApiKeys = async () => {
    try {
      const { data, error } = await supabase
        .from('user_api_keys_view')
        .select('*')
        .eq('user_id', user?.id)
        .order('created_at', { ascending: false })
      
      if (data) {
        setApiKeys(data)
      }
    } catch (error) {
      console.error('Failed to load API keys:', error)
    }
  }
  
  const loadSettings = async () => {
    try {
      const { data } = await supabase
        .from('user_profiles_extended')
        .select('email_notifications, sms_notifications, push_notifications, two_factor_enabled')
        .eq('user_id', user?.id)
        .single()
      
      if (data) {
        setNotificationSettings({
          email_notifications: data.email_notifications,
          sms_notifications: data.sms_notifications,
          push_notifications: data.push_notifications
        })
        setSecuritySettings(prev => ({
          ...prev,
          two_factor_enabled: data.two_factor_enabled
        }))
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }
  
  const handleProfileUpdate = async () => {
    setLoading(true)
    try {
      const { error } = await supabase
        .from('user_profiles_extended')
        .upsert({
          user_id: user?.id,
          display_name: profile.display_name,
          phone_number: profile.phone_number,
          birth_date: profile.birth_date,
          investor_type: profile.investor_type,
          risk_tolerance: profile.risk_tolerance,
          preferred_market: profile.preferred_market
        }, {
          onConflict: 'user_id'
        })
      
      if (error) throw error
      
      setMessage({ type: 'success', text: '프로필이 업데이트되었습니다.' })
    } catch (error) {
      setMessage({ type: 'error', text: '프로필 업데이트 실패' })
    } finally {
      setLoading(false)
    }
  }
  
  const handleAddApiKey = async () => {
    setLoading(true)
    try {
      const { data, error } = await supabase.rpc('save_user_api_key', {
        p_user_id: user?.id,
        p_provider: newApiKey.provider,
        p_key_type: newApiKey.key_type,
        p_key_name: newApiKey.key_name || `${newApiKey.provider}_${newApiKey.key_type}`,
        p_key_value: newApiKey.key_value,
        p_is_test_mode: newApiKey.is_test_mode
      })
      
      if (error) throw error
      
      await loadApiKeys()
      setShowApiKeyDialog(false)
      setNewApiKey({
        provider: 'kiwoom',
        key_type: 'app_key',
        key_name: '',
        key_value: '',
        is_test_mode: false
      })
      setMessage({ type: 'success', text: 'API 키가 안전하게 저장되었습니다.' })
    } catch (error) {
      setMessage({ type: 'error', text: 'API 키 저장 실패' })
    } finally {
      setLoading(false)
    }
  }
  
  const handleDeleteApiKey = async (keyId: string) => {
    if (!window.confirm('이 API 키를 삭제하시겠습니까?')) return
    
    try {
      const { error } = await supabase.rpc('delete_user_api_key', {
        p_user_id: user?.id,
        p_key_id: keyId
      })
      
      if (error) throw error
      
      await loadApiKeys()
      setMessage({ type: 'success', text: 'API 키가 삭제되었습니다.' })
    } catch (error) {
      setMessage({ type: 'error', text: 'API 키 삭제 실패' })
    }
  }
  
  const handlePasswordChange = async () => {
    if (securitySettings.new_password !== securitySettings.confirm_password) {
      setMessage({ type: 'error', text: '새 비밀번호가 일치하지 않습니다.' })
      return
    }
    
    setLoading(true)
    try {
      const { error } = await supabase.auth.updateUser({
        password: securitySettings.new_password
      })
      
      if (error) throw error
      
      setSecuritySettings({
        current_password: '',
        new_password: '',
        confirm_password: '',
        two_factor_enabled: securitySettings.two_factor_enabled
      })
      setMessage({ type: 'success', text: '비밀번호가 변경되었습니다.' })
    } catch (error) {
      setMessage({ type: 'error', text: '비밀번호 변경 실패' })
    } finally {
      setLoading(false)
    }
  }
  
  const handleNotificationUpdate = async () => {
    setLoading(true)
    try {
      const { error } = await supabase
        .from('user_profiles_extended')
        .upsert({
          user_id: user?.id,
          ...notificationSettings
        }, {
          onConflict: 'user_id'
        })
      
      if (error) throw error
      
      setMessage({ type: 'success', text: '알림 설정이 저장되었습니다.' })
    } catch (error) {
      setMessage({ type: 'error', text: '알림 설정 저장 실패' })
    } finally {
      setLoading(false)
    }
  }
  
  const getProviderName = (provider: string) => {
    const providers: { [key: string]: string } = {
      kiwoom: '키움증권',
      korea_investment: '한국투자증권',
      ebest: 'eBEST투자증권',
      nh: 'NH투자증권'
    }
    return providers[provider] || provider
  }
  
  const getKeyTypeName = (keyType: string) => {
    const types: { [key: string]: string } = {
      app_key: 'App Key',
      app_secret: 'App Secret',
      account_number: '계좌번호',
      cert_password: '인증서 비밀번호',
      api_password: 'API 비밀번호'
    }
    return types[keyType] || keyType
  }
  
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          <Person sx={{ mr: 1, verticalAlign: 'middle' }} />
          내 페이지
        </Typography>
        
        {message && (
          <Alert 
            severity={message.type} 
            onClose={() => setMessage(null)}
            sx={{ mb: 2 }}
          >
            {message.text}
          </Alert>
        )}
        
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="프로필" icon={<Person />} iconPosition="start" />
          <Tab label="API 키 관리" icon={<Key />} iconPosition="start" />
          <Tab label="계좌 연동" icon={<AccountBalance />} iconPosition="start" />
          <Tab label="보안 설정" icon={<Security />} iconPosition="start" />
          <Tab label="알림 설정" icon={<Notifications />} iconPosition="start" />
        </Tabs>
        
        {/* 프로필 탭 */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="이름"
                value={profile.display_name}
                onChange={(e) => setProfile({ ...profile, display_name: e.target.value })}
                margin="normal"
              />
              <TextField
                fullWidth
                label="이메일"
                value={profile.email}
                disabled
                margin="normal"
              />
              <TextField
                fullWidth
                label="전화번호"
                value={profile.phone_number}
                onChange={(e) => setProfile({ ...profile, phone_number: e.target.value })}
                margin="normal"
              />
              <TextField
                fullWidth
                label="생년월일"
                type="date"
                value={profile.birth_date}
                onChange={(e) => setProfile({ ...profile, birth_date: e.target.value })}
                margin="normal"
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>투자자 유형</InputLabel>
                <Select
                  value={profile.investor_type}
                  onChange={(e) => setProfile({ ...profile, investor_type: e.target.value })}
                  label="투자자 유형"
                >
                  <MenuItem value="beginner">초보자</MenuItem>
                  <MenuItem value="intermediate">중급자</MenuItem>
                  <MenuItem value="advanced">고급자</MenuItem>
                  <MenuItem value="professional">전문가</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl fullWidth margin="normal">
                <InputLabel>위험 성향</InputLabel>
                <Select
                  value={profile.risk_tolerance}
                  onChange={(e) => setProfile({ ...profile, risk_tolerance: e.target.value })}
                  label="위험 성향"
                >
                  <MenuItem value="conservative">안정형</MenuItem>
                  <MenuItem value="moderate">중립형</MenuItem>
                  <MenuItem value="aggressive">공격형</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl fullWidth margin="normal">
                <InputLabel>선호 시장</InputLabel>
                <Select
                  value={profile.preferred_market}
                  onChange={(e) => setProfile({ ...profile, preferred_market: e.target.value })}
                  label="선호 시장"
                >
                  <MenuItem value="kospi">KOSPI</MenuItem>
                  <MenuItem value="kosdaq">KOSDAQ</MenuItem>
                  <MenuItem value="both">모두</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={handleProfileUpdate}
                disabled={loading}
                startIcon={<Save />}
              >
                프로필 저장
              </Button>
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* API 키 관리 탭 */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 3 }}>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setShowApiKeyDialog(true)}
            >
              API 키 추가
            </Button>
          </Box>
          
          <Grid container spacing={2}>
            {apiKeys.map((apiKey) => (
              <Grid item xs={12} md={6} key={apiKey.id}>
                <Card>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Box>
                        <Typography variant="h6">
                          {getProviderName(apiKey.provider)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {getKeyTypeName(apiKey.key_type)}
                        </Typography>
                        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                          {apiKey.is_test_mode && (
                            <Chip label="테스트" size="small" color="info" />
                          )}
                          {apiKey.is_active ? (
                            <Chip label="활성" size="small" color="success" />
                          ) : (
                            <Chip label="비활성" size="small" color="default" />
                          )}
                        </Stack>
                        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                          키 이름: {apiKey.key_name}
                        </Typography>
                        <Typography variant="caption" display="block">
                          마지막 사용: {apiKey.last_used_at ? new Date(apiKey.last_used_at).toLocaleDateString() : '사용 안함'}
                        </Typography>
                      </Box>
                      <IconButton
                        color="error"
                        onClick={() => handleDeleteApiKey(apiKey.id)}
                      >
                        <Delete />
                      </IconButton>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          {/* API 키 추가 다이얼로그 */}
          <Dialog open={showApiKeyDialog} onClose={() => setShowApiKeyDialog(false)} maxWidth="sm" fullWidth>
            <DialogTitle>API 키 추가</DialogTitle>
            <DialogContent>
              <FormControl fullWidth margin="normal">
                <InputLabel>증권사</InputLabel>
                <Select
                  value={newApiKey.provider}
                  onChange={(e) => setNewApiKey({ ...newApiKey, provider: e.target.value })}
                  label="증권사"
                >
                  <MenuItem value="kiwoom">키움증권</MenuItem>
                  <MenuItem value="korea_investment">한국투자증권</MenuItem>
                  <MenuItem value="ebest">eBEST투자증권</MenuItem>
                  <MenuItem value="nh">NH투자증권</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl fullWidth margin="normal">
                <InputLabel>키 유형</InputLabel>
                <Select
                  value={newApiKey.key_type}
                  onChange={(e) => setNewApiKey({ ...newApiKey, key_type: e.target.value })}
                  label="키 유형"
                >
                  <MenuItem value="app_key">App Key</MenuItem>
                  <MenuItem value="app_secret">App Secret</MenuItem>
                  <MenuItem value="account_number">계좌번호</MenuItem>
                  <MenuItem value="cert_password">인증서 비밀번호</MenuItem>
                </Select>
              </FormControl>
              
              <TextField
                fullWidth
                label="키 이름 (선택사항)"
                value={newApiKey.key_name}
                onChange={(e) => setNewApiKey({ ...newApiKey, key_name: e.target.value })}
                margin="normal"
                helperText="예: 모의투자용, 실전투자용"
              />
              
              <TextField
                fullWidth
                label="키 값"
                type={showApiKeyValue[newApiKey.key_type] ? 'text' : 'password'}
                value={newApiKey.key_value}
                onChange={(e) => setNewApiKey({ ...newApiKey, key_value: e.target.value })}
                margin="normal"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowApiKeyValue({
                          ...showApiKeyValue,
                          [newApiKey.key_type]: !showApiKeyValue[newApiKey.key_type]
                        })}
                      >
                        {showApiKeyValue[newApiKey.key_type] ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={newApiKey.is_test_mode}
                    onChange={(e) => setNewApiKey({ ...newApiKey, is_test_mode: e.target.checked })}
                  />
                }
                label="테스트 모드 (모의투자)"
                sx={{ mt: 2 }}
              />
              
              <Alert severity="info" sx={{ mt: 2 }}>
                API 키는 Supabase Vault를 통해 안전하게 암호화되어 저장됩니다.
              </Alert>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setShowApiKeyDialog(false)}>취소</Button>
              <Button 
                onClick={handleAddApiKey} 
                variant="contained"
                disabled={loading || !newApiKey.key_value}
              >
                저장
              </Button>
            </DialogActions>
          </Dialog>
        </TabPanel>
        
        {/* 계좌 연동 탭 */}
        <TabPanel value={tabValue} index={2}>
          <AccountConnect />
        </TabPanel>
        
        {/* 보안 설정 탭 */}
        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                비밀번호 변경
              </Typography>
              
              <TextField
                fullWidth
                type="password"
                label="새 비밀번호"
                value={securitySettings.new_password}
                onChange={(e) => setSecuritySettings({
                  ...securitySettings,
                  new_password: e.target.value
                })}
                margin="normal"
              />
              
              <TextField
                fullWidth
                type="password"
                label="새 비밀번호 확인"
                value={securitySettings.confirm_password}
                onChange={(e) => setSecuritySettings({
                  ...securitySettings,
                  confirm_password: e.target.value
                })}
                margin="normal"
              />
              
              <Button
                variant="contained"
                onClick={handlePasswordChange}
                disabled={loading || !securitySettings.new_password}
                sx={{ mt: 2 }}
                startIcon={<VpnKey />}
              >
                비밀번호 변경
              </Button>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                2단계 인증
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={securitySettings.two_factor_enabled}
                    onChange={(e) => setSecuritySettings({
                      ...securitySettings,
                      two_factor_enabled: e.target.checked
                    })}
                  />
                }
                label="2단계 인증 사용"
              />
              
              <Alert severity="warning" sx={{ mt: 2 }}>
                2단계 인증을 활성화하면 로그인 시 추가 인증이 필요합니다.
              </Alert>
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* 알림 설정 탭 */}
        <TabPanel value={tabValue} index={4}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                알림 수신 설정
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.email_notifications}
                    onChange={(e) => setNotificationSettings({
                      ...notificationSettings,
                      email_notifications: e.target.checked
                    })}
                  />
                }
                label="이메일 알림"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.sms_notifications}
                    onChange={(e) => setNotificationSettings({
                      ...notificationSettings,
                      sms_notifications: e.target.checked
                    })}
                  />
                }
                label="SMS 알림"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.push_notifications}
                    onChange={(e) => setNotificationSettings({
                      ...notificationSettings,
                      push_notifications: e.target.checked
                    })}
                  />
                }
                label="푸시 알림"
              />
              
              <Box sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  onClick={handleNotificationUpdate}
                  disabled={loading}
                  startIcon={<Save />}
                >
                  알림 설정 저장
                </Button>
              </Box>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>
    </Container>
  )
}

export default MyPage