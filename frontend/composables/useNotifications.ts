import { ref, readonly } from 'vue'
import { notificationsApi } from '~/utils/api'
import type { Notification } from '~/types'

const POLL_INTERVAL_MS = 30000

const notifications = ref<Notification[]>([])
const unreadCount = ref(0)
const loading = ref(false)
const error = ref<string | null>(null)

let pollTimer: ReturnType<typeof setInterval> | null = null

export function useNotifications() {
  async function fetchNotifications(): Promise<void> {
    try {
      loading.value = true
      error.value = null
      const response = await notificationsApi.list()
      notifications.value = response.notifications
      unreadCount.value = response.unread_count
    } catch (err: any) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function markAsRead(id: string): Promise<void> {
    // Optimistic update
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index !== -1 && !notifications.value[index].is_read) {
      notifications.value[index] = { ...notifications.value[index], is_read: true }
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }

    try {
      await notificationsApi.markAsRead(id)
    } catch (err: any) {
      // Rollback on failure
      if (index !== -1) {
        notifications.value[index] = { ...notifications.value[index], is_read: false }
        unreadCount.value += 1
      }
      error.value = extractErrorMessage(err)
    }
  }

  async function markAllAsRead(): Promise<void> {
    // Optimistic update
    const previousNotifications = notifications.value.map((n) => ({ ...n }))
    const previousCount = unreadCount.value
    notifications.value = notifications.value.map((n) => ({ ...n, is_read: true }))
    unreadCount.value = 0

    try {
      await notificationsApi.markAllAsRead()
    } catch (err: any) {
      // Rollback on failure
      notifications.value = previousNotifications
      unreadCount.value = previousCount
      error.value = extractErrorMessage(err)
    }
  }

  async function clearAll(): Promise<void> {
    // Optimistic update
    const previousNotifications = notifications.value.map((n) => ({ ...n }))
    const previousCount = unreadCount.value
    notifications.value = []
    unreadCount.value = 0

    try {
      await notificationsApi.clearAll()
    } catch (err: any) {
      // Rollback on failure
      notifications.value = previousNotifications
      unreadCount.value = previousCount
      error.value = extractErrorMessage(err)
    }
  }

  function startPolling(): void {
    // Fetch immediately
    fetchNotifications()

    // Set up interval
    if (pollTimer === null) {
      pollTimer = setInterval(fetchNotifications, POLL_INTERVAL_MS)
    }
  }

  function stopPolling(): void {
    if (pollTimer !== null) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return {
    // State
    notifications: readonly(notifications),
    unreadCount: readonly(unreadCount),
    loading: readonly(loading),
    error: readonly(error),

    // Actions
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    clearAll,
    startPolling,
    stopPolling,
  }
}

function extractErrorMessage(err: any): string {
  const statusCode = err?.response?.status || err?.statusCode || err?.status
  const data = err?.response?._data || err?.data

  if (statusCode === 401) {
    return 'Authentication required'
  }

  if (statusCode === 404) {
    return data?.detail || 'Notification not found'
  }

  if (err?.message === 'Request timed out. Please try again.') {
    return err.message
  }

  if (err?.message) {
    return err.message
  }

  return 'Something went wrong. Please try again.'
}
