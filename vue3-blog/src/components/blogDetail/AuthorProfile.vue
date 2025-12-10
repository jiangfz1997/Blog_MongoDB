<template>
  <div class="flex items-center gap-3 bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
    <img
      :src="avatar_url"
      alt="author avatar"
      class="w-12 h-12 rounded-full object-cover"
    />
    <div>
      <h3 class="text-lg font-semibold">{{ name }}</h3>
      <p class="text-gray-500 text-sm">{{ bio }}</p>
    </div>
  </div>
</template>

<script setup>
import { h } from 'vue';

defineProps({
  name: String,
  bio: String,
  avatar_url: String
})
</script>
