<script setup lang="ts">
import { RouterView } from 'vue-router'
import SideBar from '@/components/SideBar.vue'
import { ref } from 'vue'
import TopBar from '@/components/TopBar.vue'

const collapsedSidebar = ref<boolean>(false)
const topBar = ref<boolean>(true)
const update = () => {
  collapsedSidebar.value = !collapsedSidebar.value
}
</script>

<template>
  <div class="fixed p-0 m-0 top-0 left-0 w-full h-full bg-surface-100 dark:bg-surface-800">
    <div class="flex flex-col w-full h-full">
      <TopBar :topBar="topBar" :update="update" />
      <div class="flex flex-row h-full">
        <Transition
          enter-active-class="transition-all duration-200"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
          leave-active-class="transition-all duration-200"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div v-if="collapsedSidebar" class="border-r-2 border-primary-600">
            <SideBar/>
          </div>
        </Transition>
        <div class="w-full">
          <RouterView />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
