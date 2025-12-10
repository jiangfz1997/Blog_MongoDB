<template>
  <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
    <h2 class="font-bold text-gray-800 text-lg mb-4 flex items-center gap-2">
      📈 Top viewed Posts
    </h2>

    <div v-if="loading" class="space-y-4">
      <div v-for="n in 5" :key="n" class="flex items-center gap-3 animate-pulse">
        <div class="w-4 h-4 bg-gray-100 rounded"></div>
        <div class="flex-1">
          <div class="h-4 bg-gray-100 rounded w-3/4 mb-1"></div>
          <div class="h-3 bg-gray-50 rounded w-1/4"></div>
        </div>
      </div>
    </div>

    <ul v-else class="space-y-3">
      <li 
        v-for="(blog, index) in trends" 
        :key="blog.id" 
        class="flex items-start gap-3 group cursor-pointer"
        @click="goToDetail(blog.id)"
      >
        <span 
          class="text-sm font-bold mt-0.5 w-4 text-center"
          :class="{
            'text-yellow-500': index === 0,
            'text-gray-400': index === 1,
            'text-orange-400': index === 2,
            'text-gray-300': index > 2
          }"
        >
          {{ index + 1 }}
        </span>

        <div class="flex-1 min-w-0">
          <h3 class="text-sm text-gray-700 font-medium group-hover:text-blue-600 transition-colors line-clamp-2 leading-snug">
            {{ blog.title }}
          </h3>
          
          <div class="flex items-center gap-1 mt-1 text-xs text-gray-400">
            <span>👁️ {{ blog.view_count }} reads</span>
            <span>·</span>
            <span>{{ formatDate(blog.created_at) }}</span>
          </div>
        </div>
      </li>
    </ul>

    <div v-if="!loading && trends.length === 0" class="text-sm text-gray-400 italic">
      No trending posts yet.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getHotViewedBlogs } from '@/api/blog'
import { useRouter } from 'vue-router'
const router = useRouter()
const loading = ref(false)
const trends = ref([])


const fetchHotBlogs = async () => {
  loading.value = true
  try {
    const data = await getHotViewedBlogs(10)
    trends.value = data
  } catch (error) {
    console.error('Failed to fetch hot blogs:', error)
  } finally {
    loading.value = false
  }
}
function goToDetail(blogId) {
  router.push(`/blog/${blogId}`)
}
function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

onMounted(async () => {
  fetchHotBlogs()
})

</script>
