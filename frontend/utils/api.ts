import type { User, Todo, TodoStats, TodoCreate, TodoUpdate, Notification, NotificationsListResponse, Comment, CommentCreate, Attachment } from '~/types'

const BASE_URL = 'http://localhost:8000/api'
const TIMEOUT_MS = 15000

interface FetchOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: unknown
  params?: Record<string, string | undefined>
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { method = 'GET', body, params } = options

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS)

  try {
    const response = await $fetch<T>(path, {
      baseURL: BASE_URL,
      method,
      body: body ? body : undefined,
      params: params
        ? Object.fromEntries(
            Object.entries(params).filter(([, v]) => v !== undefined)
          )
        : undefined,
      credentials: 'include',
      signal: controller.signal,
    })
    return response
  } catch (error: any) {
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.')
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
  }
}

// Auth API
export const authApi = {
  register(data: { email: string; username: string; password: string; password_confirm: string }) {
    return apiFetch<User>('/auth/register', { method: 'POST', body: data })
  },

  login(data: { identifier: string; password: string }) {
    return apiFetch<User>('/auth/login', { method: 'POST', body: data })
  },

  logout() {
    return apiFetch<void>('/auth/logout', { method: 'POST' })
  },

  me() {
    return apiFetch<User>('/auth/me')
  },
}

// Todos API
export const todosApi = {
  list(params?: { status?: string; priority?: string; sort_by?: string }) {
    return apiFetch<Todo[]>('/todos', { params })
  },

  get(id: string) {
    return apiFetch<Todo>(`/todos/${id}`)
  },

  create(data: TodoCreate) {
    return apiFetch<Todo>('/todos', { method: 'POST', body: data })
  },

  update(id: string, data: TodoUpdate) {
    return apiFetch<Todo>(`/todos/${id}`, { method: 'PUT', body: data })
  },

  delete(id: string) {
    return apiFetch<void>(`/todos/${id}`, { method: 'DELETE' })
  },

  stats() {
    return apiFetch<TodoStats>('/todos/stats')
  },
}

// Notifications API
export const notificationsApi = {
  list() {
    return apiFetch<NotificationsListResponse>('/notifications')
  },

  markAsRead(id: string) {
    return apiFetch<Notification>(`/notifications/${id}/read`, { method: 'PATCH' })
  },

  markAllAsRead() {
    return apiFetch<{ marked_count: number }>('/notifications/read-all', { method: 'POST' })
  },

  clearAll() {
    return apiFetch<void>('/notifications', { method: 'DELETE' })
  },
}

// Comments API
export const commentsApi = {
  list(todoId: string) {
    return apiFetch<Comment[]>(`/todos/${todoId}/comments`)
  },

  create(todoId: string, data: CommentCreate) {
    return apiFetch<Comment>(`/todos/${todoId}/comments`, { method: 'POST', body: data })
  },

  delete(todoId: string, commentId: string) {
    return apiFetch<void>(`/todos/${todoId}/comments/${commentId}`, { method: 'DELETE' })
  },
}

// Attachments API
export const attachmentsApi = {
  list(todoId: string) {
    return apiFetch<Attachment[]>(`/todos/${todoId}/attachments`)
  },

  async upload(todoId: string, file: File): Promise<Attachment> {
    const formData = new FormData()
    formData.append('file', file)

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 30000) // 30s for uploads

    try {
      const response = await $fetch<Attachment>(`/todos/${todoId}/attachments`, {
        baseURL: BASE_URL,
        method: 'POST',
        body: formData,
        credentials: 'include',
        signal: controller.signal,
      })
      return response
    } catch (error: any) {
      if (error.name === 'AbortError') {
        throw new Error('Upload timed out. Please try again.')
      }
      throw error
    } finally {
      clearTimeout(timeoutId)
    }
  },

  getFileUrl(todoId: string, attachmentId: string) {
    return `${BASE_URL}/todos/${todoId}/attachments/${attachmentId}/file`
  },

  delete(todoId: string, attachmentId: string) {
    return apiFetch<void>(`/todos/${todoId}/attachments/${attachmentId}`, { method: 'DELETE' })
  },
}
