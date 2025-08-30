import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Stack,
  Divider,
  Chip,
  Button,
  Avatar,
  IconButton,
  TextField,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Skeleton,
  Alert,
  Menu,
  MenuItem
} from '@mui/material'
import {
  ArrowBack,
  ThumbUp,
  ThumbDown,
  Visibility,
  Edit,
  Delete,
  MoreVert,
  Reply,
  Send
} from '@mui/icons-material'
import { boardService, Post, Comment } from '../../services/boardService'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'
import { useAppSelector } from '../../hooks/redux'

interface PostDetailProps {
  post: Post
  onBack: () => void
  onEdit?: (post: Post) => void
}

const PostDetail: React.FC<PostDetailProps> = ({ post, onBack, onEdit }) => {
  const [fullPost, setFullPost] = useState<Post | null>(null)
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState('')
  const [replyTo, setReplyTo] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const currentUser = useAppSelector(state => state.auth.user)

  useEffect(() => {
    loadPostDetail()
    loadComments()
  }, [post.id])

  const loadPostDetail = async () => {
    try {
      setLoading(true)
      const data = await boardService.getPost(post.id)
      if (data) {
        setFullPost(data)
      }
    } catch (error) {
      console.error('Failed to load post:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadComments = async () => {
    try {
      const data = await boardService.getComments(post.id)
      setComments(data)
    } catch (error) {
      console.error('Failed to load comments:', error)
    }
  }

  const handleLike = async () => {
    try {
      await boardService.toggleReaction(post.id, 'post', 'like')
      loadPostDetail()
    } catch (error) {
      console.error('Failed to toggle like:', error)
    }
  }

  const handleDislike = async () => {
    try {
      await boardService.toggleReaction(post.id, 'post', 'dislike')
      loadPostDetail()
    } catch (error) {
      console.error('Failed to toggle dislike:', error)
    }
  }

  const handleCommentSubmit = async () => {
    if (!newComment.trim()) return

    try {
      await boardService.createComment(post.id, newComment, replyTo || undefined)
      setNewComment('')
      setReplyTo(null)
      loadComments()
      loadPostDetail() // 댓글 수 업데이트
    } catch (error) {
      console.error('Failed to create comment:', error)
    }
  }

  const handleDeletePost = async () => {
    if (!window.confirm('정말로 이 게시글을 삭제하시겠습니까?')) return

    try {
      await boardService.deletePost(post.id)
      onBack()
    } catch (error) {
      console.error('Failed to delete post:', error)
    }
  }

  const handleDeleteComment = async (commentId: string) => {
    if (!window.confirm('정말로 이 댓글을 삭제하시겠습니까?')) return

    try {
      await boardService.deleteComment(commentId)
      loadComments()
      loadPostDetail()
    } catch (error) {
      console.error('Failed to delete comment:', error)
    }
  }

  const isAuthor = currentUser?.id === post.author_id

  const renderComment = (comment: Comment, isReply = false) => (
    <ListItem 
      key={comment.id} 
      alignItems="flex-start"
      sx={{ pl: isReply ? 8 : 2 }}
    >
      <ListItemAvatar>
        <Avatar src={comment.author?.avatar_url || undefined}>
          {comment.author?.name?.[0] || '?'}
        </Avatar>
      </ListItemAvatar>
      <ListItemText
        primary={
          <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="subtitle2">
              {comment.author?.name || '알 수 없음'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {formatDistanceToNow(new Date(comment.created_at), { 
                addSuffix: true,
                locale: ko 
              })}
            </Typography>
            {currentUser?.id === comment.author_id && (
              <IconButton 
                size="small" 
                onClick={() => handleDeleteComment(comment.id)}
              >
                <Delete fontSize="small" />
              </IconButton>
            )}
          </Stack>
        }
        secondary={
          <>
            <Typography variant="body2" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
              {comment.content}
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
              <Button
                size="small"
                startIcon={<Reply />}
                onClick={() => setReplyTo(comment.id)}
              >
                답글
              </Button>
              <IconButton size="small">
                <ThumbUp fontSize="small" />
              </IconButton>
              <Typography variant="caption">{comment.like_count}</Typography>
            </Stack>
          </>
        }
      />
    </ListItem>
  )

  if (loading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Skeleton variant="text" width="60%" height={40} />
        <Skeleton variant="rectangular" height={200} sx={{ mt: 2 }} />
      </Paper>
    )
  }

  const displayPost = fullPost || post

  return (
    <Box>
      {/* 헤더 */}
      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
        <IconButton onClick={onBack}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h6">게시글</Typography>
      </Stack>

      {/* 게시글 내용 */}
      <Paper sx={{ p: 3, mb: 2 }}>
        {/* 제목 및 메타 정보 */}
        <Stack spacing={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
            <Box>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                {displayPost.is_notice && (
                  <Chip label="공지" size="small" color="error" />
                )}
                {displayPost.category && (
                  <Chip label={displayPost.category} size="small" />
                )}
              </Stack>
              <Typography variant="h5" gutterBottom>
                {displayPost.title}
              </Typography>
            </Box>
            {isAuthor && (
              <Box>
                <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
                  <MoreVert />
                </IconButton>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={() => setAnchorEl(null)}
                >
                  <MenuItem onClick={() => onEdit?.(displayPost)}>
                    <Edit fontSize="small" sx={{ mr: 1 }} />
                    수정
                  </MenuItem>
                  <MenuItem onClick={handleDeletePost}>
                    <Delete fontSize="small" sx={{ mr: 1 }} />
                    삭제
                  </MenuItem>
                </Menu>
              </Box>
            )}
          </Stack>

          {/* 작성자 정보 */}
          <Stack direction="row" spacing={2} alignItems="center">
            <Avatar src={displayPost.author?.avatar_url || undefined}>
              {displayPost.author?.name?.[0] || '?'}
            </Avatar>
            <Box>
              <Typography variant="subtitle1">
                {displayPost.author?.name || '알 수 없음'}
              </Typography>
              <Stack direction="row" spacing={2}>
                <Typography variant="caption" color="text.secondary">
                  {new Date(displayPost.published_at).toLocaleString()}
                </Typography>
                <Stack direction="row" spacing={0.5} alignItems="center">
                  <Visibility fontSize="small" />
                  <Typography variant="caption">{displayPost.view_count}</Typography>
                </Stack>
              </Stack>
            </Box>
          </Stack>

          <Divider />

          {/* 본문 */}
          <Typography 
            variant="body1" 
            sx={{ 
              minHeight: 200, 
              whiteSpace: 'pre-wrap',
              py: 2 
            }}
          >
            {displayPost.content}
          </Typography>

          {/* 태그 */}
          {displayPost.tags && displayPost.tags.length > 0 && (
            <Stack direction="row" spacing={1}>
              {displayPost.tags.map((tag, index) => (
                <Chip key={index} label={`#${tag}`} size="small" variant="outlined" />
              ))}
            </Stack>
          )}

          <Divider />

          {/* 추천/비추천 */}
          <Stack direction="row" spacing={2} justifyContent="center">
            <Button
              variant="outlined"
              startIcon={<ThumbUp />}
              onClick={handleLike}
            >
              추천 {displayPost.like_count}
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<ThumbDown />}
              onClick={handleDislike}
            >
              비추천 {displayPost.like_count || 0}
            </Button>
          </Stack>
        </Stack>
      </Paper>

      {/* 댓글 섹션 */}
      {displayPost.board?.use_comment !== false && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            댓글 {displayPost.comment_count}개
          </Typography>

          {/* 댓글 작성 */}
          {currentUser ? (
            <Box sx={{ mb: 3 }}>
              {replyTo && (
                <Alert 
                  severity="info" 
                  onClose={() => setReplyTo(null)}
                  sx={{ mb: 1 }}
                >
                  답글 작성 중
                </Alert>
              )}
              <Stack direction="row" spacing={2}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  placeholder="댓글을 작성하세요..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                />
                <Button
                  variant="contained"
                  endIcon={<Send />}
                  onClick={handleCommentSubmit}
                  disabled={!newComment.trim()}
                >
                  등록
                </Button>
              </Stack>
            </Box>
          ) : (
            <Alert severity="info" sx={{ mb: 3 }}>
              댓글을 작성하려면 로그인이 필요합니다.
            </Alert>
          )}

          {/* 댓글 목록 */}
          <List>
            {comments.length === 0 ? (
              <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
                첫 댓글을 작성해보세요!
              </Typography>
            ) : (
              comments.map(comment => (
                <React.Fragment key={comment.id}>
                  {renderComment(comment)}
                  {comment.replies?.map(reply => renderComment(reply, true))}
                </React.Fragment>
              ))
            )}
          </List>
        </Paper>
      )}
    </Box>
  )
}

export default PostDetail