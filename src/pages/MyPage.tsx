import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
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
  Tooltip,
  ToggleButton,
  ToggleButtonGroup,
  Badge
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
  VpnKey,
  Science,
  TrendingUp,
  SwapHoriz,
  Info,
  ArrowBack
} from '@mui/icons-material'
import { useAppSelector } from '../hooks/redux'
import { supabase } from '../lib/supabase'
import AccountConnectEnhanced from '../components/trading/AccountConnectEnhanced'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  // Use display: none instead of unmounting to keep state/data preserved
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
      style={{ display: value === index ? 'block' : 'none' }}
    >
      <Box sx={{ p: 3 }}>
        {children}
      </Box>
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

const MyPageEnhanced: React.FC = () => {
  const navigate = useNavigate()
  const user = useAppSelector(state => state.auth.user)
  const [tabValue, setTabValue] = useState(0)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const [currentAuthUser, setCurrentAuthUser] = useState<any>(null)

  // 거래 모드 상태
  const [tradingMode, setTradingMode] = useState<'test' | 'live'>('test')
  const [modeInfo, setModeInfo] = useState<any>(null)
  const [showQuickSetup, setShowQuickSetup] = useState(false)

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

  // 빠른 설정 상태 (키움 전용)
  const [quickSetup, setQuickSetup] = useState({
    app_key: '',
    app_secret: '',
    account_number: '',
    cert_password: '',
    is_test_mode: true
  })

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
    // 초기 로드
    const loadAllData = async () => {
      await loadAuthUser()
      await loadProfile()
      await loadApiKeys()
      await loadSettings()
      await loadTradingMode()
    }

    loadAllData()
  }, []) // 컴포넌트 마운트 시 한 번만

  // 탭 변경 시 API 키 재로드
  useEffect(() => {
    if (tabValue === 1) { // API 키 관리 탭
      console.log('API keys tab selected, reloading...');
      loadApiKeys()
    }
  }, [tabValue])

  const loadAuthUser = async () => {
    const { data: { user: authUser } } = await supabase.auth.getUser()
    if (authUser) {
      setCurrentAuthUser(authUser)
    }
  }

  const loadProfile = async () => {
    try {
      console.log('Loading profile...');

      // Ensure we have the auth user
      let authUser = currentAuthUser;
      if (!authUser) {
        const { data } = await supabase.auth.getUser();
        authUser = data.user;
      }

      if (!authUser) {
        console.error('No auth user found');
        return;
      }

      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', authUser.id)
        .maybeSingle()

      console.log('Profile data loaded for user:', authUser.id, data);

      if (data) {
        setProfile(prev => ({
          ...prev,
          ...data,
          // Handle schema migration discrepancies
          display_name: data.display_name || data.name || '',
          name: data.name || '',
          // Ensure email is always from auth if not in profile
          email: authUser.email || prev.email,
          // Ensure other fields don't break if null
          phone_number: data.phone_number || prev.phone_number || '',
          investor_type: data.investor_type || prev.investor_type || '',
          risk_tolerance: data.risk_tolerance || prev.risk_tolerance || '',
          preferred_market: data.preferred_market || prev.preferred_market || ''
        }))
      } else if (!error) {
        // Profile might not exist yet, pre-fill from Auth
        console.log('Profile not found, using auth data');
        setProfile(prev => ({
          ...prev,
          display_name: authUser.user_metadata?.name || '',
          name: authUser.user_metadata?.name || '',
          email: authUser.email || ''
        }))
      } else {
        console.error('Error loading profile:', error);
      }
    } catch (error) {
      console.error('Failed to load profile:', error)
    }
  }

  const loadApiKeys = async () => {
    try {
      // Get current auth user if user.id is not available
      let userId = user?.id;
      if (!userId) {
        const { data: { user: authUser } } = await supabase.auth.getUser();
        userId = authUser?.id;
      }

      if (!userId) {
        console.error('No user ID available');
        return;
      }

      // Try view first, fallback to direct table
      let { data, error } = await supabase
        .from('user_api_keys_view')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })

      // If view fails, try direct table access
      if (error || !data) {
        console.log('View failed, trying direct table access');
        const directResult = await supabase
          .from('user_api_keys')
          .select('*')
          .eq('user_id', userId)
          .order('created_at', { ascending: false })

        if (directResult.data) {
          // Transform data to match view structure
          data = directResult.data.map(key => ({
            ...key,
            masked_value: '••••••••'
          }))
        }
      }

      if (data) {
        console.log('Loaded API keys:', data);
        console.log('Test keys:', data.filter(k => k.is_test_mode));
        console.log('Live keys:', data.filter(k => !k.is_test_mode));
        setApiKeys(data)
      } else {
        console.log('No API keys found');
        setApiKeys([])
      }
    } catch (error) {
      console.error('Failed to load API keys:', error)
    }
  }

  const loadSettings = async () => {
    try {
      let userId = user?.id;
      if (!userId) {
        const { data: { user: authUser } } = await supabase.auth.getUser();
        userId = authUser?.id;
      }

      if (!userId) return;

      const { data } = await supabase
        .from('profiles')
        .select('email_notifications, sms_notifications, push_notifications, two_factor_enabled, current_trading_mode')
        .eq('id', userId)
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
        setTradingMode(data.current_trading_mode || 'test')
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }

  const loadTradingMode = async () => {
    try {
      // Get current auth user if user.id is not available
      let userId = user?.id;
      if (!userId) {
        const { data: { user: authUser } } = await supabase.auth.getUser();
        userId = authUser?.id;
      }

      if (!userId) {
        console.error('No user ID available');
        return;
      }

      const { data, error } = await supabase.rpc('get_current_mode_info', {
        p_user_id: userId
      })

      if (data) {
        setModeInfo(data)
        setTradingMode(data.current_mode || 'test')
      }
    } catch (error) {
      console.error('Failed to load trading mode:', error)
    }
  }

  const handleSwitchMode = async (event: React.MouseEvent<HTMLElement>, newMode: 'test' | 'live' | null) => {
    if (newMode === null) return

    try {
      // 1. Get User ID safely
      let userId = user?.id
      if (!userId) {
        const { data: { user: authUser } } = await supabase.auth.getUser()
        userId = authUser?.id
      }
      if (!userId) throw new Error('사용자 정보를 찾을 수 없습니다.')

      const { data, error } = await supabase.rpc('switch_trading_mode', {
        p_user_id: userId,
        p_new_mode: newMode
      })

      if (error) throw error

      setTradingMode(newMode)
      await loadTradingMode()
      await loadApiKeys()
      setMessage({
        type: 'success',
        text: `${newMode === 'test' ? '모의투자' : '실전투자'} 모드로 전환되었습니다.`
      })
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.message || '모드 전환 실패'
      })
    }
  }

  const handleQuickSetup = async () => {
    setLoading(true)
    try {
      // Import the ApiKeyService
      const { ApiKeyService } = await import('../services/apiKeyService')

      // Get current auth user if user.id is not available
      let userId = user?.id;
      if (!userId) {
        const { data: { user: authUser } } = await supabase.auth.getUser();
        userId = authUser?.id;
      }

      if (!userId) {
        throw new Error('사용자 ID를 찾을 수 없습니다. 다시 로그인해주세요.');
      }

      const keyName = quickSetup.is_test_mode ? '모의투자' : '실전투자'

      // Save App Key
      const appKeyResult = await ApiKeyService.saveApiKey(userId, {
        provider: 'kiwoom',
        keyType: 'app_key',
        keyName: keyName,
        keyValue: quickSetup.app_key,
        isTestMode: quickSetup.is_test_mode
      })

      if (!appKeyResult.success) {
        throw new Error('App Key 저장 실패')
      }

      // Save App Secret
      const appSecretResult = await ApiKeyService.saveApiKey(userId, {
        provider: 'kiwoom',
        keyType: 'app_secret',
        keyName: keyName,
        keyValue: quickSetup.app_secret,
        isTestMode: quickSetup.is_test_mode
      })

      if (!appSecretResult.success) {
        throw new Error('App Secret 저장 실패')
      }

      // Save Account Number if provided
      if (quickSetup.account_number) {
        await ApiKeyService.saveApiKey(userId, {
          provider: 'kiwoom',
          keyType: 'account_number',
          keyName: keyName,
          keyValue: quickSetup.account_number,
          isTestMode: quickSetup.is_test_mode
        })
      }

      // Save Cert Password if provided
      if (quickSetup.cert_password) {
        await ApiKeyService.saveApiKey(userId, {
          provider: 'kiwoom',
          keyType: 'cert_password',
          keyName: keyName,
          keyValue: quickSetup.cert_password,
          isTestMode: quickSetup.is_test_mode
        })
      }

      await loadApiKeys()
      await loadTradingMode()
      setShowQuickSetup(false)
      setQuickSetup({
        app_key: '',
        app_secret: '',
        account_number: '',
        cert_password: '',
        is_test_mode: true
      })

      // Show which method was used
      const methodText = appKeyResult.method === 'direct_insert' ? ' (직접 저장)' : ''
      setMessage({
        type: 'success',
        text: `키움 ${quickSetup.is_test_mode ? '모의투자' : '실전투자'} 키가 저장되었습니다${methodText}`
      })
    } catch (error: any) {
      console.error('Quick setup error:', error)
      setMessage({ type: 'error', text: error.message || '키 저장 실패' })
    } finally {
      setLoading(false)
    }
  }

  const handleProfileUpdate = async () => {
    setLoading(true)
    try {
      // Ensure we have a valid user ID
      let targetUserId = user?.id
      if (!targetUserId) {
        const { data: { user: authUser } } = await supabase.auth.getUser()
        targetUserId = authUser?.id
      }

      if (!targetUserId) {
        throw new Error('사용자 정보를 찾을 수 없습니다. 다시 로그인해주세요.')
      }

      const { error } = await supabase
        .from('profiles')
        .update({
          display_name: profile.display_name,
          phone_number: profile.phone_number,
          birth_date: profile.birth_date,
          investor_type: profile.investor_type,
          risk_tolerance: profile.risk_tolerance,
          preferred_market: profile.preferred_market
        })
        .eq('id', targetUserId)

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
      // Import and use the ApiKeyService with fallback strategies
      const { ApiKeyService } = await import('../services/apiKeyService')

      // Get current auth user if user.id is not available
      let userId = user?.id;
      if (!userId) {
        const { data: { user: authUser } } = await supabase.auth.getUser();
        userId = authUser?.id;
      }

      if (!userId) {
        throw new Error('사용자 ID를 찾을 수 없습니다. 다시 로그인해주세요.');
      }

      const result = await ApiKeyService.saveApiKey(userId, {
        provider: newApiKey.provider,
        keyType: newApiKey.key_type,
        keyName: newApiKey.key_name || `${newApiKey.provider}_${newApiKey.key_type}`,
        keyValue: newApiKey.key_value,
        isTestMode: newApiKey.is_test_mode
      })

      if (!result.success) {
        throw new Error(('error' in result ? result.error : 'API 키 저장 실패') as string)
      }

      await loadApiKeys()
      await loadTradingMode()
      setShowApiKeyDialog(false)
      setNewApiKey({
        provider: 'kiwoom',
        key_type: 'app_key',
        key_name: '',
        key_value: '',
        is_test_mode: false
      })

      // Show which method was used for transparency
      const methodText = result.method === 'direct_insert'
        ? ' (직접 저장)'
        : result.method === 'rpc_standard'
          ? ' (RPC 표준)'
          : ''
      setMessage({ type: 'success', text: `API 키가 안전하게 저장되었습니다${methodText}` })
    } catch (error: any) {
      console.error('API key save error:', error)
      setMessage({ type: 'error', text: error.message || 'API 키 저장 실패' })
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
      await loadTradingMode()
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
        .from('profiles')
        .update({
          ...notificationSettings
        })
        .eq('id', user?.id)

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

  // 모의/실전 키 분리 필터링 (계좌번호/비밀번호 제외)
  const isApiKey = (k: ApiKey) => k.key_type !== 'account_number' && k.key_type !== 'account_password'
  const testKeys = apiKeys.filter(k => k.is_test_mode && isApiKey(k))
  const liveKeys = apiKeys.filter(k => !k.is_test_mode && isApiKey(k))

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Stack direction="row" alignItems="center">
            <Button
              variant="outlined"
              startIcon={<ArrowBack />}
              onClick={() => navigate('/')}
              sx={{ mr: 2 }}
            >
              메인으로 돌아가기
            </Button>
            <Typography variant="h4">
              <Person sx={{ mr: 1, verticalAlign: 'middle' }} />
              내 페이지
            </Typography>
          </Stack>

          {/* 거래 모드 표시 (변경 불가) */}
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              현재 거래 모드
            </Typography>
            <Stack direction="row" alignItems="center" spacing={1}>
              <Chip
                icon={tradingMode === 'live' ? <TrendingUp /> : <Science />}
                label={tradingMode === 'live' ? '실전투자' : '모의투자'}
                color={tradingMode === 'live' ? 'warning' : 'primary'}
                variant="outlined"
              />
              <Typography variant="caption" color="text.secondary">
                (변경 시 재로그인 필요)
              </Typography>
            </Stack>
          </Box>
        </Stack>

        {message && (
          <Alert
            severity={message.type}
            onClose={() => setMessage(null)}
            sx={{ mb: 2 }}
          >
            {message.text}
          </Alert>
        )}

        {/* 모드 상태 정보 */}
        {modeInfo && (
          <Alert
            severity={tradingMode === 'live' ? 'warning' : 'info'}
            sx={{ mb: 2 }}
            icon={tradingMode === 'live' ? <TrendingUp /> : <Science />}
          >
            <Stack spacing={1}>
              <Typography variant="body2">
                <strong>{tradingMode === 'test' ? '모의투자' : '실전투자'} 모드</strong>로 운영 중입니다.
              </Typography>
              <Stack direction="row" spacing={2}>
                <Chip
                  label={`모의 키: ${modeInfo.test_ready ? '준비됨' : '미설정'}`}
                  size="small"
                  color={modeInfo.test_ready ? 'success' : 'default'}
                />
                <Chip
                  label={`실전 키: ${modeInfo.live_ready ? '준비됨' : '미설정'}`}
                  size="small"
                  color={modeInfo.live_ready ? 'success' : 'default'}
                />
              </Stack>
            </Stack>
          </Alert>
        )}

        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="프로필" icon={<Person />} iconPosition="start" />
          <Tab
            label={
              <Badge badgeContent={apiKeys.length} color="primary">
                API 키 관리
              </Badge>
            }
            icon={<Key />}
            iconPosition="start"
          />
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
            <Stack direction="row" spacing={2}>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setShowQuickSetup(true)}
              >
                API 키 추가
              </Button>
              <Button
                variant="outlined"
                onClick={() => {
                  console.log('Manual refresh triggered');
                  loadApiKeys();
                  loadTradingMode();
                }}
              >
                새로고침
              </Button>
            </Stack>
          </Box>

          {/* 디버그 정보 */}
          <Alert severity="info" sx={{ mb: 2 }}>
            총 {apiKeys.length}개의 API 키가 로드되었습니다.
            (모의: {apiKeys.filter(k => k.is_test_mode).length}개,
            실전: {apiKeys.filter(k => !k.is_test_mode).length}개)
          </Alert>

          {/* 모의투자 키 섹션 */}
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <Science sx={{ mr: 1 }} />
            모의투자 API 키
            <Chip label={`${testKeys.length}개`} size="small" sx={{ ml: 1 }} />
          </Typography>

          <Grid container spacing={2} sx={{ mb: 4 }}>
            {testKeys.length === 0 ? (
              <Grid item xs={12}>
                <Alert severity="info">
                  모의투자용 API 키가 없습니다. 키움 빠른 설정을 통해 추가하세요.
                </Alert>
              </Grid>
            ) : (
              testKeys.map((apiKey) => (
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
                            <Chip label="모의투자" size="small" color="info" />
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
              ))
            )}
          </Grid>

          <Divider sx={{ mb: 3 }} />

          {/* 실전투자 키 섹션 */}
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <TrendingUp sx={{ mr: 1 }} />
            실전투자 API 키
            <Chip label={`${liveKeys.length}개`} size="small" sx={{ ml: 1 }} />
          </Typography>

          <Grid container spacing={2}>
            {liveKeys.length === 0 ? (
              <Grid item xs={12}>
                <Alert severity="warning">
                  실전투자용 API 키가 없습니다. 실전 거래를 위해서는 반드시 실전 API 키를 등록해야 합니다.
                </Alert>
              </Grid>
            ) : (
              liveKeys.map((apiKey) => (
                <Grid item xs={12} md={6} key={apiKey.id}>
                  <Card sx={{ borderColor: 'warning.main', borderWidth: 1, borderStyle: 'solid' }}>
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
                            <Chip label="실전투자" size="small" color="warning" />
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
              ))
            )}
          </Grid>

          {/* API 키 추가 다이얼로그 (통합) */}
          <Dialog open={showQuickSetup} onClose={() => setShowQuickSetup(false)} maxWidth="sm" fullWidth>
            <DialogTitle>
              API 키 추가
            </DialogTitle>
            <DialogContent>
              <Alert severity="info" sx={{ mb: 2 }}>
                App Key와 App Secret을 한 번에 등록합니다.
              </Alert>

              <FormControlLabel
                control={
                  <Switch
                    checked={quickSetup.is_test_mode}
                    onChange={(e) => setQuickSetup({ ...quickSetup, is_test_mode: e.target.checked })}
                  />
                }
                label={quickSetup.is_test_mode ? "모의투자 모드" : "실전투자 모드"}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                label="App Key"
                value={quickSetup.app_key}
                onChange={(e) => setQuickSetup({ ...quickSetup, app_key: e.target.value })}
                margin="normal"
                required
              />

              <TextField
                fullWidth
                label="App Secret"
                type="password"
                value={quickSetup.app_secret}
                onChange={(e) => setQuickSetup({ ...quickSetup, app_secret: e.target.value })}
                margin="normal"
                required
              />



              <TextField
                fullWidth
                label="인증서 비밀번호 (선택)"
                type="password"
                value={quickSetup.cert_password}
                onChange={(e) => setQuickSetup({ ...quickSetup, cert_password: e.target.value })}
                margin="normal"
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setShowQuickSetup(false)}>취소</Button>
              <Button
                onClick={handleQuickSetup}
                variant="contained"
                disabled={loading || !quickSetup.app_key || !quickSetup.app_secret}
              >
                저장
              </Button>
            </DialogActions>
          </Dialog>


        </TabPanel>

        {/* 계좌 연동 탭 */}
        <TabPanel value={tabValue} index={2}>
          <AccountConnectEnhanced />
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

export default MyPageEnhanced