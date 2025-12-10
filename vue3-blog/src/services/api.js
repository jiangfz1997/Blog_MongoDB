// src/services/api.js
import axios from 'axios'
import qs from 'qs'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true, 
  headers: {
    'Content-Type': 'application/json'
  },
  paramsSerializer: (params) => {
    return qs.stringify(params, { arrayFormat: 'repeat' })
  }
})

api.interceptors.response.use(
  (res) => res.data,
  (error) => {
    if (error.response) {
      const errorBody = error.response.data
      
      console.group(`🚨 API Error: ${error.response.status} ${error.config.url}`)
      console.error('Error Body:', errorBody)
      console.groupEnd()

      let displayMsg = error.message
      
      if (errorBody) {
        if (typeof errorBody.detail === 'string') {
           displayMsg = errorBody.detail
        } else if (Array.isArray(errorBody.detail)) {
           displayMsg = `Validation Error: ${errorBody.detail[0].msg} at ${errorBody.detail[0].loc.pop()}`
        } else if (errorBody.message) {
           displayMsg = errorBody.message
        }
      }


      const status = error.response.status
      if (status === 401) {
        console.warn('Login required')

      } else if (status === 403) {
        console.warn('Permission denied')
      }



    } else {
      console.error('Network Error:', error.message)
    }

    return Promise.reject(error)
  }
)

export default api
