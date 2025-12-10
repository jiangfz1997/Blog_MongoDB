<template>
  <DefaultLayout>
    <template #main>
      <div class="max-w-7xl mx-auto">
        
        <div class="bg-white rounded-lg p-6 border border-gray-200 shadow-sm mb-6">
          <h1 class="text-2xl font-bold text-gray-800 mb-4">
            Search results for 
            <span class="text-blue-600">{{ currentKeyword || '...' }}</span>
          </h1>

          <n-input-group>
            <n-input 
              v-model:value="searchInput" 
              :placeholder="searchPlaceholder" 
              size="large"
              @keyup.enter="triggerSearch"
              clearable 
            >
              <template #prefix>🔍</template>
            </n-input>
            <n-button type="primary" size="large" @click="triggerSearch">
              Search
            </n-button>
          </n-input-group>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 min-h-[600px]">
          
          <div class="md:col-span-1">
            <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden sticky top-4">
              <div class="p-4 bg-gray-50 border-b border-gray-200 font-semibold text-gray-700">
                Filter by Type
              </div>
              <nav class="flex flex-col p-2 space-y-1">
                <button 
                  @click="switchType('posts')"
                  :class="[
                    'flex items-center w-full px-4 py-3 text-sm font-medium rounded-md transition-colors',
                    currentType === 'posts' 
                      ? 'bg-blue-50 text-blue-700 border border-blue-100' 
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  ]"
                >
                  <span class="mr-3">📄</span> Posts
                  <n-badge :value="total" :max="99" type="info" class="ml-auto" v-if="currentType === 'posts' && !loading" />
                </button>

                <button 
                  @click="switchType('people')"
                  :class="[
                    'flex items-center w-full px-4 py-3 text-sm font-medium rounded-md transition-colors',
                    currentType === 'people' 
                      ? 'bg-blue-50 text-blue-700 border border-blue-100' 
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  ]"
                >
                  <span class="mr-3">👥</span> People
                  <n-badge :value="userTotal" :max="99" type="info" class="ml-auto" v-if="currentType === 'people' && !userLoading" />
                </button>
              </nav>
            </div>
          </div>

          <div class="md:col-span-3 bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
            
            <div v-if="currentType === 'posts' && hasActiveFilters" class="flex flex-wrap items-center gap-2 mb-6 pb-4 border-b border-gray-100">
              <span class="text-xs text-gray-500 mr-1 uppercase tracking-wide font-bold">Filters:</span>
              
              <n-tag v-if="currentKeyword" closable type="info" size="small" @close="removeKeyword">
                Keyword: {{ currentKeyword }}
              </n-tag>

              <n-tag 
                v-for="tag in selectedTags" 
                :key="tag" 
                closable 
                type="success" 
                size="small" 
                @close="removeTag(tag)"
              >
                Tag: {{ tag }}
              </n-tag>

              <n-button text type="error" size="tiny" class="ml-2 underline" @click="clearAllFilters">
                Clear All
              </n-button>
            </div>

            <div v-if="loading || userLoading" class="py-20 flex justify-center">
              <n-spin size="large" :description="`Searching ${currentType}...`" />
            </div>

            <div v-else>
              
              <template v-if="currentType === 'posts'">
                <div v-if="results.length > 0" class="space-y-6">
                  <ArticleCard v-for="post in results" :key="post.id" :post="post" />
                </div>
                <n-empty v-else description="No posts found" class="py-12" />
              </template>

              <template v-if="currentType === 'people'">
                <div v-if="userResults.length > 0" class="space-y-4">
                  <UserProfileCard v-for="user in userResults" :key="user.user_id" :user="user" />
                </div>
                <n-empty v-else description="No authors found" class="py-12">
                   <template #extra>
                    <span class="text-gray-400 text-sm">Try searching for a different username.</span>
                  </template>
                </n-empty>
              </template>

              <div v-if="(currentType === 'posts' && total > 0) || (currentType === 'people' && userTotal > 0)" class="flex justify-center mt-10 pt-6 border-t border-gray-100">
                <n-pagination
                  v-model:page="currentPage"
                  :item-count="currentType === 'posts' ? total : userTotal"
                  :page-size="pageSize"
                  :on-update:page="handlePageChange"
                />
              </div>

            </div>
          </div>
        </div>

      </div>
    </template>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import ArticleCard from '@/components/card/ArticleCard.vue'
