<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import SideBar from '@/components/SideBar.vue'
import { ref } from 'vue'
import TopBar from '@/components/TopBar.vue'

const collapsedSidebar = ref<boolean>(false)
const update = () => {
  collapsedSidebar.value = !collapsedSidebar.value
}
</script>

<template>
  <div class="fixed p-0 m-0 top-0 left-0 w-full h-full bg-surface-100 dark:bg-surface-900">
    <div class="flex flex-row">
      <header>
        <SideBar v-if="collapsedSidebar" />
        <nav>
          <RouterLink to="/" class="text-amber-50">Home</RouterLink>
          <RouterLink to="/about" class="text-amber-50">About</RouterLink>
          <RouterLink to="/login" class="text-amber-50">Login</RouterLink>
        </nav>
      </header>
      <div class="flex flex-col w-full">
        <TopBar :update="update" />
        <RouterView />
      </div>
    </div>
  </div>
</template>

<style scoped></style>
