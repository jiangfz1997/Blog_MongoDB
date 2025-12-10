<template>
  <div class="bg-white border border-gray-100 rounded-xl shadow-sm overflow-hidden">
    <div class="px-5 py-4 border-b border-gray-100 bg-gray-50/50">
      <h2 class="text-base font-bold text-gray-800 flex items-center">
        <span class="mr-2">📚</span> 
        More from {{ author }}
      </h2>
    </div>

    <div class="p-2">
      <div v-if="!postItems.length" class="text-center text-gray-400 py-4 text-sm">
        No other posts found.
      </div>

      <ul v-else class="space-y-1">
        <li
          v-for="post in postItems"
          :key="post.id"
          class="group flex flex-col p-3 rounded-lg cursor-pointer hover:bg-blue-50/50 transition-colors duration-200"
          @click.stop="goToDetail(post.id)"
        >
          <h3 class="text-sm font-semibold text-gray-700 group-hover:text-blue-600 transition-colors leading-snug mb-2 line-clamp-2">
            {{ post.title }}
          </h3>

          <div class="flex items-center text-xs text-gray-400 space-x-3">
            <span class="flex items-center">
              {{ formatDate(post.created_at) }}
            </span>

            <span class="w-0.5 h-0.5 bg-gray-300 rounded-full"></span>

            <span class="flex items-center hover:text-gray-600 transition-colors" title="Views">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {{ formatNumber(post.view_count) }}
            </span>

            <span 
              class="flex items-center transition-colors" 
              :class="post.comment_count > 0 ? 'text-blue-400 hover:text-blue-600' : 'hover:text-gray-600'"
              title="Comments"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              {{ post.comment_count || 0 }}
            </span>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { computed } from 'vue'

const props = defineProps({
  author: { type: String, required: true },
  posts: { 
    type: Object, 
    required: true,
    default: () => ({ items: [] }) 
  }
})

const router = useRouter()

const postItems = computed(() => {
  return props.posts?.items || []
})

const goToDetail = (id) => {
  console.log('Navigating to post detail:', id)
  router.push(`/blog/${id}`)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(date)
}

const formatNumber = (num) => {
  if (!num) return 0
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num
}
</script>