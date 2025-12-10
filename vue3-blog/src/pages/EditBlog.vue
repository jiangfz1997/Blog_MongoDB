<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    
    <header class="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-gray-200 shadow-sm">
      <div class="w-full max-w-[1920px] mx-auto px-6 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <n-button text @click="router.push('/')" class="text-gray-500 hover:text-gray-800">
            <template #icon>←</template>
            Back
          </n-button>
          <div class="h-4 w-px bg-gray-300 mx-2"></div>
          <span class="text-lg">📝</span>
          <span class="font-semibold text-gray-700">{{ isEditing ? 'Editing Post' : 'New Draft' }}</span>
        </div>

        <div class="flex gap-3">
          <span v-if="loading" class="text-xs text-gray-400 flex items-center mr-2">Saving...</span>
          <!-- <n-button @click="saveDraft" secondary size="medium">Save draft</n-button> -->
          <n-button type="primary" @click="publish" :loading="loading" size="medium">Publish</n-button>
        </div>
      </div>
    </header>

    <main class="flex-1 w-full max-w-screen-2xl mx-auto px-6 py-8">
      
      <div class="mb-6 max-w-4xl text-[30px]"> <input
          v-model="title"
          type="text"
          placeholder="Enter your post title..."
          class="w-full text-9xl font-extrabold text-gray-900 placeholder:text-gray-300 bg-transparent border-none outline-none p-0 focus:ring-0 leading-tight"
        />
      </div>

      <div class="mb-6">
         <n-dynamic-tags v-model:value="tags" :max="6" size="large" />
      </div>

      <div class="bg-white border border-gray-200 rounded-xl shadow-sm editor-wrapper">
        <MdEditor 
          v-model="content" 
          language="en-US"
          :preview="true"
          :toolbarsExclude="['github', 'save']"
          class="custom-editor" 
          previewTheme="github"
          :style="{ height: 'calc(100vh - 250px)' }" 
        />
        </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { updateBlog, publishBlog } from '@/api/blog' 
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { NInput, NButton, NDynamicTags } from 'naive-ui'
import { getBlog } from '@/api/blog'

const route = useRoute()
const router = useRouter()
const message = useMessage() 
const isEditing = ref(!!route.params.id)
const loading = ref(false)
const title = ref('')
const content = ref('')
const tags = ref([]) 

onMounted(async () => {
  if (isEditing.value) {

    const id = route.params.id

    try {
      const blogData = await getBlog(id)      
      title.value = blogData.title
      content.value = blogData.content
      tags.value = blogData.tags || []
    } catch (e) {
      message.error('Failed to load blog data')
    }

  } else {
    const draft = localStorage.getItem('blog-draft')
    if (draft) {
      const confirmLoad = confirm('Found a draft. Do you want to load it?')
      if (confirmLoad) {
        const d = JSON.parse(draft)
        title.value = d.title
        content.value = d.content
        tags.value = d.tags || []
      }
    }
  }
})


function saveDraft() {
  localStorage.setItem('blog-draft', JSON.stringify({
    title: title.value,
    content: content.value,
    tags: tags.value,
  }))
  message.success('Draft saved locally')
}


const publish = async () => {

  const trimmedTitle = title.value.trim()
  const trimmedContent = content.value.trim()

  if (!trimmedTitle) {
    return message.warning('Title is required')
  }
  if (trimmedTitle.length < 3 || trimmedTitle.length > 80) {
    return message.warning('Title must be between 3 and 80 characters')
  }

  if (!trimmedContent) {
    return message.warning('Content is required')
  }
  if (trimmedContent.length < 10) {
    return message.warning('Content must be at least 10 characters')
  }
  loading.value = true
  const blogData = {
    title: title.value,
    content: content.value,
    tags: tags.value,
  }

  try {
    let res;
    if (isEditing.value) {
      res = await updateBlog(route.params.id, blogData)

    } else {
      res = await publishBlog(blogData)
    }
    message.success(isEditing.value ? 'Updated successfully!' : 'Published successfully!')
    localStorage.removeItem('blog-draft')
    const newId = res?.id || route.params.id 
    router.push(`/blog/${newId}`)

  } catch (e) {
    console.error(e)
    message.error(`Operation failed (${e.message})`)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
:deep(.md-editor) {
  background-color: #ffffff !important;
  border: none !important;
  border-radius: 12px;
}

:deep(.md-editor-toolbar-wrapper) {
  border-bottom: 1px solid #f3f4f6 !important;
  padding: 6px 12px !important;
}

:deep(.md-editor-fullscreen) {
  z-index: 9999 !important;
  top: 0 !important;
}

:deep(.md-editor-content) {
  background-color: transparent !important;
}
</style>