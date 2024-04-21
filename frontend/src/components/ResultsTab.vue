<script setup lang="ts">
import Dialog from 'primevue/dialog'
import { ref } from 'vue'
import Button from 'primevue/button'

export type sendingType = {
  sendData: () => boolean
}

const { sendData } = defineProps<sendingType>()
const visible = ref(false)
const onSendClicked = () => {
  if(sendData()){
    visible.value = true
  }
}

</script>

<template>
  <Button label="Send Data" @click="onSendClicked" />
  <div class="flex justify-center">
    <Dialog
      v-model:visible="visible"
      modal header="Result"
      :style="{ width: '50rem' }"
      :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    >
      <div class="flex flex-row justify-center items-center ">
        <slot name="result" />
      </div>
    </Dialog>
  </div>
</template>