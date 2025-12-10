<template>
  <div 
    class="group bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer"
    @click="getBlogDetail"
  >
    <div class="flex items-center mb-3">
      <img 
        v-if="avatar_url" 
        :src="avatar_url" 
        alt="User Avatar"
        class="w-8 h-8 rounded-full object-cover mr-2"
      >

      <div 
          v-else
          class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-sm mr-2">
          {{ author ? author.charAt(0).toUpperCase() : 'U' }}
      </div>
      <div class="flex flex-col">
        <span class="text-sm font-medium text-gray-800 leading-none mb-1">
          {{ author || 'Anonymous' }}
        </span>
        <span class="text-xs text-gray-500">
          {{ formattedDate }}
        </span>
      </div>
    </div>

    <div class="mb-3">
      <h3 class="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors leading-tight">
        {{ title }}
      </h3>
    </div>

    <div class="flex flex-wrap gap-2 mb-4">
      <span
        v-for="tag in tags"
        :key="tag"
        class="text-xs text-gray-600 hover:text-black hover:bg-gray-100 px-1 py-0.5 rounded transition-colors"
      >
        #{{ tag }}
      </span>
    </div>

    <div class="flex items-center justify-between pt-2 border-t border-gray-50">
      <div class="flex items-center space-x-6">
        <div class="flex items-center space-x-1.5 text-sm text-gray-500 group/like">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            class="w-5 h-5 transition-transform group-hover/like:scale-110" 
            :class="isLiked ? 'text-red-500 fill-current' : 'text-gray-400'"
            viewBox="0 0 24 24" 
            stroke="currentColor" 
            stroke-width="2" 
            fill="none" 
            stroke-linecap="round" 
            stroke-linejoin="round"
          >
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
          </svg>
          <span :class="isLiked ? 'text-gray-700 font-medium' : ''">
            {{ likeCount }} <span class="hidden sm:inline">Reactions</span>
          </span>
        </div>

        <div class="flex items-center space-x-1.5 text-sm text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          <span>{{ viewCount }} <span class="hidden sm:inline">Views</span></span>
        </div>

        <div class="flex items-center space-x-1.5 text-sm text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 8h2a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2h2"/>
            <rect x="7" y="12" width="10" height="8" rx="2" ry="2"/>
          </svg>
          <span>{{ comment_count }} <span class="hidden sm:inline">Comments</span></span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  id: {
    type: String, 
    required: true
  },
  title: {
    type: String,
    required: true
  },
  author: {
    type: String,
    default: 'Unknown'
  },
  avatar_url: {
    type: String,
    default: ''
  },
  tags: {
    type: Array,
    default: () => []
  },
  date: {
    type: String,
    default: ''
  },
  viewCount: {
    type: Number,
    default: 0
  },
  likeCount: {
    type: Number,
    default: 0
  },
  isLiked: {
    type: Boolean,
    default: false
  },
  comment_count: {
    type: Number,
    default: 0
  }
})


const formattedDate = computed(() => {
  if (!props.date) return ''
  const d = new Date(props.date)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
})



function getBlogDetail() {
  router.push(`/blog/${props.id}`)
}
</script>