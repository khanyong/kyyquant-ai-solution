import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  TextField,
  Button,
  Stack,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  FormControlLabel,
  Checkbox,
  Alert,
  IconButton
} from '@mui/material'
import {
  Save,
  Cancel,
  AttachFile,
  LocalOffer
} from '@mui/icons-material'
import { boardService, Post, Board } from '../../services/boardService'
import { useAppSelector } from '../../hooks/redux'

interface PostEditorProps {
  boardCode: string
  post?: Post | null
  onSave: () => void
  onCancel: () => void
}

const PostEditor: React.FC<PostEditorProps> = ({ boardCode, post, onSave, onCancel }) => {
  const [board, setBoard] = useState<Board | null>(null)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [summary, setSummary] = useState('')
  const [category, setCategory] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')
  const [isNotice, setIsNotice] = useState(false)
  const [isPinned, setIsPinned] = useState(false)
  const [isSecret, setIsSecret] = useState(false)
  const [secretPassword, setSecretPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const currentUser = useAppSelector(state => state.auth.user)
  const isAdmin = currentUser?.role === 'admin'

  useEffect(() => {
    loadBoard()
    if (post) {
      setTitle(post.title)
      setContent(post.content)
      setSummary(post.summary || '')
      setCategory(post.category || '')
      setTags(post.tags || [])
      setIsNotice(post.is_notice)
      setIsPinned(post.is_pinned)
      setIsSecret(post.is_secret)
    }
  }, [boardCode, post])

  const loadBoard = async () => {
    try {
      const data = await boardService.getBoardByCode(boardCode)
      setBoard(data)
    } catch (error) {
      console.error('Failed to load board:', error)
    }
  }

  const handleSubmit = async () => {
    if (!title.trim() || !content.trim()) {
      setError('제목과 내용을 입력해주세요.')
      return
    }

    if (isSecret && !secretPassword) {
      setError('비밀글 비밀번호를 입력해주세요.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const postData = {
        title,
        content,
        summary: summary || undefined,
        category: category || undefined,
        tags: tags.length > 0 ? tags : undefined,
        is_notice: isAdmin ? isNotice : false,
        is_pinned: isAdmin ? isPinned : false,
        is_secret: isSecret,
        secret_password: isSecret ? secretPassword : undefined
      }

      if (post) {
        await boardService.updatePost(post.id, postData)
      } else {
        await boardService.createPost(boardCode, postData)
      }

      onSave()
    } catch (error) {
      console.error('Failed to save post:', error)
      setError('게시글 저장에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()])
      setTagInput('')
    }
  }

  const handleDeleteTag = (tagToDelete: string) => {
    setTags(tags.filter(tag => tag !== tagToDelete))
  }

  const categories = board?.categories as string[] || []

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {post ? '게시글 수정' : '새 게시글 작성'}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Stack spacing={3}>
        {/* 카테고리 선택 */}
        {board?.use_category && categories.length > 0 && (
          <FormControl fullWidth>
            <InputLabel>카테고리</InputLabel>
            <Select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              label="카테고리"
            >
              <MenuItem value="">선택 안함</MenuItem>
              {categories.map((cat) => (
                <MenuItem key={cat} value={cat}>{cat}</MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {/* 제목 */}
        <TextField
          fullWidth
          label="제목"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          error={!title.trim() && loading}
          helperText={!title.trim() && loading ? '제목을 입력해주세요' : ''}
        />

        {/* 요약 */}
        <TextField
          fullWidth
          label="요약 (선택사항)"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          multiline
          rows={2}
          helperText="게시글 목록에 표시될 짧은 요약입니다"
        />

        {/* 내용 */}
        <TextField
          fullWidth
          label="내용"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          multiline
          rows={15}
          required
          error={!content.trim() && loading}
          helperText={!content.trim() && loading ? '내용을 입력해주세요' : ''}
        />

        {/* 태그 */}
        <Box>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 1 }}>
            <TextField
              label="태그 추가"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
              size="small"
              sx={{ flexGrow: 1 }}
            />
            <Button
              variant="outlined"
              startIcon={<LocalOffer />}
              onClick={handleAddTag}
              disabled={!tagInput.trim()}
            >
              추가
            </Button>
          </Stack>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            {tags.map((tag) => (
              <Chip
                key={tag}
                label={tag}
                onDelete={() => handleDeleteTag(tag)}
                sx={{ mb: 1 }}
              />
            ))}
          </Stack>
        </Box>

        {/* 옵션 */}
        <Stack direction="row" spacing={2} flexWrap="wrap">
          {isAdmin && (
            <>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={isNotice}
                    onChange={(e) => setIsNotice(e.target.checked)}
                  />
                }
                label="공지사항"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={isPinned}
                    onChange={(e) => setIsPinned(e.target.checked)}
                  />
                }
                label="상단 고정"
              />
            </>
          )}
          <FormControlLabel
            control={
              <Checkbox
                checked={isSecret}
                onChange={(e) => setIsSecret(e.target.checked)}
              />
            }
            label="비밀글"
          />
        </Stack>

        {/* 비밀글 비밀번호 */}
        {isSecret && (
          <TextField
            label="비밀글 비밀번호"
            type="password"
            value={secretPassword}
            onChange={(e) => setSecretPassword(e.target.value)}
            helperText="비밀글 열람 시 필요한 비밀번호입니다"
            required
          />
        )}

        {/* 버튼 */}
        <Stack direction="row" spacing={2} justifyContent="flex-end">
          <Button
            variant="outlined"
            startIcon={<Cancel />}
            onClick={onCancel}
            disabled={loading}
          >
            취소
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSubmit}
            disabled={loading || !title.trim() || !content.trim()}
          >
            {post ? '수정' : '등록'}
          </Button>
        </Stack>
      </Stack>
    </Paper>
  )
}

export default PostEditor