<template>
  <header class="sticky top-0 z-40 w-full bg-white/80 backdrop-blur-md border-b border-gray-100 transition-all duration-300">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 gap-4">
        
        <div class="flex-shrink-0 flex items-center cursor-pointer" @click="gotoHome">
          <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center mr-2 shadow-sm">
             <span class="text-white font-bold text-lg">B</span>
          </div>
          <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-800 to-gray-600 tracking-tight">
            DevBlog
          </h1>
        </div>

        <!-- <div class="hidden md:flex flex-1 max-w-md mx-4">
          <div class="relative w-full group">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search articles..."
              class="block w-full pl-10 pr-3 py-2 border-transparent bg-gray-100 text-gray-900 placeholder-gray-500 rounded-full leading-5 focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 sm:text-sm transition-all duration-200"
              @keyup.enter="handleSearch"
            />
            </div>
        </div> -->
        <div class="hidden md:flex flex-1 max-w-md mx-4">
  <div 
    class="relative w-full flex items-center bg-gray-100 rounded-full border border-transparent focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all duration-200"
  >
    
    <div class="relative" ref="searchTypeRef">
      <button 
        @click="toggleSearchType"
        type="button"
        class="flex items-center gap-1 pl-4 pr-2 py-2 text-sm font-medium text-gray-600 hover:text-blue-600 focus:outline-none"
      >
        <span>{{ searchType === 'posts' ? 'Article' : 'Author' }}</span>
        
        <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <transition
        enter-active-class="transition ease-out duration-100"
        enter-from-class="transform opacity-0 scale-95"
        enter-to-class="transform opacity-100 scale-100"
        leave-active-class="transition ease-in duration-75"
        leave-from-class="transform opacity-100 scale-100"
        leave-to-class="transform opacity-0 scale-95"
      >
        <div 
          v-if="searchTypeOpen"
          class="absolute top-full left-0 mt-2 w-28 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50 overflow-hidden"
        >
          <button 
            @click="selectSearchType('posts')"
            class="w-full text-left px-4 py-2 text-sm hover:bg-blue-50 text-gray-700 hover:text-blue-600 flex items-center justify-between"
          >
            Article
            <span v-if="searchType === 'posts'" class="text-blue-600">✓</span>
          </button>
          <button 
            @click="selectSearchType('people')"
            class="w-full text-left px-4 py-2 text-sm hover:bg-blue-50 text-gray-700 hover:text-blue-600 flex items-center justify-between"
          >
            Author
            <span v-if="searchType === 'people'" class="text-blue-600">✓</span>
          </button>
        </div>
      </transition>
    </div>

    <div class="w-px h-5 bg-gray-300 mx-1"></div>

    <div class="pl-2 text-gray-400">
        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
    </div>

    <input
      v-model="searchQuery"
      type="text"
      :placeholder="searchPlaceholder"
      class="block w-full pl-2 pr-4 py-2 bg-transparent border-none focus:ring-0 text-gray-900 placeholder-gray-500 sm:text-sm"
      @keyup.enter="handleSearch"
    />
  </div>
  
  <div v-if="searchTypeOpen" class="fixed inset-0 z-30" @click="searchTypeOpen = false"></div>
