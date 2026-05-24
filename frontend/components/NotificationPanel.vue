<template>
  <div
    class="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-white dark:bg-secondary-800 rounded-lg shadow-xl border border-secondary-200 dark:border-secondary-700 z-50 overflow-hidden"
    role="menu"
    aria-label="Notifications"
  >
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-secondary-200 dark:border-secondary-700">
      <h3 class="text-sm font-semibold text-secondary-900 dark:text-white">
        Notifications
      </h3>
      <div class="flex items-center gap-2">
        <button
          v-if="notifications.length > 0 && unreadCount > 0"
          type="button"
          class="text-xs text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium transition-colors"
          @click="$emit('markAllAsRead')"
        >
          Mark all read
        </button>
        <button
          v-if="notifications.length > 0"
          type="button"
          class="text-xs text-secondary-500 dark:text-secondary-400 hover:text-red-600 dark:hover:text-red-400 font-medium transition-colors"
          @click="$emit('clearAll')"
        >
          Clear all
        </button>
      </div>
    </div>

    <!-- Notification list -->
    <div class="max-h-80 overflow-y-auto">
      <!-- Loading state -->
      <div v-if="loading && notifications.length === 0" class="px-4 py-8 text-center">
        <svg class="animate-spin h-5 w-5 mx-auto text-primary-600 dark:text-primary-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-2 text-xs text-secondary-500 dark:text-secondary-400">Loading notifications...</p>
      </div>

      <!-- Empty state -->
      <div v-else-if="notifications.length === 0" class="px-4 py-8 text-center">
        <svg class="w-10 h-10 mx-auto text-secondary-300 dark:text-secondary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <p class="mt-2 text-sm text-secondary-500 dark:text-secondary-400">No notifications</p>
        <p class="text-xs text-secondary-400 dark:text-secondary-500">You're all caught up!</p>
      </div>

      <!-- Notification items -->
      <ul v-else class="divide-y divide-secondary-100 dark:divide-secondary-700">
        <li
          v-for="notification in notifications"
          :key="notification.id"
          class="px-4 py-3 hover:bg-secondary-50 dark:hover:bg-secondary-750 transition-colors cursor-pointer"
          :class="{ 'bg-primary-50/50 dark:bg-primary-900/10': !notification.is_read }"
          role="menuitem"
          @click="$emit('markAsRead', notification.id)"
        >
          <div class="flex items-start gap-3">
            <!-- Icon -->
            <div
              class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
              :class="notificationIconClasses(notification.type)"
            >
              <!-- Reminder icon (clock) -->
              <svg v-if="notification.type === 'reminder'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <!-- Overdue icon (exclamation) -->
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <p
                class="text-sm leading-snug"
                :class="notification.is_read
                  ? 'text-secondary-500 dark:text-secondary-400'
                  : 'text-secondary-900 dark:text-white font-medium'"
              >
                {{ notification.message }}
              </p>
              <p class="mt-0.5 text-xs text-secondary-400 dark:text-secondary-500">
                {{ formatTimeAgo(notification.created_at) }}
              </p>
            </div>

            <!-- Unread indicator -->
            <div v-if="!notification.is_read" class="flex-shrink-0 mt-1.5">
              <span class="block w-2 h-2 rounded-full bg-primary-500" aria-label="Unread"></span>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Notification } from '~/types'

defineProps<{
  notifications: Notification[]
  unreadCount: number
  loading: boolean
}>()

defineEmits<{
  markAsRead: [id: string]
  markAllAsRead: []
  clearAll: []
}>()

function notificationIconClasses(type: string): string {
  if (type === 'reminder') {
    return 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
  }
  return 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
}

function formatTimeAgo(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSeconds < 60) return 'Just now'
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>
