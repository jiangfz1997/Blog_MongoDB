<template>
  <DefaultLayout>
    <template #main>
      <div class="bg-white rounded-lg p-10 shadow-sm border border-gray-200">
        <h1 class="text-3xl font-bold mb-4">{{ post.title }}</h1>
        <div class="flex items-center justify-between mb-6 text-gray-500 text-sm">
          <div class="flex items-center space-x-4">
            <router-link 
              v-if="post.author_id"
              :to="`/user/${post.author_id}`" 
              class="font-medium text-gray-700 hover:underline cursor-pointer"
            >
              by {{ post.author }}
            </router-link>

            <span v-else class="font-medium text-gray-700">
              by {{ post.author }}
            </span>           
            <span>{{ formatDate(post.createdAt) }}</span>
          </div>

          <div class="flex items-center space-x-6">
            <div class="flex items-center space-x-1" title="Views">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <span>{{ post.viewCount }}</span>
            </div>

            <button 
              @click="handleLike"
              class="group flex items-center space-x-2 transition-all duration-200 active:scale-95"
              :class="post.isLiked ? 'text-red-500' : 'text-gray-400 hover:text-red-500'"
              title="Like this post"
            >
              <div class="p-2 rounded-full group-hover:bg-red-50 transition-colors">
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="w-8 h-8 transform transition-transform duration-300 group-hover:scale-110" 
                  viewBox="0 0 24 24" 
                  :fill="post.isLiked ? 'currentColor' : 'none'" 
                  stroke="currentColor" 
                  stroke-width="2" 
                  stroke-linecap="round" 
                  stroke-linejoin="round"
                >
                  <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
                </svg>
              </div>
              
              <span class="text-xl font-semibold">{{ post.likeCount }}</span>
            </button>
          </div>
        </div>
        <div class="border-t border-gray-200 my-2 pt-4">
        <MdPreview 
          editorId="preview-only" 
          :modelValue="post.content" 
          previewTheme="github" 
        />
        </div>
        <CommentSection v-if="post.id" :blogId="post.id" />
      </div>
    </template>

    <template #right>
        <AuthorProfile
        :name="author.name"
        :bio="author.bio"
        :avatar_url="author.avatar_url"
      />
       <AuthorMorePosts :author="author.name" :posts="morePosts" />
    </template>
  </DefaultLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getBlog, toggleLikeBlog, getBlogListByUserId } from '@/api/blog.js'
import { getUserProfile } from '@/api/user.js'
import { MdPreview } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AuthorProfile from '@/components/blogDetail/AuthorProfile.vue'
import AuthorMorePosts from '@/components/blogDetail/AuthorMorePosts.vue'
import CommentSection from '@/components/blogDetail/CommentSection.vue'
import { useMessage } from 'naive-ui'
const message = useMessage()
const route = useRoute()
const post = ref({})
const author = ref({})
const morePosts = ref([])
watch(
  () => route.params.id,
  (newId) => {
    if (newId) fetchBlogDetail()
  }
)
onMounted(async () => {
  const blogId = route.params.id
  if (blogId) {
    await fetchBlogDetail()
  }
  
})
const fetchBlogDetail = async () => {
  const id = route.params.id
  const blogData = await getBlog(id)
  console.log('Loaded blog data:', blogData)
  
  post.value = {
    id: blogData.id,
    title: blogData.title,
    author: blogData.author_username,
    author_id: blogData.author_id,
    content: blogData.content,
    viewCount: blogData.view_count,
    likeCount: blogData.like_count,
    isLiked: blogData.is_liked,
    createdAt: blogData.created_at
  }
  console.log('Post data set to:', post.value)
  const authorData = await getUserProfile(blogData.author_id)
  console.log('Loaded author data:', authorData)
  author.value = {
    name: authorData.username,
    bio: authorData.bio,
    avatar_url: authorData.avatar_url
  }
  console.log('Author data set to:', author.value)
  morePosts.value = await getBlogListByUserId(blogData.author_id, 1, 5, blogData.id)

}


const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const handleLike = async () => {
  if (!post.value.id) return


  const previousIsLiked = post.value.isLiked
  const previousCount = post.value.likeCount
  
  post.value.isLiked = !previousIsLiked
  post.value.likeCount = post.value.isLiked 
    ? previousCount + 1 
    : previousCount - 1

  try {
    const res = await toggleLikeBlog(post.value.id)
    

    if (res) {
      post.value.isLiked = res.is_liked
      post.value.likeCount = res.like_count
    }
  } catch (error) {
    if (error.response && error.response.status === 401) {
       message.warning('Login required to like posts')
    } else {
       console.error('Like failed', error)
       message.error(`Operation failed, please try again later (${error.message})`)
    }
    post.value.isLiked = previousIsLiked
    post.value.likeCount = previousCount
  }
}
</script>