import UserProfileCard from '@/components/card/UserProfileCard.vue' 
import { useSearch } from '@/composables/useSearch'
import { searchUserbyUsername } from '@/api/user.js'
import { NInput, NInputGroup, NButton, NSpin, NPagination, NEmpty, NTag, NBadge } from 'naive-ui'

const route = useRoute()
const router = useRouter()

const searchInput = ref('')
const selectedTags = ref([])

const currentType = computed(() => route.query.type || 'posts')
const currentKeyword = computed(() => route.query.q || '')

const { results, total, loading, pageSize, executeSearch } = useSearch()

const userResults = ref([])
const userTotal = ref(0)
const userLoading = ref(false)

const searchPlaceholder = computed(() => {
  return currentType.value === 'people' 
    ? "Search for authors by username..."
    : "Type keyword or tag (e.g. '#python')..."
})

const hasActiveFilters = computed(() => {
  return (!!currentKeyword.value || selectedTags.value.length > 0) && currentType.value === 'posts'
})

const currentPage = computed({
  get: () => Number(route.query.page) || 1,
  set: (val) => handlePageChange(val)
})


const switchType = (type) => {
  if (currentType.value === type) return
  
  const query = {
    ...route.query,
    type: type,
    page: 1
  }
  
  if (type === 'people') {
    delete query.tags
  }

  router.push({ query })
}

const triggerSearch = () => {
  const val = searchInput.value.trim()
  
  let newTags = currentType.value === 'posts' ? [...selectedTags.value] : [] 
  let newKeyword = route.query.q || ''

  if (val.startsWith('#') && currentType.value === 'posts') {
    const tagName = val.slice(1).trim()
    if (tagName && !newTags.includes(tagName)) {
      newTags.push(tagName)
    }
  } else {
    newKeyword = val 
  }

  router.push({ 
    query: { 
      ...route.query,
      q: newKeyword || undefined, 
      tags: newTags.length ? newTags : undefined,           
      page: 1                  
    } 
  })
}

const performSearchFromRoute = async () => {
  const q = route.query.q || ''
  const page = Number(route.query.page) || 1
  const size = Number(route.query.size) || 10
  const type = route.query.type || 'posts'
  
  let tags = [];
  const rawTags = route.query.tags;
  if (Array.isArray(rawTags)) tags = rawTags;
  else if (rawTags) tags = [rawTags];
  
  searchInput.value = q
  selectedTags.value = tags

  if (type === 'posts') {
    await executeSearch({ q, tags, page, size })
  } else if (type === 'people') {
    await fetchUsers({ q, page, size })
  }
}


const fetchUsers = async ({ q, page, size }) => {
  userLoading.value = true
  try {
    const res = await searchUserbyUsername(q, page, size)
    console.log(`Searching users for: ${q}`)
    console.log('User search results:', res)
    userResults.value = res.users || []
    userTotal.value = res.total || 0
  } catch (error) {
    console.error('Failed to search users:', error)
  } finally {
    userLoading.value = false
  }
}

const removeKeyword = () => {
  searchInput.value = ''
  router.push({ query: { ...route.query, q: undefined, page: 1 } })
}

const removeTag = (tagToRemove) => {
  const newTags = selectedTags.value.filter(t => t !== tagToRemove)
  router.push({ query: { ...route.query, tags: newTags, page: 1 } })
}

const clearAllFilters = () => {
  searchInput.value = ''
  router.push({ 
    query: { 
      type: currentType.value, 
      size: 10 
    } 
  })
}

const handlePageChange = (newPage) => {
  router.push({ query: { ...route.query, page: newPage } })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => performSearchFromRoute())
watch(() => route.query, () => performSearchFromRoute())
</script>