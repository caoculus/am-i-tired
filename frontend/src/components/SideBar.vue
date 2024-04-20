<script setup lang="ts">
import Menu from 'primevue/menu'
import { ref } from "vue";

const items = ref([
  { label: 'New', icon: 'pi pi-plus' },
  { label: 'Search', icon: 'pi pi-search' }
]);
</script>

<template>
  <div class="flex justify-center">
    <Menu :model="items" />
  </div>
</template>

<style scoped>

</style>