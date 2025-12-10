<template>
  <teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center px-4 sm:px-0">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" @click="close"></div>

      <div
        class="relative z-10 w-full max-w-md bg-white rounded-2xl shadow-2xl transform transition-all scale-100"
        role="dialog"
        aria-modal="true"
        @click.stop
      >
        <div class="px-8 py-6 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-blue-50 to-white rounded-t-2xl">
          <div>
            <h3 class="text-2xl font-bold text-gray-800">Create Account</h3>
            <p class="text-gray-500 text-sm mt-1">Join our community today!</p>
          </div>
          <button @click="close" class="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-full hover:bg-gray-100">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="onSubmit" class="p-8 space-y-6">
          <div class="space-y-3">
            <label class="block text-sm font-medium text-gray-700 mb-2">Choose an Avatar</label>
            <div class="flex flex-wrap justify-center gap-4 py-2">
              <div
                v-for="(url, index) in avatarOptions"
                :key="index"
                @click="selectAvatar(url)"
                class="relative cursor-pointer group"
              >
                <img
                  :src="url"
                  alt="Avatar Option"
                  class="w-16 h-16 rounded-full border-4 transition-all duration-200 p-0.5"
                  :class="selectedAvatar === url
                    ? 'border-blue-500 shadow-md scale-110'
                    : 'border-transparent group-hover:border-blue-200 group-hover:scale-105'"
                >
                <div v-if="selectedAvatar === url" class="absolute bottom-0 right-0 bg-blue-500 text-white rounded-full p-0.5 border-2 border-white">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
             <p v-if="!selectedAvatar && showErrors" class="text-xs text-red-500 text-center">Please select an avatar.</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                </svg>
              </span>
              <input
                v-model="username"
                :class="['pl-10 w-full border rounded-xl px-4 py-3 bg-gray-50 focus:bg-white transition-colors outline-none focus:ring-2',
                         usernameError ? 'border-red-300 focus:ring-red-200' : 'border-gray-200 focus:ring-blue-100 focus:border-blue-400']"
                type="text"
                autocomplete="username"
                placeholder="Choose a username"
              />
            </div>
            <p v-if="usernameError" class="text-xs text-red-500 mt-1 ml-1">{{ usernameError }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                </svg>
              </span>
              <input
                v-model="email"
                 :class="['pl-10 w-full border rounded-xl px-4 py-3 bg-gray-50 focus:bg-white transition-colors outline-none focus:ring-2',
                         emailError ? 'border-red-300 focus:ring-red-200' : 'border-gray-200 focus:ring-blue-100 focus:border-blue-400']"
                type="email"
                autocomplete="email"
                placeholder="you@example.com"
              />
            </div>
            <p v-if="emailError" class="text-xs text-red-500 mt-1 ml-1">{{ emailError }}</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
               <div class="relative">
                <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                  </svg>
                </span>
                <input
                  v-model="password"
                  :class="['pl-10 w-full border rounded-xl px-4 py-3 bg-gray-50 focus:bg-white transition-colors outline-none focus:ring-2',
                           passwordError ? 'border-red-300 focus:ring-red-200' : 'border-gray-200 focus:ring-blue-100 focus:border-blue-400']"
                  type="password"
                  autocomplete="new-password"
                  placeholder="6+ characters"
                />
               </div>
               <p v-if="passwordError" class="text-xs text-red-500 mt-1 ml-1">{{ passwordError }}</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
              <div class="relative">
                 <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                  </svg>
                </span>
                <input
                  v-model="confirmPassword"
                  :class="['pl-10 w-full border rounded-xl px-4 py-3 bg-gray-50 focus:bg-white transition-colors outline-none focus:ring-2',
                           confirmPasswordError ? 'border-red-300 focus:ring-red-200' : 'border-gray-200 focus:ring-blue-100 focus:border-blue-400']"
                  type="password"
                  autocomplete="new-password"
                  placeholder="Repeat password"
                />
              </div>
               <p v-if="confirmPasswordError" class="text-xs text-red-500 mt-1 ml-1">{{ confirmPasswordError }}</p>
            </div>
          </div>

          <div v-if="store.error || localError" class="bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-700">{{ store.error || localError }}</p>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-4 pt-4">
            <button
              type="button"
              @click="close"
              class="px-5 py-2.5 rounded-xl border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center"
              :disabled="store.loading"
            >
               <svg v-if="store.loading" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="store.loading">Creating Account...</span>
              <span v-else>Create Account</span>
            </button>
          </div>

          <div class="text-center pt-4 border-t border-gray-100 text-sm text-gray-600">
            <span>Already have an account?</span>
            <button type="button" @click="switchToLogin" class="text-blue-600 font-semibold hover:text-blue-800 hover:underline ml-1 transition-colors">
              Log in here
            </button>
          </div>
        </form>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../store/userStore'

