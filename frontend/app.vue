<template>
  <div id="app">
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
// Global meta configuration is handled in nuxt.config.ts
</script>

<style>
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

html,
body,
#app {
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>
