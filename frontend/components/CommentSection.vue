<template>
  <div class="mt-4 border-t border-secondary-200 dark:border-secondary-700 pt-4">
    <!-- Header -->
    <button
      type="button"
      class="flex items-center gap-2 text-sm font-medium text-secondary-700 dark:text-secondary-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
      @click="expanded = !expanded"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
      Comments ({{ comments.length }})
      <svg
        class="w-3 h-3 transition-transform duration-200"
        :class="{ 'rotate-180': expanded }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Comments list -->
    <div v-if="expanded" class="mt-3 space-y-3">
      <!-- Loading -->
      <div v-if="loading" class="text-sm text-secondary-500 dark:text-secondary-400">
        Loading comments...
      </div>

      <!-- Empty state -->
      <div v-else-if="comments.length === 0" class="text-sm text-secondary-500 dark:text-secondary-400 italic">
        No comments yet. Be the first to comment.
      </div>

      <!-- Comment items -->
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="flex gap-2 group"
      >
        <div class="flex-shrink-0 w-7 h-7 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
          <span class="text-xs font-medium text-primary-700 dark:text-primary-300">
            {{ comment.username.charAt(0).toUpperCase() }}
          </span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="text-xs font-medium text-secondary-700 dark:text-secondary-300">
              {{ comment.username }}
            </span>
            <span class="text-xs text-secondary-400 dark:text-secondary-500">
              {{ formatDate(comment.created_at) }}
            </span>
            <button
              v-if="comment.user_id === currentUserId"
              type="button"
              class="opacity-0 group-hover:opacity-100 text-xs text-red-500 hover:text-red-700 transition-all"
              aria-label="Delete comment"
              @click="handleDelete(comment.id)"
            >
              Delete
            </button>
          </div>
          <p class="text-sm text-secondary-800 dark:text-secondary-200 whitespace-pre-wrap break-words">
            {{ comment.content }}
          </p>
        </div>
      </div>

      <!-- Add comment form -->
      <form class="flex gap-2 mt-3" @submit.prevent="handleSubmit">
        <input
          v-model="newComment"
          type="text"
          placeholder="Add a comment..."
          maxlength="1000"
          class="flex-1 text-sm rounded-lg border border-secondary-300 dark:border-secondary-600 bg-white dark:bg-secondary-700 px-3 py-2 text-secondary-900 dark:text-white placeholder-secondary-400 dark:placeholder-secondary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          :disabled="submitting"
        />
        <button
          type="submit"
          class="px-3 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!newComment.trim() || submitting"
        >
          {{ submitting ? '...' : 'Post' }}
        </button>
      </form>

      <!-- Error -->
      <p v-if="error" class="text-xs text-red-500 mt-1">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { commentsApi } from '~/utils/api'
import type { Comment } from '~/types'

const props = defineProps<{
  todoId: string
  currentUserId: string
}>()

const expanded = ref(false)
const comments = ref<Comment[]>([])
const loading = ref(false)
const submitting = ref(false)
const newComment = ref('')
const error = ref<string | null>(null)

async function fetchComments() {
  loading.value = true
  error.value = null
  try {
    comments.value = await commentsApi.list(props.todoId)
  } catch (err: any) {
    error.value = 'Failed to load comments'
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!newComment.value.trim()) return

  submitting.value = true
  error.value = null
  try {
    const comment = await commentsApi.create(props.todoId, { content: newComment.value.trim() })
    comments.value.push(comment)
    newComment.value = ''
  } catch (err: any) {
    error.value = 'Failed to post comment'
  } finally {
    submitting.value = false
  }
}

async function handleDelete(commentId: string) {
  try {
    await commentsApi.delete(props.todoId, commentId)
    comments.value = comments.value.filter(c => c.id !== commentId)
  } catch (err: any) {
    error.value = 'Failed to delete comment'
  }
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

// Fetch comments when expanded
watch(expanded, (val) => {
  if (val && comments.value.length === 0) {
    fetchComments()
  }
})
</script>
