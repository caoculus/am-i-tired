<script setup lang="ts">
import VideoPlayer from '@/components/VideoPlayer.vue'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import Toast from 'primevue/toast'
import ResultsTab from '@/components/ResultsTab.vue'


const toast = useToast()
const errorMsg = () => {
  toast.add({
    severity: 'error',
    summary: 'Permission declined',
    detail: ' Camera permission denied, thus app does not work, please go into settings to allow camera usage',
    life: 2000
  })
}


</script>

<template>
  <Toast />
  <div class="h-screen flex justify-center items-center">
    <div class="flex flex-col">
      <VideoPlayer />
      <div class="flex flex-row items-center justify-center gap-3 my-3">
        <Button label="Record" rounded @click="errorMsg()"/>
        <ResultsTab />
      </div>
    </div>
  </div>
</template>