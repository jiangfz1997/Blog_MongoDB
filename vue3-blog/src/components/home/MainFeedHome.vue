<template>
  <div class="space-y-4">
  <div class="flex items-center gap-2 mb-6 px-1">
      <div class="p-2 bg-orange-100 rounded-full text-orange-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.298-2.296a1 1 0 00-1.648-1.052c-.862 1.363-.71 3.088.41 4.568.966 1.273 2.529 2.461 4.312 2.461 1.86 0 3.642-1.284 4.14-3.123.636-2.346.225-5.228-2.118-7.416z" clip-rule="evenodd" />
        </svg>
      </div>
      <div>
        <h2 class="text-xl font-bold text-gray-800">Discover Trending</h2>
        <p class="text-xs text-gray-500 font-medium">Top stories picked for you</p>
      </div>
    </div>
    <PostCard
      v-for="post in posts"
      :key="post.id" 
      :id="post.id"
      :title="post.title"
      :author="post.author"
      :tags="post.tags"
      :date="post.date"
      :viewCount="post.viewCount"
      :likeCount="post.likeCount"
      :avatar_url="post.avatar_url"
      :comment_count="post.comment_count"
      :isLiked="post.isLiked"
    />
    
    <div class="text-center py-4">
      <div v-if="loading" class="text-gray-400 text-sm">Loading...</div>
      
      <button 
        v-else-if="hasMore" 
        @click="loadMore"
        class="text-blue-500 hover:text-blue-700 text-sm font-medium px-4 py-2"
      >
        Load More Posts
      </button>
      
      <div v-else class="text-gray-400 text-sm">No more posts</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDiscoverFeed } from '@/api/blog.js' 
import PostCard from '@/components/PostCard.vue'

const posts = ref([])
const page = ref(1)
const pageSize = 5
const loading = ref(false)
const hasMore = ref(true)

const fetchPosts = async () => {
  if (loading.value) return
  loading.value = true

  try {
    const res = await getDiscoverFeed(page.value, pageSize)
    

    const newItems = res.blogs?.items || [] 

    const mappedItems = newItems.map(item => ({
      id: item.blog_id,             
      title: item.title,
      author: item.author_username, 
      avatar_url: item.avatar_url || '',
      tags: item.tags || [],
      date: item.created_at,        
      viewCount: item.view_count || 0,
      likeCount: item.like_count || 0, 
      isLiked: item.is_liked || false,
      comment_count: item.comment_count || 0
    }))

    posts.value.push(...mappedItems)
    console.log('Loaded posts:', posts.value)
    if (newItems.length < pageSize) {
      hasMore.value = false
    }
    
  } catch (error) {
    console.error('Failed to load discover feed:', error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  page.value++
  fetchPosts()
}

onMounted(() => {
  fetchPosts()
})
</script>