</div>

        <div class="flex items-center gap-3">
          
          <template v-if="!userStore.isLoggedIn">
            <button
              @click="openLogin"
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Log in
            </button>
            <button
              @click="openSignup"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full text-sm font-medium shadow-sm shadow-blue-500/30 transition-all hover:-translate-y-0.5"
            >
              Sign up
            </button>
          </template>

          <template v-else>
            <button
              @click="goWrite"
              class="hidden sm:flex items-center gap-1 text-gray-600 hover:text-blue-600 font-medium px-3 py-2 rounded-lg hover:bg-blue-50 transition-colors mr-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span>Write</span>
            </button>

            <div class="relative ml-3" ref="menuRef">
              <button
                @click="toggleMenu"
                class="flex items-center gap-2 focus:outline-none"
              >
                <div class="relative group">
                  <img
                    v-if="userStore.user?.avatar_url"
                    :src="userStore.user.avatar_url"
                    class="h-9 w-9 rounded-full object-cover border border-gray-200 group-hover:border-blue-400 transition-colors"
                    alt="User avatar"
                  />
                  <div
                    v-else
                    class="h-9 w-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm shadow-sm"
                  >
                    {{ userInitial }}
                  </div>
                  <span class="absolute bottom-0 right-0 block h-2.5 w-2.5 rounded-full ring-2 ring-white bg-green-400"></span>
                </div>
                <span class="hidden md:block text-sm font-medium text-gray-700">{{ userStore.displayName }}</span>
                <svg :class="{'rotate-180': menuOpen}" class="w-4 h-4 text-gray-400 transition-transform duration-200 hidden md:block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-if="menuOpen"
                  class="absolute right-0 mt-3 w-48 bg-white rounded-xl shadow-lg py-1 ring-1 ring-black ring-opacity-5 z-50 origin-top-right"
                >
                  <div class="px-4 py-3 border-b border-gray-100 md:hidden">
                    <p class="text-sm font-medium text-gray-900">{{ userStore.displayName }}</p>
                    <p class="text-xs text-gray-500 truncate">{{ userStore.user?.email }}</p>
                  </div>

                  <button
                    @click="goProfile"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Your Profile
                  </button>

                  <button
                    @click="goWrite"
                    class="md:hidden w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                  >
                     <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    Write a post
                  </button>
                  
                  <div class="border-t border-gray-100 my-1"></div>

                  <button
                    @click="handleLogout"
                    class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Sign out
                  </button>
                </div>
              </transition>
              
              <div v-if="menuOpen" class="fixed inset-0 z-40" @click="menuOpen = false"></div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <LoginModal v-if="showLogin" @close="showLogin = false" @success="onLoginSuccess" @switchToRegister="openSignup" /> 
    <RegisterModal v-if="showSignup" @close="showSignup = false" @success="onLoginSuccess" @switchToLogin="openLogin" />
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import LoginModal from './user/LoginModal.vue' 
import RegisterModal from './user/RegisterModal.vue' 

const router = useRouter()
const userStore = useUserStore()

const showLogin = ref(false)
const showSignup = ref(false)
const menuOpen = ref(false)


const searchQuery = ref('')
const searchType = ref('posts')
const searchTypeOpen = ref(false)





function openLogin() {
  showSignup.value = false
  showLogin.value = true
}

function openSignup() {
  showLogin.value = false
  showSignup.value = true
}

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function toggleSearchType() {
  searchTypeOpen.value = !searchTypeOpen.value
}

function selectSearchType(type) {
  searchType.value = type
  searchTypeOpen.value = false
}

function goProfile() {
  menuOpen.value = false
  if (userStore.user?.id) {
     router.push({ path: `/user/${userStore.user.id}` })
  }
}

function goWrite() {
  menuOpen.value = false
  router.push({ name: 'CreateBlog' }).catch(() => {})
}

function handleLogout() {
  userStore.logout()
  menuOpen.value = false
  router.push({ name: 'Home' }).catch(() => {})
}

function gotoHome() {
  router.push({ name: 'Home' }).catch(() => {})
}

function onLoginSuccess() {
  if (userStore.user?.id) {
    router.push({ path: `/user/${userStore.user.id}` })
  }
}

function handleSearch() {
  const query = searchQuery.value.trim()

  if (query) {
    console.log("Searching for:", query)
    router.push({ 
      path: '/search', 
      query: { 
        q: query,
        type: searchType.value 
      } 
    }).catch(() => {})
    
    searchQuery.value = ''
    document.activeElement?.blur()

  }
}


const userInitial = computed(() => {
  const n = userStore.user?.name || userStore.user?.email || ''
  return n ? n.charAt(0).toUpperCase() : 'U'
})

const searchPlaceholder = computed(() => {
  return searchType.value === 'posts' 
    ? 'Search articles...' 
    : 'Search by author name...'
})
</script>