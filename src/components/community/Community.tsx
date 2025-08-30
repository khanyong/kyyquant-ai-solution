import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  Stack,
  Chip,
  Alert,
  CircularProgress
} from '@mui/material'
import {
  Announcement,
  Forum,
  QuestionAnswer,
  TrendingUp,
  Analytics,
  Assessment,
  AdminPanelSettings
} from '@mui/icons-material'
import BoardList from './BoardList'
import PostDetail from './PostDetail'
import PostEditor from './PostEditor'
import { boardService, Board, Post } from '../../services/boardService'
import { useAppSelector } from '../../hooks/redux'

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
      {value === index && (
        <Box sx={{ pt: 2 }}>
          {children}
        </Box>
      )}
    </div>
  )
}

const Community: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0)
  const [boards, setBoards] = useState<Board[]>([])
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState<'list' | 'detail' | 'edit'>('list')
  const [selectedPost, setSelectedPost] = useState<Post | null>(null)
  const [editingPost, setEditingPost] = useState<Post | null>(null)
  
  const currentUser = useAppSelector(state => state.auth.user)
  const userRole = useAppSelector(state => state.auth.user?.role)

  // 게시판 코드와 탭 인덱스 매핑
  const boardTabs = [
    { code: 'notice', name: '공지사항', icon: <Announcement />, color: 'error' },
    { code: 'free', name: '자유게시판', icon: <Forum />, color: 'primary' },
    { code: 'qna', name: 'Q&A', icon: <QuestionAnswer />, color: 'info' },
    { code: 'strategy_share', name: '전략 공유', icon: <TrendingUp />, color: 'success' },
    { code: 'market_analysis', name: '시장 분석', icon: <Analytics />, color: 'warning' },
    { code: 'backtesting', name: '백테스트 결과', icon: <Assessment />, color: 'secondary' }
  ]

  // 관리자 전용 탭 추가
  if (userRole === 'admin') {
    boardTabs.push({ 
      code: 'admin', 
      name: '관리자', 
      icon: <AdminPanelSettings />, 
      color: 'error' 
    })
  }

  // 프리미엄 사용자 전용 탭 추가
  if (userRole === 'premium' || userRole === 'vip' || userRole === 'admin') {
    const premiumIndex = boardTabs.findIndex(tab => tab.code === 'strategy_share')
    if (premiumIndex !== -1) {
      boardTabs.splice(premiumIndex + 1, 0, {
        code: 'premium_strategy',
        name: '프리미엄 전략',
        icon: <TrendingUp />,
        color: 'secondary'
      })
    }
  }

  useEffect(() => {
    loadBoards()
  }, [])

  const loadBoards = async () => {
    try {
      setLoading(true)
      const data = await boardService.getBoards()
      setBoards(data)
    } catch (error) {
      console.error('Failed to load boards:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
    setView('list')
    setSelectedPost(null)
    setEditingPost(null)
  }

  const handlePostClick = (post: Post) => {
    setSelectedPost(post)
    setView('detail')
  }

  const handleWriteClick = () => {
    setEditingPost(null)
    setView('edit')
  }

  const handleEditClick = (post: Post) => {
    setEditingPost(post)
    setView('edit')
  }

  const handleSave = () => {
    setView('list')
    setEditingPost(null)
    // 목록 새로고침은 BoardList 컴포넌트가 자동으로 처리
  }

  const handleCancel = () => {
    setView('list')
    setEditingPost(null)
  }

  const handleBack = () => {
    setView('list')
    setSelectedPost(null)
  }

  const currentBoardCode = boardTabs[currentTab]?.code

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      {/* 커뮤니티 헤더 */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h5">커뮤니티</Typography>
          <Stack direction="row" spacing={1}>
            {currentUser && (
              <Chip 
                label={currentUser.name} 
                size="small" 
                color="primary"
                variant="outlined"
              />
            )}
            {userRole && userRole !== 'user' && (
              <Chip 
                label={userRole.toUpperCase()} 
                size="small" 
                color={userRole === 'admin' ? 'error' : 'secondary'}
              />
            )}
          </Stack>
        </Stack>
      </Paper>

      {/* 게시판 탭 */}
      <Paper sx={{ mb: 2 }}>
        <Tabs 
          value={currentTab} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              minHeight: 64,
              textTransform: 'none',
              fontSize: '0.95rem'
            }
          }}
        >
          {boardTabs.map((tab, index) => (
            <Tab 
              key={tab.code}
              icon={tab.icon}
              label={tab.name}
              sx={{
                '&.Mui-selected': {
                  color: `${tab.color}.main`
                }
              }}
            />
          ))}
        </Tabs>
      </Paper>

      {/* 탭 컨텐츠 */}
      {boardTabs.map((tab, index) => (
        <TabPanel key={tab.code} value={currentTab} index={index}>
          {view === 'list' && (
            <BoardList
              boardCode={tab.code}
              onPostClick={handlePostClick}
              onWriteClick={handleWriteClick}
            />
          )}
          {view === 'detail' && selectedPost && (
            <PostDetail
              post={selectedPost}
              onBack={handleBack}
              onEdit={handleEditClick}
            />
          )}
          {view === 'edit' && (
            <PostEditor
              boardCode={tab.code}
              post={editingPost}
              onSave={handleSave}
              onCancel={handleCancel}
            />
          )}
        </TabPanel>
      ))}

      {/* 권한 안내 */}
      {!currentUser && (
        <Alert severity="info" sx={{ mt: 2 }}>
          로그인하면 더 많은 게시판을 이용하고 글을 작성할 수 있습니다.
        </Alert>
      )}

      {currentUser && userRole === 'user' && (
        <Alert severity="info" sx={{ mt: 2 }}>
          프리미엄 회원이 되면 전문가 전략과 고급 분석 게시판을 이용할 수 있습니다.
        </Alert>
      )}
    </Box>
  )
}

export default Community