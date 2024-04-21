<script setup lang="ts">
import Menu from 'primevue/menu'
import { ref } from "vue";
export type sideBarItems = {
  label: string;
  icon: string;
  route: string;
}

const items = ref<sideBarItems[]>([
  {
    label: 'Home',
    icon: 'pi pi-home',
    route: '/',
  },
  {
    label: 'App',
    icon: 'pi pi-desktop',
    route: '/app',
  },
  {
    label: 'About',
    icon: 'pi pi-info',
    route: '/about',
  },
  // {
  //   label: 'History',
  //   icon: 'pi pi-bookmark-fill',
  //   route: '/history'
  // },
  // {
  //   label: 'Login',
  //   icon: 'pi pi-times',
  //   route: '/login'
  // }
]);
</script>

<template>
    <Menu
      :model="items"
      class="w-full h-full"
    >
      <template #item="{ item, props }">
        <router-link v-slot="{href, navigate }" :to="item.route" custom>
          <a v-ripple :href="href" v-bind="props.action" @click="navigate">
            <span :class="item.icon" />
            <span class="ml-2">{{ item.label }}</span>
          </a>
        </router-link>
      </template>
    </Menu>
</template>

<style scoped>

</style>