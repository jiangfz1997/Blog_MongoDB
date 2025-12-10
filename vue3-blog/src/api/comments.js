import api from '@/services/api.js'



export async function getComments(blogId, page=1, size=10, replies_page=1, replies_size=5) {
  return await api.get(`/comments/blog/${blogId}`,
    {params:{
        page: page,
        size: size,
        replies_page: replies_page,
        replies_size: replies_size
    }}
  )
}

export async function postComment(blogId, content, parentId = null) {
  return await api.post('/comments', {
    blog_id: blogId,
    content,
    parent_id: parentId
  })
}

export function formatDate(isoString) {
  if (!isoString.endsWith('Z')) {
    isoString += 'Z'
  }
  const date = new Date(isoString)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return 'Just now'
  // If within 1 hour
  if (diff < 3600000) return Math.floor(diff / 60000) + ' minutes ago'
  // If within 24 hours
  if (diff < 86400000) return Math.floor(diff / 3600000) + ' hours ago'
  
  // Otherwise show date
  return date.toLocaleDateString('en-US', {
    month: '2-digit',
    day: '2-digit'
  })
}

export async function getMoreReplies(rootId, page=1, size=5) {
  return await api.get(`/comments/root/${rootId}/replies`, {
    params: {
      page,
      size
    }
  })
}

export async function deleteComment(commentId, blogId) {
  return await api.delete(`/comments/${commentId}`, {
    params: { blog_id: blogId }
  }
  )
}