<template>
  <n-card 
    :title="post.title" 
    hoverable 
    class="cursor-pointer h-full" 
    @click="goToDetail"
  >
    
    <template #header-extra>
      <span class="text-xs text-gray-400">{{ formatDate(post.created_at) }}</span>
    </template>

    <n-space size="small" class="mb-4">
      <n-tag 
        v-for="tag in post.tags" 
        :key="tag" 
        type="info" 
        size="small" 
        bordered
      >
        #{{ tag }}
      </n-tag>
    </n-space>

    <!-- <p class="text-gray-500 text-sm line-clamp-3 mb-4">
       {{ getSummary(post.content) }}
    </p> -->

    <template #footer>
      <div class="flex justify-between items-center">
        
        <div class="flex items-center gap-2">
          <n-avatar 
            round 
            size="small" 
            :src="post.avatar_url" 
          />
          <span class="text-sm text-gray-600">{{ post.author_username }}</span>
        </div>

        <n-space size="medium">
          <span class="text-xs text-gray-400 flex items-center gap-1">
            👁️ {{ post.views || 0 }}
          </span>
          <span class="text-xs text-gray-400 flex items-center gap-1">
            💬 {{ post.comments_count || 0 }}
          </span>
          <span class="text-xs text-gray-400 flex items-center gap-1">
            ❤️ {{ post.like_count || 0 }}
          </span>
        </n-space>
      </div>
    </template>
  </n-card>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { NCard, NTag, NSpace, NAvatar } from 'naive-ui'
import { onMounted } from 'vue'

const props = defineProps({
  post: { type: Object, required: true }
})

const router = useRouter()
const goToDetail = () => router.push(`/blog/${props.post.id}`)

const formatDate = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const getSummary = (content) => {
  if (!content) return ''
  const text = content.replace(/<[^>]+>/g, '')
  return text.length > 100 ? text.substring(0, 100) + '...' : text
}


const mounted = onMounted(() => {
  console.log('ArticleCard mounted with post:', props.post)
})
</script>