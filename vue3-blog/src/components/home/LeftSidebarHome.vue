<template>
  <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
    <h2 class="font-bold text-gray-800 text-lg mb-4 flex items-center gap-2">
      🔥 Trending Tags
    </h2>

    <div v-if="loading" class="space-y-3 animate-pulse">
      <div class="h-4 bg-gray-100 rounded w-3/4"></div>
      <div class="h-4 bg-gray-100 rounded w-1/2"></div>
      <div class="h-4 bg-gray-100 rounded w-5/6"></div>
    </div>

    <ul v-else class="space-y-1">
      <li 
        v-for="item in tags" 
        :key="item.tag" 
        class="flex items-center justify-between group cursor-pointer p-2 rounded-md hover:bg-blue-50 transition-colors"
        @click="searchTag(item.tag)"
      >
        <span class="text-gray-600 font-medium group-hover:text-blue-600 transition-colors">
          # {{ item.tag }}
        </span>
        
        <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
          {{ item.blog_count }}
        </span>
      </li>
    </ul>
    
    <div v-if="!loading && tags.length === 0" class="text-sm text-gray-400 italic">
      No tags yet.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHotTags } from '@/api/blog'
const tags = ref([])
const loading = ref(false)
const router = useRouter()

const fetchHotTags = async () => {
  loading.value = true
  try {
    const data = await getHotTags()
    console.log('Fetched hot tags:', data)
    tags.value = data || []
  } catch (error) {
    console.error('Failed to fetch hot tags:', error)
  } finally {
    loading.value = false
  }
}

function searchTag(tagName) {
  console.log('Searching for tag:', tagName)
  router.push({ 
    path: '/search', 
    query: { tags: [tagName] } 
  })
}

onMounted(() => {
  fetchHotTags()
})
</script>
