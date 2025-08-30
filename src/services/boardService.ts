import { supabase } from '../lib/supabase'

export interface Board {
  id: string
  code: string
  name: string
  description: string | null
  board_type: string
  read_permission: string
  write_permission: string
  comment_permission: string
  use_comment: boolean
  use_like: boolean
  is_active: boolean
}

export interface Post {
  id: string
  board_id: string
  author_id: string | null
  title: string
  content: string
  summary: string | null
  category: string | null
  tags: string[]
  status: 'draft' | 'published' | 'hidden' | 'deleted'
  is_notice: boolean
  is_pinned: boolean
  is_secret: boolean
  view_count: number
  like_count: number
  comment_count: number
  published_at: string
  updated_at: string
  author?: {
    id: string
    name: string
    email: string
    avatar_url: string | null
  }
  board?: Board
}

export interface Comment {
  id: string
  post_id: string
  author_id: string | null
  parent_id: string | null
  content: string
  is_secret: boolean
  like_count: number
  created_at: string
  updated_at: string
  author?: {
    id: string
    name: string
    email: string
    avatar_url: string | null
  }
  replies?: Comment[]
}

export interface BoardPermission {
  can_read: boolean
  can_write: boolean
  can_comment: boolean
  can_delete_own: boolean
  can_edit_own: boolean
}

class BoardService {
  // 게시판 목록 조회
  async getBoards(): Promise<Board[]> {
    const { data, error } = await supabase
      .from('boards')
      .select('*')
      .eq('is_active', true)
      .order('name')

    if (error) throw error
    return data || []
  }

  // 특정 게시판 조회
  async getBoardByCode(code: string): Promise<Board | null> {
    const { data, error } = await supabase
      .from('boards')
      .select('*')
      .eq('code', code)
      .eq('is_active', true)
      .single()

    if (error) {
      if (error.code === 'PGRST116') return null
      throw error
    }
    return data
  }

  // 게시글 목록 조회
  async getPosts(
    boardCode: string,
    options: {
      page?: number
      limit?: number
      category?: string
      search?: string
    } = {}
  ): Promise<{ posts: Post[]; total: number }> {
    const { page = 1, limit = 20, category, search } = options
    const offset = (page - 1) * limit

    // 먼저 board_id 조회
    const board = await this.getBoardByCode(boardCode)
    if (!board) throw new Error('Board not found')

    let query = supabase
      .from('posts')
      .select(`
        *,
        author:profiles!posts_author_id_fkey(
          id,
          name,
          email,
          avatar_url
        )
      `, { count: 'exact' })
      .eq('board_id', board.id)
      .eq('status', 'published')
      .order('is_pinned', { ascending: false })
      .order('is_notice', { ascending: false })
      .order('published_at', { ascending: false })
      .range(offset, offset + limit - 1)

    if (category) {
      query = query.eq('category', category)
    }

    if (search) {
      query = query.or(`title.ilike.%${search}%,content.ilike.%${search}%`)
    }

    const { data, error, count } = await query

    if (error) throw error
    return { 
      posts: data || [], 
      total: count || 0 
    }
  }

  // 게시글 상세 조회
  async getPost(postId: string): Promise<Post | null> {
    const { data, error } = await supabase
      .from('posts')
      .select(`
        *,
        author:profiles!posts_author_id_fkey(
          id,
          name,
          email,
          avatar_url
        ),
        board:boards!posts_board_id_fkey(
          id,
          code,
          name,
          board_type,
          use_comment,
          use_like
        )
      `)
      .eq('id', postId)
      .single()

    if (error) {
      if (error.code === 'PGRST116') return null
      throw error
    }

    // 조회수 증가
    await this.incrementViewCount(postId)

    return data
  }

  // 조회수 증가
  private async incrementViewCount(postId: string): Promise<void> {
    const { error } = await supabase.rpc('increment_view_count', {
      post_id: postId
    })
    
    // RPC 함수가 없으면 직접 업데이트
    if (error?.code === 'PGRST202') {
      await supabase
        .from('posts')
        .update({ view_count: 1 })
        .eq('id', postId)
    }
  }

  // 게시글 작성
  async createPost(
    boardCode: string,
    post: {
      title: string
      content: string
      summary?: string
      category?: string
      tags?: string[]
      is_notice?: boolean
      is_pinned?: boolean
      is_secret?: boolean
      secret_password?: string
    }
  ): Promise<Post> {
    const board = await this.getBoardByCode(boardCode)
    if (!board) throw new Error('Board not found')

    const { data: userData, error: userError } = await supabase.auth.getUser()
    if (userError || !userData.user) throw new Error('User not authenticated')

    const { data, error } = await supabase
      .from('posts')
      .insert({
        board_id: board.id,
        author_id: userData.user.id,
        ...post,
        status: 'published',
        published_at: new Date().toISOString()
      })
      .select(`
        *,
        author:profiles!posts_author_id_fkey(
          id,
          name,
          email,
          avatar_url
        )
      `)
      .single()

    if (error) throw error
    return data
  }

  // 게시글 수정
  async updatePost(
    postId: string,
    updates: {
      title?: string
      content?: string
      summary?: string
      category?: string
      tags?: string[]
      is_notice?: boolean
      is_pinned?: boolean
    }
  ): Promise<Post> {
    const { data, error } = await supabase
      .from('posts')
      .update({
        ...updates,
        updated_at: new Date().toISOString()
      })
      .eq('id', postId)
      .select(`
        *,
        author:profiles!posts_author_id_fkey(
          id,
          name,
          email,
          avatar_url
        )
      `)
      .single()

    if (error) throw error
    return data
  }

