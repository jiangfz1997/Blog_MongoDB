<template>
  <div class="max-w-4xl mx-auto py-8">
    <h1 class="text-2xl font-bold mb-6">
      Search Results: 
      <span class="text-blue-600">"{{ searchQuery }}"</span>
    </h1>

    <div v-if="loading" class="text-center py-10">
      Searching...
    </div>

    <div v-else-if="results.length > 0" class="grid gap-6">
      <ArticleCard 
        v-for="blog in results" 
        :key="blog.id" 
        :post="blog" 
      />
    </div>

    <div v-else class="text-center text-gray-500 py-10">
      No results found for "{{ searchQuery }}"
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useSearch } from '@/composables/useSearch'
import ArticleCard from '@/components/card/ArticleCard.vue'

const route = useRoute()
const { results, loading, executeSearch } = useSearch()

const searchQuery = computed(() => route.query.q || route.query.tag || '')

const handleSearch = () => {
  const query = route.query
  if (Object.keys(query).length > 0) {
    executeSearch(query)
  }
}

onMounted(handleSearch)
watch(() => route.query, () => {
  handleSearch()
})
</script>