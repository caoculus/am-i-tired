<script setup lang="ts">
import Button from 'primevue/button'
import MeterGroup from 'primevue/metergroup'
import { useToast } from 'primevue/usetoast'
import Toast from 'primevue/toast'
import ResultsTab from '@/components/ResultsTab.vue'
import { onMounted, reactive, ref, watchEffect } from 'vue'
import ResultMap from '@/assets/resultMap'

export type results = {
  success: boolean,
  result?: number,
}

type meter = {
  label: string,
  value: number,
}

const url = "wss://am-i-tired-backend.fly.dev/"
const toast = useToast()
let ws = new WebSocket(url)
const mediaRecorder = ref<MediaRecorder | null>(null);
const send = ref(true)
const video = ref<HTMLVideoElement>();
const curStream = ref<MediaStream | null>(null);
const response = ref<results | null>(null)

const recorderOptions = {
  mimeType: 'video/webm',
  videoBitsPerSecond: 200000 // 0.2 Mbit/sec.
}

onMounted(() => {
  navigator.mediaDevices.getUserMedia({video: true, audio: false}).then(
    stream => {
      curStream.value = stream;
      mediaRecorder.value = new MediaRecorder(stream, recorderOptions)
      mediaRecorder.value.ondataavailable = (event) => {
        if (event.data && event.data.size > 0 && send.value) {
          console.log('Got blob data:', event.data);
          ws.send(event.data);
        }
      };
      addListener()
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
    toast.add({
      severity: 'error',
      summary: 'Permission declined',
      detail: 'Please enable camera',
      life: 5000
    })
    return false
  }
  mediaRecorder.value.start(1000); // 1000 - the number of milliseconds to record into each Blob
  window.setTimeout(stop, 1500)
  return true
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
  response.value = null
  send.value = true
  start()
  addListener()
}

const addListener = () => {
  ws.addEventListener("message", (event) => {
    console.log(`Received message from ${url}: ${event.data}`);
    response.value = JSON.parse(event.data);
    ws.close()
  })
}

watchEffect(() => {
  if(video.value){
    video.value.srcObject = curStream.value
  }
})

const returnMetered: () => meter[] = () => {
  return [{
    label: 'Tiredness level',
    value: response.value?.result * 10
  },]
}

</script>

<template>
  <Toast />
  <div class="h-screen flex justify-center items-center">
    <div class="flex flex-col">
      <video ref="video" muted autoplay controls class="h-100 w-auto rounded-lg" />
      <div class="flex flex-row items-center justify-center gap-3 my-3">
        <ResultsTab :send-data="start">
          <template #result>
            <div class="flex flex-col" v-if="!response">
              <h1 class="text-primary-50">Getting results...</h1>
              <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
            </div>
            <div class="flex flex-col" v-else>
              <div>
              </div>
              <p class="flex flex-wrap justify-center items-center gap-3" v-if="response.success">
                <MeterGroup :value='returnMetered()' />
                {{ResultMap[response.result]}}
              </p>
              <p class="flex flex-wrap justify-center items-center" v-else>
                Connection Failed! Please try again.
              </p>
              <Button label="try again" @click="reconnect" />
            </div>
          </template>
        </ResultsTab>
      </div>
    </div>
  </div>
</template>