  // 게시글 삭제
  async deletePost(postId: string): Promise<void> {
    const { error } = await supabase
      .from('posts')
      .update({ 
        status: 'deleted',
        deleted_at: new Date().toISOString()
      })
      .eq('id', postId)

    if (error) throw error
  }

  // 댓글 목록 조회
  async getComments(postId: string): Promise<Comment[]> {
    const { data, error } = await supabase
      .from('comments')
      .select(`
        *,
        author:profiles!comments_author_id_fkey(
          id,
          name,
          email,
          avatar_url
        )
      `)
      .eq('post_id', postId)
      .is('deleted_at', null)
      .order('created_at', { ascending: true })

    if (error) throw error

    // 대댓글 구조화
    const comments = data || []
    const rootComments = comments.filter(c => !c.parent_id)
    const repliesMap = new Map<string, Comment[]>()

    comments.forEach(comment => {
      if (comment.parent_id) {
        if (!repliesMap.has(comment.parent_id)) {
          repliesMap.set(comment.parent_id, [])
        }
        repliesMap.get(comment.parent_id)!.push(comment)
      }
    })

    return rootComments.map(comment => ({
      ...comment,
      replies: repliesMap.get(comment.id) || []
    }))
  }

  // 댓글 작성
  async createComment(
    postId: string,
    content: string,
    parentId?: string
  ): Promise<Comment> {
    const { data: userData, error: userError } = await supabase.auth.getUser()
    if (userError || !userData.user) throw new Error('User not authenticated')

    const { data, error } = await supabase
      .from('comments')
      .insert({
        post_id: postId,
        author_id: userData.user.id,
        parent_id: parentId,
        content
      })
      .select(`
        *,
        author:profiles!comments_author_id_fkey(
          id,
          name,
          email,
          avatar_url
        )
      `)
      .single()

    if (error) throw error

    // 댓글 수 증가
    await supabase
      .from('posts')
      .update({ comment_count: 1 })
      .eq('id', postId)

    return data
  }

  // 댓글 삭제
  async deleteComment(commentId: string): Promise<void> {
    const { error } = await supabase
      .from('comments')
      .update({ 
        deleted_at: new Date().toISOString()
      })
      .eq('id', commentId)

    if (error) throw error
  }

  // 좋아요/싫어요
  async toggleReaction(
    targetId: string,
    targetType: 'post' | 'comment',
    reactionType: 'like' | 'dislike'
  ): Promise<void> {
    const { data: userData, error: userError } = await supabase.auth.getUser()
    if (userError || !userData.user) throw new Error('User not authenticated')

    // 기존 반응 확인
    const { data: existing } = await supabase
      .from('reactions')
      .select('*')
      .eq('user_id', userData.user.id)
      .eq(targetType === 'post' ? 'post_id' : 'comment_id', targetId)
      .single()

    if (existing) {
      if (existing.reaction_type === reactionType) {
        // 같은 반응이면 삭제
        await supabase
          .from('reactions')
          .delete()
          .eq('id', existing.id)

        // 카운트 감소
        const table = targetType === 'post' ? 'posts' : 'comments'
        const field = reactionType === 'like' ? 'like_count' : 'dislike_count'
        await supabase
          .from(table)
          .update({ [field]: 0 })
          .eq('id', targetId)
      } else {
        // 다른 반응이면 변경
        await supabase
          .from('reactions')
          .update({ reaction_type: reactionType })
          .eq('id', existing.id)

        // 카운트 조정
        const table = targetType === 'post' ? 'posts' : 'comments'
        const oldField = existing.reaction_type === 'like' ? 'like_count' : 'dislike_count'
        const newField = reactionType === 'like' ? 'like_count' : 'dislike_count'
        
        await supabase
          .from(table)
          .update({ 
            [oldField]: 0,
            [newField]: 1
          })
          .eq('id', targetId)
      }
    } else {
      // 새로운 반응 추가
      await supabase
        .from('reactions')
        .insert({
          user_id: userData.user.id,
          [targetType === 'post' ? 'post_id' : 'comment_id']: targetId,
          reaction_type: reactionType
        })

      // 카운트 증가
      const table = targetType === 'post' ? 'posts' : 'comments'
      const field = reactionType === 'like' ? 'like_count' : 'dislike_count'
      await supabase
        .from(table)
        .update({ [field]: 1 })
        .eq('id', targetId)
    }
  }

  // 사용자 권한 확인
  async checkPermission(
    boardCode: string,
    action: 'read' | 'write' | 'comment'
  ): Promise<boolean> {
    const { data: userData } = await supabase.auth.getUser()
    const board = await this.getBoardByCode(boardCode)
    
    if (!board) return false

    const permission = `${action}_permission`
    const requiredPermission = board[permission as keyof Board] as string

    if (requiredPermission === 'all') return true
    if (!userData.user) return false
    if (requiredPermission === 'user') return true

    // 프로필에서 role 확인
    const { data: profile } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', userData.user.id)
      .single()

    if (!profile) return false

    // admin은 모든 권한
    if (profile.role === 'admin') return true

    // role 기반 권한 확인
    if (requiredPermission === profile.role) return true
    
    // premium 권한이 필요한 경우
    if (requiredPermission === 'premium' && 
        (profile.role === 'premium' || profile.role === 'vip')) {
      return true
    }

    return false
  }
}

export const boardService = new BoardService()