const emit = defineEmits(['close', 'success', 'switchToLogin'])
const store = useUserStore()

// --- Form Data ---
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const selectedAvatar = ref(null) // Store selected avatar URL
const localError = ref('')
const showErrors = ref(false) // Control when to show validation errors

// --- Avatar Options ---
// Using Multiavatar service for diverse, deterministic avatars.
// You can replace these URLs with any other public avatar service (e.g., Dicebear).
// We use a random string/number to get different avatars.
const avatarOptions = ref([
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Felix',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Aneka',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Milo',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Lia',
  'https://api.dicebear.com/9.x/adventurer/svg?seed=Christopher',
])

// --- Validation Logic (Simple client-side check) ---
const usernameError = computed(() => {
  if (!showErrors.value) return ''
  if (!username.value.trim()) return 'Username is required.'
  if (username.value.trim().length < 3) return 'Username must be at least 3 characters.'
  return ''
})

const emailError = computed(() => {
  if (!showErrors.value) return ''
  if (!email.value.trim()) return 'Email is required.'
  // Simple email regex for client-side check
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value.trim())) return 'Please enter a valid email address.'
  return ''
})

const passwordError = computed(() => {
  if (!showErrors.value) return ''
  if (!password.value) return 'Password is required.'
  if (password.value.length < 6) return 'Password must be at least 6 characters.'
  return ''
})

const confirmPasswordError = computed(() => {
  if (!showErrors.value) return ''
  if (confirmPassword.value !== password.value) return 'Passwords do not match.'
  return ''
})

const isFormValid = computed(() => {
  return !usernameError.value &&
         !emailError.value &&
         !passwordError.value &&
         !confirmPasswordError.value &&
         selectedAvatar.value
})

// --- Actions ---
function selectAvatar(url) {
  selectedAvatar.value = url
}

function close() {
  resetForm()
  emit('close')
}

function switchToLogin() {
  resetForm()
  emit('switchToLogin')
  emit('close')
}

function resetForm() {
    username.value = ''
    email.value = ''
    password.value = ''
    confirmPassword.value = ''
    selectedAvatar.value = null
    localError.value = ''
    showErrors.value = false
    store.error = null // Clear store error on close/reset
}

async function onSubmit() {
  localError.value = ''
  showErrors.value = true // Trigger validation display

  if (!isFormValid.value) {
      if (!selectedAvatar.value && !localError.value) {
           // Keep logic simple, avatar error is handled in template, but if form is invalid ONLY due to avatar, we can ensure no other error hides it.
      }
      return // Stop if form is invalid
  }

  try {
    const user = await store.register({
      username: username.value.trim(),
      email: email.value.trim(),
      password: password.value,
      avatar_url: selectedAvatar.value
    })
    console.log("Registration successful", user);
    emit('success', user)
    close() // Close handles reset
  } catch (err) {
    console.error('onSubmit error:', err)
    // Handle API errors that the store doesn't catch or re-throws
    localError.value = err?.message || String(err) || 'An unexpected error occurred.'
  }
}
</script>