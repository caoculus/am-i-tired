<script setup lang="ts">
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import Toast from 'primevue/toast'
import ResultsTab from '@/components/ResultsTab.vue'
import { onMounted, ref, watchEffect } from 'vue'

const url = "ws://10.0.0.251:3000"
let ws = new WebSocket(url)
const mediaRecorder = ref<MediaRecorder | null>(null);
const send = ref(true)
const video = ref<HTMLVideoElement>();
const curStream = ref<MediaStream | null>(null);

const toast = useToast()

onMounted(() => {
  const recorderOptions = {
    mimeType: 'video/webm',
    videoBitsPerSecond: 20000 // 0.2 Mbit/sec.
  }

  navigator.mediaDevices.getUserMedia({video: true, audio: false}).then(
    stream => {
      curStream.value = stream;
      mediaRecorder.value = new MediaRecorder(stream, recorderOptions)
      mediaRecorder.value.ondataavailable = (event) => {
        console.log('Got blob data:', event.data);
        if (event.data && event.data.size > 0 && send) {
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
  })
})

const start = () => {
  if(!mediaRecorder.value) {
    return
  }
  mediaRecorder.value.start(1000); // 1000 - the number of milliseconds to record into each Blob
}

const stop = () => {
  if(!mediaRecorder.value) {
    return
  }

  send.value = false
  const test = new Blob()
  ws.send(test)
  console.log(`send data: ${test}`)
  mediaRecorder.value.stop()
}
const shutdown = () => {
  stop()
  // const test = new Blob()
  // ws.send(test)
  // console.log(`send data: ${test}`)
  ws.close()
}
const reconnect = () => {
  if(ws.readyState !== WebSocket.CLOSED) {
    ws.close()
  }
  ws = new WebSocket(url)
}

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
        <Button label="Record" rounded @click="console.log('hi')"/>
        <ResultsTab />
      </div>
    </div>
  </div>
</template>