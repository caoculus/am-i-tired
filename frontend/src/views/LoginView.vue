<script setup lang="ts">
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import InputText from 'primevue/inputtext'
import FloatLabel from 'primevue/floatlabel'
import { ref } from 'vue'

const username = ref<string>('')
const password = ref<string>('')
</script>

<template>
  <div class="m-0 position-absolute h-screen bg-primary-200 w-screen flex justify-center items-center">
    <div class="flex flex-col gap-10 md:flex-col dark:bg-surface-800 p-7 rounded-2xl">
      <InputGroup>
        <InputGroupAddon>
          <i class="pi pi-user"/>
        </InputGroupAddon>
        <FloatLabel>
          <InputText id="username" :v-model="username" />
          <label for="username">Username</label>
        </FloatLabel>
      </InputGroup>
      <InputGroup>
        <InputGroupAddon>
          <i class="pi pi-key"/>
        </InputGroupAddon>
        <FloatLabel>
          <InputText id="password" :v-model="password" />
          <label for="password">Password</label>
        </FloatLabel>
      </InputGroup>
    </div>
  </div>
</template>

<style scoped>

</style>