<script setup lang="ts">
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import { ref } from 'vue'
const visible = ref(false)

</script>

<template>
  <Button label="Show Dialog" @click="visible = true"/>
  <div class="flex justify-center">
    <Dialog
      v-model:visible="visible"
      modal header="Result"
      :style="{ width: '50rem' }"
      :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    >
      <div class="flex flex-row justify-center items-center ">
        <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      </div>
    </Dialog>
  </div>
</template>