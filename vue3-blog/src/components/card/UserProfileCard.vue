<template>
  <router-link 
    :to="`/user/${user.user_id}`"
    class="flex items-center bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
  >
    <img 
        v-if="user.avatar_url" 
        :src="user.avatar_url" 
        alt="User Avatar"
        class="w-16 h-16 rounded-full mr-4 object-cover"
      >

      <div 
          v-else
          class="w-16 h-16 rounded-full mr-4 object-cover">
          {{ user.username ? user.username.charAt(0).toUpperCase() : 'U' }}
      </div>
    <div>
      <h3 class="text-xl font-bold text-gray-800">{{ user.username }}</h3>
      <p class="text-gray-500 text-sm mt-1 line-clamp-2">{{ user.bio || 'No bio yet.' }}</p>
      <!-- <div class="text-xs text-gray-400 mt-2">
         {{ user.post_count }} posts
      </div> -->
    </div>
    
    <div class="ml-auto text-blue-600">
       View Profile →
    </div>
  </router-link>
</template>

<script setup>
defineProps({
  user: {
    type: Object,
    required: true
  }
})
</script>