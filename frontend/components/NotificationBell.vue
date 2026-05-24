<template>
  <div class="relative" ref="bellContainer">
    <!-- Bell button -->
    <button
      type="button"
      class="relative p-2 rounded-md text-secondary-500 hover:text-secondary-700 dark:text-secondary-400 dark:hover:text-secondary-200 hover:bg-secondary-100 dark:hover:bg-secondary-700 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary-500"
      aria-label="Notifications"
      :aria-expanded="panelOpen"
      @click="togglePanel"
    >
      <!-- Bell icon -->
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>

      <!-- Unread badge -->
      <span
        v-if="unreadCount > 0"
        class="absolute -top-0.5 -right-0.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-red-500 rounded-full ring-2 ring-white dark:ring-secondary-800"
        aria-label="Unread notifications count"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <!-- Notification panel -->
    <NotificationPanel
      v-if="panelOpen"
      :notifications="notifications"
      :unread-count="unreadCount"
      :loading="loading"
      @mark-as-read="handleMarkAsRead"
      @mark-all-as-read="handleMarkAllAsRead"
      @clear-all="handleClearAll"
    />
  </div>
</template>

<script setup lang="ts">
import { useNotifications } from '~/composables/useNotifications'

const {
  notifications,
  unreadCount,
  loading,
  startPolling,
  stopPolling,
  markAsRead,
  markAllAsRead,
  clearAll,
} = useNotifications()

const panelOpen = ref(false)
const bellContainer = ref<HTMLElement | null>(null)

function togglePanel() {
  panelOpen.value = !panelOpen.value
}

function handleMarkAsRead(id: string) {
  markAsRead(id)
}

function handleMarkAllAsRead() {
  markAllAsRead()
}

function handleClearAll() {
  clearAll()
  panelOpen.value = false
}

// Close panel when clicking outside
function handleClickOutside(event: MouseEvent) {
  if (bellContainer.value && !bellContainer.value.contains(event.target as Node)) {
    panelOpen.value = false
  }
}

onMounted(() => {
  startPolling()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  stopPolling()
  document.removeEventListener('click', handleClickOutside)
})
</script>
