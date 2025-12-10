// src/store/userStore.js
import { defineStore } from 'pinia'
import api from '@/services/api.js'

// Helper function to parse error messages from backend responses
function extractErrorMessage(err) {
  const resp = err.response
  if (resp?.data) {
    if (resp.data.detail) return resp.data.detail
    if (resp.data.message) return resp.data.message
    return JSON.stringify(resp.data)
  }
  return err.message || 'Unknown error occurred'
}

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    loading: false,
    error: null,
    isInitialized: false
  }),

  getters: {
    isLoggedIn: (state) => !!state.user,
    displayName: (state) => (state.user ? state.user.username || state.user.email : '')
  },

  actions: {

    async fetchCurrentUser() {
      this.loading = true
      try {
        const user = await api.get('/users/me')
        this.user = user
      } catch (err) {
        this.user = null
      } finally {
        this.loading = false
        this.isInitialized = true
      }
    },

    /**
     * Handle user login
     */

    async login({ email, password }) {
      this.loading = true
      this.error = null
      
      try {
        // api.post now returns response.data directly
        const data = await api.post('/users/login', { email, password })
        
        // Adjust based on your actual backend response structure
        this.user = data.user ?? data
        console.log("Logged in user data:", this.user)
        return this.user
      } catch (err) {
        const msg = extractErrorMessage(err)
        this.error = msg
        throw new Error(msg)
      } finally {
        this.loading = false
      }
    },

    /**
     * Handle user registration
     */
    async register({ username, email, password, avatar_url }) {
      this.loading = true
      this.error = null

      try {
        // API automatically unwraps the response, so 'data' is the payload
        const data = await api.post('/users/register', { username, email, password, avatar_url })
        
        this.user = data.user ?? data
        
        return this.user
      } catch (err) {
        const msg = extractErrorMessage(err)
        this.error = msg
        throw new Error(msg)
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        await api.post('/users/logout')
      } catch (err) {
        console.error('Logout warning:', err)
      } finally {
        this.user = null
        this.error = null
      }
    }
  }
})