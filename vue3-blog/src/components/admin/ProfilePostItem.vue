<template>
  <div class="flex items-center justify-between p-5 bg-white border border-gray-200 rounded-lg hover:shadow-md hover:border-blue-300 transition-all duration-300 group">
    
    <div class="flex-1 min-w-0 mr-6">
      
      <div class="flex items-center gap-3 mb-2">
        <h3 
          class="text-lg font-semibold text-gray-800 truncate cursor-pointer hover:text-blue-600 transition-colors"
          @click="goToDetail"
        >
          {{ post.title }}
        </h3>
        </div>

      <div class="mb-3">
        <n-space size="small">
          <span v-if="!post.tags || post.tags.length === 0" class="text-xs text-gray-400">
            No tags
          </span>
          
          <n-tag 
            v-for="tag in post.tags" 
            :key="tag" 
            type="info" 
            size="small" 
            bordered
            class="opacity-90"
          >
            # {{ tag }}
          </n-tag>
        </n-space>
      </div>
      
      <div class="flex items-center gap-4 text-xs text-gray-400">
        <span>{{ formatDate(post.created_at) }}</span>
        
        <span class="w-[1px] h-3 bg-gray-300"></span> <span class="flex items-center gap-1">
          👁️ {{ post.view_count || 0 }}
        </span>
        <span class="flex items-center gap-1">
           ❤️ {{ post.like_count || 0 }}
        </span>
        <span class="flex items-center gap-1">
          💬 {{ post.comment_count || 0 }}
        </span>
      </div>
    </div>

    <div v-if="showActions" class="flex items-center gap-3 shrink-0">
      
      <n-button 
        size="small" 
        secondary 
        type="primary" 
        @click.stop="$emit('edit', post.id)"
      >
        Edit
      </n-button>

      <n-popconfirm
        @positive-click="handleDelete"
        negative-text="Cancel"
        positive-text="Confirm"
      >
        <template #trigger>
          <n-button 
            size="small" 
            secondary 
            type="error" 
            @click.stop
          >
            Delete
          </n-button>
        </template>
        Are you sure you want to delete this post?
      </n-popconfirm>

    </div>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { NTag, NSpace, NButton, NPopconfirm } from 'naive-ui'

const props = defineProps({
  post: { type: Object, required: true },
  showActions: { type: Boolean, default: false }
})

const emit = defineEmits(['edit', 'delete'])
const router = useRouter()

const goToDetail = () => {
  router.push(`/blog/${props.post.id}`)
}

const handleDelete = () => {
  emit('delete', props.post.id)
}


const formatDate = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}
</script>