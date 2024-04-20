<script setup lang="ts">
import Toolbar from 'primevue/toolbar'

const { update } = defineProps<{
  update: () => void
}>()

</script>


<template>
    <Toolbar class="bg-surface-900 shadow-md bg-gradient-to-r from-primary-500/70 to-primary-600/80">
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
        <div class="flex items-center gap-2">
          <i class="pi pi-person"></i>
        </div>
      </template>
    </Toolbar>
</template>

<style scoped>

</style>