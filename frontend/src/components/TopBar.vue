<script setup lang="ts">
import Toolbar from 'primevue/toolbar'

const { update, topBar } = defineProps<{
  update: () => void,
  topBar: boolean
}>()

</script>


<template>
    <Toolbar v-if="topBar" class="shadow-md bg-gradient-to-r from-surface-700 to-surface-700 rounded-none">
      <template #start>
        <button
          class="p-link inline-flex justify-center items-center text-white w-[3rem] rounded-full hover:bg-white/10 transition-all transition-duration-200"
          @click="update"
        >
        <i class="pi pi-align-left text-2xl"></i>
        </button>
      </template>
      <template #center>
        <h1 class="text-white">Am I tired?</h1>
      </template>
      <template #end>
        <button
          class="p-link inline-flex justify-center items-center text-white w-[3rem] rounded-full hover:bg-white/10 transition-all transition-duration-200"
        >
          <i class="pi pi-user text-2xl text-white"></i>
        </button>
      </template>
    </Toolbar>
</template>

<style scoped>

</style>