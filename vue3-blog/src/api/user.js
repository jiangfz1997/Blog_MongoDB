import api from '@/services/api.js'

export async function getUserProfile(id) {
  return await api.get(`/users/${id}/public`)
}

export async function searchUserbyUsername(q, page=1, size=10) {
  return await api.get('/search/users', {
    params: {
      q,
      page,
      size
    }
  })
}

export async function updateUserProfile( profileData) {
  return await api.patch(`/users/me/info`,  profileData)
}

export async function checkUsernameAvailability(username) {
  return await api.get('/users/username/check', {
    params: { username }
  })
}