<script setup lang="ts">
import Toolbar from 'primevue/toolbar'
import { ref } from 'vue'

const items = ref([
  {
    label: 'Update',
    icon: 'pi pi-refresh'
  },
  {
    label: 'Delete',
    icon: 'pi pi-times'
  }
])
</script>
<template>
  <div>
    <Toolbar>
      <template #start>
        <Button icon="pi pi-plus" class="mr-2" />
        <Button icon="pi pi-print" class="mr-2" />
        <Button icon="pi pi-upload" />
      </template>

      <template #center>
        <span class="relative">
            <i class="pi pi-search absolute top-2/4 -mt-2 left-3 text-surface-400 dark:text-surface-600" />
            <InputText placeholder="Search" class="pl-10" />
        </span>
      </template>

      <template #end> <SplitButton label="Save" icon="pi pi-check" :model="items"></SplitButton></template>
    </Toolbar>
  </div>
</template>

<style>
</style>
