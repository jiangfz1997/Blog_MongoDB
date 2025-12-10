<template>
  <div class="min-h-screen bg-gray-50 text-gray-800">
    <NavBar />

    <div class="max-w-7xl mx-auto grid grid-cols-12 gap-6 px-4 mt-6">
      <aside v-if="$slots.left" class="col-span-3 hidden lg:block">
        <slot name="left" />
      </aside>

      <main
        :class="[
          $slots.left ? 'lg:col-span-6' : 'lg:col-span-9',
          'col-span-12'
        ]"
      >
        <slot name="main" />
      </main>

      <aside v-if="$slots.right" class="col-span-3 hidden xl:block">
        <slot name="right" />
      </aside>
    </div>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
</script>
