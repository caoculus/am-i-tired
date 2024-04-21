<script setup lang="ts">
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import Toast from 'primevue/toast'
import ResultsTab, { type sendingType } from '@/components/ResultsTab.vue'
import { onMounted, ref, watchEffect } from 'vue'

export type results = {
  success: boolean,
  result?: number,
}

const url = "ws://10.0.0.251:3000"
const toast = useToast()
let ws = new WebSocket(url)
const mediaRecorder = ref<MediaRecorder | null>(null);
const send = ref(true)
const video = ref<HTMLVideoElement>();
const curStream = ref<MediaStream | null>(null);
const response = ref<results | null>(null)


onMounted(() => {
  const recorderOptions = {
    mimeType: 'video/webm',
    videoBitsPerSecond: 200000 // 0.2 Mbit/sec.
  }

  navigator.mediaDevices.getUserMedia({video: true, audio: false}).then(
    stream => {
      // ws.value = new WebSocket(url,)
      curStream.value = stream;
      mediaRecorder.value = new MediaRecorder(stream, recorderOptions)
      mediaRecorder.value.ondataavailable = (event) => {
        if (event.data && event.data.size > 0 && send.value) {
          console.log('Got blob data:', event.data);
          ws.send(event.data);
        }
      };
    }
  ).catch(() => {
    toast.add({
      severity: 'error',
      summary: 'Permission declined',
      detail: ' Camera permission denied, thus app does not work, please go into settings to allow camera usage',
      life: 5000
    })
    ws.close()
  })
})

const start = () => {
  if(!mediaRecorder.value) {
    return
  }
  mediaRecorder.value.start(1000); // 1000 - the number of milliseconds to record into each Blob
  window.setTimeout(stop, 6000)
}

const stop = () => {
  if(!mediaRecorder.value) {
    return
  }
  send.value = false
  const test: string = 'Stop connection'
  ws.send(test)
  console.log(`send data: ${test}`)
  mediaRecorder.value.stop()
}

const reconnect = () => {
  if(ws.readyState !== WebSocket.CLOSED) {
    ws.close()
  }
  ws = new WebSocket(url)
}

ws.addEventListener("message", (event) => {
  console.log(`Received message from ${url}: ${event.data}`);
  response.value = JSON.parse(event.data);
  ws.close()
})

watchEffect(() => {
  if(video.value){
    video.value.srcObject = curStream.value
  }
})

</script>

<template>
  <Toast />
  <div class="h-screen flex justify-center items-center">
    <div class="flex flex-col">
      <video ref="video" muted autoplay controls class="h-100 w-auto rounded-lg" />
      <div class="flex flex-row items-center justify-center gap-3 my-3">
        <ResultsTab :send-data="start">
          <template #result>
            <div class="flex" v-if="!response">
              <h1 class="text-primary-50">Getting results...</h1>
              <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
            </div>
            <div class="flex flex-col" v-else>
              {{response.result}}
              <Button label="try again" @click="reconnect" />
            </div>
          </template>
        </ResultsTab>
      </div>
    </div>
  </div>
</template>