import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Typography,
  Stack,
  IconButton,
  Button,
  TextField,
  InputAdornment,
  Skeleton,
  Avatar,
  Tooltip
} from '@mui/material'
import {
  Visibility,
  ThumbUp,
  Comment,
  Search,
  Edit,
  PushPin,
  Announcement,
  Lock
} from '@mui/icons-material'
import { boardService, Post } from '../../services/boardService'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'

interface BoardListProps {
  boardCode: string
  onPostClick: (post: Post) => void
  onWriteClick: () => void
}

const BoardList: React.FC<BoardListProps> = ({ boardCode, onPostClick, onWriteClick }) => {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(20)
  const [total, setTotal] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')
  const [canWrite, setCanWrite] = useState(false)

  useEffect(() => {
    loadPosts()
    checkWritePermission()
  }, [boardCode, page, rowsPerPage])

  const loadPosts = async () => {
    try {
      setLoading(true)
      const { posts, total } = await boardService.getPosts(boardCode, {
        page: page + 1,
        limit: rowsPerPage,
        search: searchTerm || undefined
      })
      setPosts(posts)
      setTotal(total)
    } catch (error) {
      console.error('Failed to load posts:', error)
    } finally {
      setLoading(false)
    }
  }

  const checkWritePermission = async () => {
    try {
      const permission = await boardService.checkPermission(boardCode, 'write')
      setCanWrite(permission)
    } catch (error) {
      console.error('Failed to check permission:', error)
      setCanWrite(false)
    }
  }

  const handleSearch = () => {
    setPage(0)
    loadPosts()
  }

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const getPostTypeIcon = (post: Post) => {
    if (post.is_notice) return <Announcement fontSize="small" color="error" />
    if (post.is_pinned) return <PushPin fontSize="small" color="primary" />
    if (post.is_secret) return <Lock fontSize="small" color="action" />
    return null
  }

  const getCategoryColor = (category: string | null) => {
    if (!category) return 'default'
    const colorMap: Record<string, any> = {
      '공지': 'error',
      '중요': 'warning',
      '질문': 'info',
      '정보': 'success',
      '일반': 'default'
    }
    return colorMap[category] || 'default'
  }

  return (
    <Box>
      {/* 검색 및 글쓰기 버튼 */}
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <TextField
          size="small"
          placeholder="제목 또는 내용 검색"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            )
          }}
          sx={{ flexGrow: 1 }}
        />
        <Button variant="contained" onClick={handleSearch}>
          검색
        </Button>
        {canWrite && (
          <Button variant="contained" color="primary" onClick={onWriteClick}>
            글쓰기
          </Button>
        )}
      </Stack>

      {/* 게시글 목록 */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width="80" align="center">번호</TableCell>
              <TableCell>제목</TableCell>
              <TableCell width="120" align="center">작성자</TableCell>
              <TableCell width="80" align="center">조회</TableCell>
              <TableCell width="80" align="center">추천</TableCell>
              <TableCell width="120" align="center">작성일</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              Array.from({ length: 5 }).map((_, index) => (
                <TableRow key={index}>
                  <TableCell colSpan={6}>
                    <Skeleton variant="rectangular" height={40} />
                  </TableCell>
                </TableRow>
              ))
            ) : posts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography color="text.secondary" sx={{ py: 4 }}>
                    게시글이 없습니다.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              posts.map((post, index) => (
                <TableRow 
                  key={post.id}
                  hover
                  onClick={() => onPostClick(post)}
                  sx={{ 
                    cursor: 'pointer',
                    backgroundColor: post.is_notice ? 'action.hover' : 'inherit'
                  }}
                >
                  <TableCell align="center">
                    {post.is_notice ? (
                      <Chip label="공지" size="small" color="error" />
                    ) : (
                      total - (page * rowsPerPage + index)
                    )}
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1} alignItems="center">
                      {getPostTypeIcon(post)}
                      {post.category && (
                        <Chip 
                          label={post.category} 
                          size="small" 
                          color={getCategoryColor(post.category) as any}
                        />
                      )}
                      <Typography variant="body2">
                        {post.title}
                      </Typography>
                      {post.comment_count > 0 && (
                        <Typography variant="caption" color="primary">
                          [{post.comment_count}]
                        </Typography>
                      )}
                    </Stack>
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={1} alignItems="center" justifyContent="center">
                      <Avatar 
                        src={post.author?.avatar_url || undefined}
                        sx={{ width: 24, height: 24 }}
                      >
                        {post.author?.name?.[0] || '?'}
                      </Avatar>
                      <Typography variant="body2">
                        {post.author?.name || '알 수 없음'}
                      </Typography>
                    </Stack>
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={0.5} alignItems="center" justifyContent="center">
                      <Visibility fontSize="small" color="action" />
                      <Typography variant="body2">{post.view_count}</Typography>
                    </Stack>
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={0.5} alignItems="center" justifyContent="center">
                      <ThumbUp fontSize="small" color="action" />
                      <Typography variant="body2">{post.like_count}</Typography>
                    </Stack>
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title={new Date(post.published_at).toLocaleString()}>
                      <Typography variant="caption">
                        {formatDistanceToNow(new Date(post.published_at), { 
                          addSuffix: true,
                          locale: ko 
                        })}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 페이지네이션 */}
      <TablePagination
        rowsPerPageOptions={[10, 20, 50]}
        component="div"
        count={total}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="페이지당 게시글"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} / 전체 ${count}`}
      />
    </Box>
  )
}

export default BoardList