<template>
  <teleport to="body">
    <transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        class="fixed inset-0 z-50 flex items-center justify-center px-4 sm:px-0"
        role="dialog"
        aria-modal="true"
      >
        <div
          class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity"
          @click="close"
        ></div>

        <transition
          enter-active-class="transition ease-out duration-300"
          enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          enter-to-class="opacity-100 translate-y-0 sm:scale-100"
          leave-active-class="transition ease-in duration-200"
          leave-from-class="opacity-100 translate-y-0 sm:scale-100"
          leave-to-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
        >
          <div
            class="relative z-10 w-full max-w-md bg-white rounded-2xl shadow-2xl transform overflow-hidden"
            @click.stop
          >
            <div class="px-8 pt-8 pb-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-2xl font-bold text-gray-800">Welcome Back</h3>
                <button 
                  @click="close" 
                  class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <p class="text-gray-500 text-sm">Please sign in to continue your journey.</p>
            </div>

            <form @submit.prevent="onSubmit" class="px-8 pb-8 space-y-5">
              
              <div v-if="store.error" class="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                {{ store.error }}
              </div>

              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1.5">Email</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                    </svg>
                  </div>
                  <input
                    ref="emailInput"
                    v-model="email"
                    type="email"
                    required
                    class="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                    placeholder="Enter your email"
                  />
                </div>
              </div>
              
              <div>
                <div class="flex items-center justify-between mb-1.5">
                  <label class="block text-sm font-semibold text-gray-700">Password</label>
                  <!-- <a href="#" class="text-xs text-blue-600 hover:underline hover:text-blue-800">Forgot password?</a> -->
                </div>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <input
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    class="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                    placeholder="••••••••"
                  />
                  <button 
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 cursor-pointer focus:outline-none"
                  >
                    <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a10.059 10.059 0 013.999-5.42m3.714 8.505l-9.014-8.36m0 0L3.55 2.62m18.117 17.783l-3.24-3.01" />
                    </svg>
                  </button>
                </div>
              </div>

              <button
                type="submit"
                class="w-full flex items-center justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                :disabled="store.loading"
              >
                <svg v-if="store.loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ store.loading ? 'Signing in...' : 'Sign In' }}</span>
              </button>

            <div class="text-center mt-4">
              <p class="text-sm text-gray-600">
                Don't have an account? 
                <a 
                  href="#" 
                  class="font-medium text-blue-600 hover:text-blue-500"
                  @click.prevent="switchToRegister"
                >
                  Sign up
                </a>
              </p>
            </div>
            </form>
          </div>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useUserStore } from '@/store/userStore'

const emit = defineEmits(['close', 'success', 'switchToRegister'])

const store = useUserStore()
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const emailInput = ref(null) 

async function onSubmit() {
  if (!email.value || !password.value) return
  
  try {
    const user = await store.login({ 
      email: email.value.trim(), 
      password: password.value 
    })
    emit('success', user)
    emit('close')
  } catch (err) {
    console.error('onSubmit error:', err)
  }
}

function close() {
  store.error = null
  emit('close')
}

function onDocumentKey(e) {
  if (e.key === 'Escape') close()
}
function switchToRegister() {
  emit('close')
  emit('switchToRegister')
}
onMounted(() => {

  
  document.addEventListener('keydown', onDocumentKey)
  
  nextTick(() => {
    emailInput.value?.focus()
  })
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onDocumentKey)
})
</script>