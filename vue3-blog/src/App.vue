<template>
  <n-config-provider :theme-overrides="themeOverrides">
    
    <n-message-provider>
      
      <router-view />
      
    </n-message-provider>

  </n-config-provider>
</template>

<script setup>
import { NConfigProvider, NMessageProvider } from 'naive-ui'

const themeOverrides = {
  common: {
    primaryColor: '#2563eb', 
    primaryColorHover: '#1d4ed8', 
    primaryColorPressed: '#1e40af', 
    borderRadius: '6px' 
  },
  Button: {
    borderRadiusMedium: '6px'
  }
}
</script>