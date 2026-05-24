<template>
  <div class="mt-3 border-t border-secondary-200 dark:border-secondary-700 pt-3">
    <!-- Header -->
    <button
      type="button"
      class="flex items-center gap-2 text-sm font-medium text-secondary-700 dark:text-secondary-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
      @click="expanded = !expanded"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      Images ({{ attachments.length }})
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

    <!-- Attachments content -->
    <div v-if="expanded" class="mt-3">
      <!-- Loading -->
      <div v-if="loading" class="text-sm text-secondary-500 dark:text-secondary-400">
        Loading attachments...
      </div>

      <!-- Image grid -->
      <div v-else-if="attachments.length > 0" class="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-3">
        <div
          v-for="attachment in attachments"
          :key="attachment.id"
          class="relative group rounded-lg overflow-hidden border border-secondary-200 dark:border-secondary-700"
        >
          <img
            :src="getImageUrl(attachment)"
            :alt="attachment.filename"
            class="w-full h-24 object-cover cursor-pointer hover:opacity-90 transition-opacity"
            loading="lazy"
            @click="openPreview(attachment)"
          />
          <button
            v-if="attachment.user_id === currentUserId"
            type="button"
            class="absolute top-1 right-1 opacity-0 group-hover:opacity-100 bg-red-500 hover:bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center transition-all"
            aria-label="Delete attachment"
            @click.stop="handleDelete(attachment.id)"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <div class="absolute bottom-0 left-0 right-0 bg-black/50 px-1.5 py-0.5">
            <p class="text-xs text-white truncate">{{ attachment.filename }}</p>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="text-sm text-secondary-500 dark:text-secondary-400 italic mb-3">
        No images attached yet.
      </div>

      <!-- Upload button -->
      <div class="flex items-center gap-2">
        <label
          class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-primary-700 dark:text-primary-300 bg-primary-50 dark:bg-primary-900/30 hover:bg-primary-100 dark:hover:bg-primary-900/50 rounded-lg cursor-pointer transition-colors"
          :class="{ 'opacity-50 cursor-not-allowed': uploading }"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          {{ uploading ? 'Uploading...' : 'Add Image' }}
          <input
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            class="hidden"
            :disabled="uploading"
            @change="handleFileSelect"
          />
        </label>
        <span class="text-xs text-secondary-400 dark:text-secondary-500">
          JPEG, PNG, GIF, WebP (max 5 MB)
        </span>
      </div>

      <!-- Error -->
      <p v-if="error" class="text-xs text-red-500 mt-2">{{ error }}</p>
    </div>

    <!-- Image preview modal -->
    <Teleport to="body">
      <div
        v-if="previewAttachment"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80"
        @click="previewAttachment = null"
      >
        <img
          :src="getImageUrl(previewAttachment)"
          :alt="previewAttachment.filename"
          class="max-w-full max-h-[90vh] object-contain rounded-lg shadow-2xl"
          @click.stop
        />
        <button
          type="button"
          class="absolute top-4 right-4 text-white hover:text-secondary-300 transition-colors"
          aria-label="Close preview"
          @click="previewAttachment = null"
        >
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { attachmentsApi } from '~/utils/api'
import type { Attachment } from '~/types'

const props = defineProps<{
  todoId: string
  currentUserId: string
}>()

const expanded = ref(false)
const attachments = ref<Attachment[]>([])
const loading = ref(false)
const uploading = ref(false)
const error = ref<string | null>(null)
const previewAttachment = ref<Attachment | null>(null)

function getImageUrl(attachment: Attachment): string {
  return attachmentsApi.getFileUrl(props.todoId, attachment.id)
}

function openPreview(attachment: Attachment) {
  previewAttachment.value = attachment
}

async function fetchAttachments() {
  loading.value = true
  error.value = null
  try {
    attachments.value = await attachmentsApi.list(props.todoId)
  } catch (err: any) {
    error.value = 'Failed to load attachments'
  } finally {
    loading.value = false
  }
}

async function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // Reset input so same file can be selected again
  input.value = ''

  uploading.value = true
  error.value = null
  try {
    const attachment = await attachmentsApi.upload(props.todoId, file)
    attachments.value.push(attachment)
  } catch (err: any) {
    if (err?.data?.detail) {
      const detail = err.data.detail
      if (Array.isArray(detail)) {
        error.value = detail.map((d: any) => d.message).join(', ')
      } else {
        error.value = detail
      }
    } else {
      error.value = 'Failed to upload image'
    }
  } finally {
    uploading.value = false
  }
}

async function handleDelete(attachmentId: string) {
  try {
    await attachmentsApi.delete(props.todoId, attachmentId)
    attachments.value = attachments.value.filter(a => a.id !== attachmentId)
  } catch (err: any) {
    error.value = 'Failed to delete attachment'
  }
}

// Fetch attachments when expanded
watch(expanded, (val) => {
  if (val && attachments.value.length === 0) {
    fetchAttachments()
  }
})
</script>
