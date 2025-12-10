import { ref } from 'vue'
import { searchBlogs } from '@/api/blog'


export function useSearch() {
  const results = ref([])
  const total = ref(0)
  const loading = ref(false)
  const pageSize = 10 

  const executeSearch = async (params) => {
    loading.value = true
    console.log('Executing search with params:',
        params
    )
    console.log("params are:  ", params)
    try {
      const apiParams = {
        keyword: params.q || '', 
        tags: params.tags || [],
        page: params.page || 1,
        size: pageSize,
        sort_by: params.sortBy || 'created',
        sort_order: params.sortOrder || 'desc'
      }
      console.log('API search params:', apiParams)
      const rawData = await searchBlogs(apiParams)
      
      console.log('Raw search data:', rawData)
      if (rawData.blogs && Array.isArray(rawData.blogs.items)) {
        
        results.value = rawData.blogs.items.map(item => ({
          id: item.blog_id,             
          title: item.title,
          author_username: item.author_username,
          created_at: item.created_at,

          tags: item.tags || [],                     
          content: '',                  
          views: item.view_count || 0,                     
          like_count: item.like_count || 0,                  
          comments_count: item.comment_count||0,
          isLiked: item.is_liked || false,
          avatar_url: item.avatar_url || ''         
        }))

        total.value = rawData.blogs.total
      } else {
        results.value = []
        total.value = 0
      }

    } catch (e) {
      console.error('Search error:', e)
      results.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  return { results, total, loading, pageSize, executeSearch }
}