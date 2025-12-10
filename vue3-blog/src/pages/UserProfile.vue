<template>
  <DefaultLayout>
    <template #main>
      <div class="max-w-4xl mx-auto pb-20 px-4 sm:px-6">
        
        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden mb-6 relative z-0">
          
          <div class="h-32 md:h-48 bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400"></div>

          <div class="px-6 md:px-8 pb-6">
            <div class="flex justify-between items-end -mt-12 mb-4">
              <div class="relative">
                <img
                  :src="currentUser.avatar || 'https://api.dicebear.com/9.x/adventurer/svg?seed=Default'"
                  class="w-24 h-24 md:w-32 md:h-32 rounded-full object-cover border-4 border-white shadow-md bg-white"
                />
              </div>

              <button 
                v-if="isOwner"
                @click="showEditModal = true"
                class="mb-2 px-5 py-2 rounded-full border border-gray-300 font-semibold text-gray-700 hover:bg-gray-50 transition-all shadow-sm active:scale-95 bg-white"
              >
                Edit Profile
              </button>
            </div>

            <div>
              <h1 class="text-2xl md:text-3xl font-bold text-gray-900">
                {{ currentUser.username }}
              </h1>
              <p class="text-gray-500 mt-2 text-base md:text-lg max-w-2xl leading-relaxed">
                {{ currentUser.bio || 'No bio yet.' }}
              </p>
              
              <div class="flex items-center gap-6 mt-4 text-sm text-gray-600">
                <div class="flex items-center gap-1">
                  <span class="font-bold text-gray-900">{{ totalPosts }}</span> Posts
                </div>
                <!-- <div class="flex items-center gap-1 text-gray-400">
                  <span>📅 Joined recently</span>
                </div> -->
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 min-h-[400px]">
          
          <div class="border-b border-gray-100 px-6 flex items-center gap-8">
            <button class="py-4 border-b-2 border-blue-500 text-blue-600 font-medium text-sm">
              My Posts
            </button>
            <button class="py-4 border-b-2 border-transparent text-gray-400 hover:text-gray-600 font-medium text-sm transition-colors">
              Likes
            </button>
          </div>

          <div v-if="blogs.length > 0">
            <div class="divide-y divide-gray-100">
              <ProfilePostItem 
                v-for="post in blogs" 
                :key="post.id" 
                :post="post"
                :show-actions="isOwner" 
                @edit="handleEdit"
                @delete="handleDelete"
                class="p-6 hover:bg-gray-50 transition-colors" 
              />
              </div>
            
            <div class="p-6 border-t border-gray-100 flex justify-center">
              <NPagination
                v-model:page="page"
                :page-size="pageSize"
                :item-count="totalPosts"
                :page-count="totalPages"
                @update:page="loadBlogs"
              />
            </div>
          </div>

          <div v-else class="py-20 text-center text-gray-400">
             <div class="text-4xl mb-3">📭</div>
             <p>No posts published yet.</p>
          </div>
        </div>

        <EditProfileModal 
          v-if="showEditModal"
          :user="currentUser"
          @close="showEditModal = false"
          @updated="handleProfileUpdate"
        />

      </div>
    </template>
  </DefaultLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NPagination } from "naive-ui"


import DefaultLayout from '@/layouts/DefaultLayout.vue'
import ProfilePostItem from '@/components/admin/ProfilePostItem.vue'
import EditProfileModal from '@/components/user/EditProfileModal.vue' 


import { useUserStore } from '@/store/userStore'
import { getUserProfile } from '@/api/user.js'
import { getBlogListByUserId, deleteBlog } from '@/api/blog.js'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const targetUserId = route.params.userid 

const currentUser = ref({
  id: '',
  username: 'Loading...',
  avatar: '',
  bio: ''
})

const blogs = ref([])
const page = ref(1)
const pageSize = ref(10)
const totalPosts = ref(0)
const totalPages = ref(0)


const showEditModal = ref(false)

const isOwner = computed(() => {
  console.log("Comparing user IDs:", userStore.user?.id, targetUserId)
  return userStore.user?.id && String(userStore.user.id) === String(targetUserId)
})


onMounted(async () => {
  if (!targetUserId) {
    console.error("No user ID found in route")
    return
  }
  
  await Promise.all([
    fetchUserInfo(),
    loadBlogs()
  ])
})


const fetchUserInfo = async () => {
  try {
    const data = await getUserProfile(targetUserId)
    console.log("Fetched user profile data:", data)
    currentUser.value = {
      id: data.id || data._id, 
      username: data.username,
      avatar: data.avatar || data.avatar_url || `https://api.dicebear.com/9.x/adventurer/svg?seed=${data.username}`,
      bio: data.bio || ''
    }
    console.log("Loaded user profile:", currentUser.value)
    console.log("Target User ID:", targetUserId)
    console.log("Is Owner:", isOwner.value)
  } catch (error) {
    console.error("Failed to fetch user profile", error)
  }
}

const loadBlogs = async () => {
  try {
    const data = await getBlogListByUserId(targetUserId, page.value, pageSize.value)
    blogs.value = data.items || [] 
    totalPosts.value = data.total || 0
    totalPages.value = Math.ceil((data.total || 0) / pageSize.value)
  } catch (error) {
    console.error("Failed to load blogs", error)
  }
}

const handleProfileUpdate = async(updatedForm) => {
  await fetchUserInfo()
}

const handleEdit = (id) => {
  router.push(`/blog/edit/${id}`)
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this post?')) return
  
  try {
    await deleteBlog(id)

    await loadBlogs()
  } catch (error) {
    console.error(error)
    alert('Failed to delete post')
  }
}
</script>
