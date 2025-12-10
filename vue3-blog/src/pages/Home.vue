<template>
  <DefaultLayout>
    <template #left>
      <LeftSidebarHome />
    </template>

    <template #main>
      <MainFeedHome />
    </template>

    <template #right>
      <RightSidebarHome />
    </template>
  </DefaultLayout>
</template>

<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import LeftSidebarHome from '@/components/home/LeftSidebarHome.vue'
import MainFeedHome from '@/components/home/MainFeedHome.vue'
import RightSidebarHome from '@/components/home/RightSidebarHome.vue'
</script>
