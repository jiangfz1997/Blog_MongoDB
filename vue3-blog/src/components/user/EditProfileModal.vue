<template>
  <teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center px-4 sm:px-0">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" @click="close"></div>

      <div class="relative z-10 w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        <div class="px-6 py-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-800">Edit Profile</h3>
          <button @click="close" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <div class="p-6 space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">Choose Avatar</label>
            <div class="flex flex-wrap gap-3 justify-center p-4 bg-gray-50 rounded-xl border border-gray-100">
              <div 
                v-for="url in avatarOptions" 
                :key="url"
                @click="form.avatar = url"
                class="relative cursor-pointer transition-transform hover:scale-105 group"
              >
                <img 
                  :src="url" 
                  class="w-14 h-14 rounded-full border-2 transition-colors"
                  :class="form.avatar === url ? 'border-blue-500 ring-2 ring-blue-200' : 'border-transparent group-hover:border-gray-300'"
                />
                <div v-if="form.avatar === url" class="absolute -bottom-1 -right-1 bg-blue-500 text-white rounded-full p-0.5 border border-white shadow-sm">
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/></svg>
                </div>
              </div>
            </div>
          </div>

        <div class="relative">
            <label class="block text-sm font-medium text-gray-700 mb-1">User Name</label>

            <input 
            v-model="form.username"
            type="text" 
            @blur="validateUsername"
            class="w-full px-4 py-2 rounded-lg border outline-none transition-all"
            :class="[
                usernameError 
                ? 'border-red-500 focus:ring-2 focus:ring-red-100' 
                : 'border-gray-300 focus:ring-2 focus:ring-blue-100 focus:border-blue-500'
            ]"
            />
            
            <div v-if="checkingUsername" class="absolute right-3 top-2.5">
            <svg class="animate-spin h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            </div>
            <p v-if="usernameError" class="text-xs text-red-500 mt-1">
                {{ usernameError }}
            </p>
            <p v-else-if="!checkingUsername && form.username && form.username !== props.user.username && !usernameError" class="text-xs text-green-600 mt-1">
                Username is available
            </p>
        </div>

          <div>
             <label class="block text-sm font-medium text-gray-700 mb-1">Bio</label>
             <textarea 
                v-model="form.bio"
                rows="3"
                maxlength="160"
                class="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all resize-none"
                placeholder="Tell us about yourself..."
             ></textarea>
             <div class="text-right text-xs text-gray-400 mt-1">
                {{ form.bio?.length || 0 }}/160
             </div>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button 
              @click="close" 
              class="px-4 py-2 rounded-lg text-gray-600 hover:bg-gray-100 font-medium transition-colors"
            >
              Cancel
            </button>
            <button 
              @click="handleSave" 
              :disabled="loading"
              class="px-6 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-70 flex items-center gap-2 shadow-md hover:shadow-lg transition-all"
            >
              <span v-if="loading" class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></span>
              {{ loading ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>

        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/store/userStore' 
import { updateUserProfile, checkUsernameAvailability } from '@/api/user'
import { useMessage } from 'naive-ui'
const usernameError = ref('')
const checkingUsername = ref(false)
const props = defineProps({
  user: { type: Object, required: true } 
})

const emit = defineEmits(['close', 'updated']) 
const message = useMessage()
const store = useUserStore()
const loading = ref(false)

const form = reactive({
  username: '',
  bio: '',
  avatar: ''
})

const avatarOptions = [
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Felix',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Aneka',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Milo',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Lia',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Christopher',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Sophia',
]

onMounted(() => {
  form.username = props.user.username
  form.bio = props.user.bio || ''
  form.avatar = props.user.avatar || avatarOptions[0]
})

const close = () => {
  emit('close')
}
const validateUsername = async () => {
  usernameError.value = ''
  const val = form.username.trim()

  if (!val) {
    usernameError.value = 'Username cannot be empty'
    return false
  }

  if (val.length < 3) {
    usernameError.value = 'Username must be at least 3 characters'
    return false
  }

  if (val === props.user.username) {
    return true
  }

  checkingUsername.value = true
  try {
    const res = await checkUsernameAvailability(val)
    
    if (!res.is_available) {
      usernameError.value = 'Username is already taken'
      return false
    }
    return true 
  } catch (error) {
    console.error(error)
    usernameError.value = 'Unable to validate username'
    return false
  } finally {
    checkingUsername.value = false
  }
}
const handleSave = async () => {
  if (!form.username.trim()) {
    message.error('Username cannot be empty.')
    return
  }
  
  loading.value = true
  try {
    const newUserData =  {
        username: form.username,
        bio: form.bio,
        avatar_url: form.avatar
    }
    console.log('Updating profile with:', newUserData)
    const newUser = await updateUserProfile(newUserData)
    store.userInfo = { ...store.userInfo, ...newUser }

    message.success('Profile updated successfully!')
    console.log('Updated:', newUser)
    
    
    emit('updated', newUser) 
    close()
  } catch (error) {
    console.error('Update failed:', error)
    message.error(`Failed to update profile. Please try again. Reason: ${error.response.data.detail|| 'Unknown error'}`)
  } finally {
    loading.value = false
  }
}
</script>