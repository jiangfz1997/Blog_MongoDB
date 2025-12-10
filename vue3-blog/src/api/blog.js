import api from '@/services/api.js'

export async function getBlog(id) {
  return await api.get(`/blogs/${id}`)
}

export async function getBlogListByUserId(id, page=1, limit=10, excludeId=null) {
  return await api.get(`/blogs/author/${id}`, {
    params: {
      page,
      size: limit,
      exclude_blog_id: excludeId
    }
  })
}

export async function publishBlog(blogData) {
  return await api.post('/blogs', blogData)
}

export async function updateBlog(blogId, blogData) {
  return await api.patch(`/blogs/${blogId}`, blogData)
}

export async function searchBlogs(params) {
  console.log('API call to searchBlogs with params:', params)
  return await api.get('/search/blogs', { params })
}

export async  function deleteBlog(blogId) { {
  return await api.delete(`/blogs/${blogId}`)
} }
export async function getHotTags(limit=10) {
  return await api.get("/blogs/tags/hottest", {
    params: {limit}
  })
}

export async function getHotViewedBlogs(limit=5) {
  return await api.get("/blogs/views/hottest", {
    params: {limit}
  })
}
export async function toggleLikeBlog(blogId) {
  return await api.post(`/blogs/${blogId}/like`)
}

export async function getDiscoverFeed(page=1,size=5) {
  return await api.get("/search/discover", {
    params: {page, size}
  })
}