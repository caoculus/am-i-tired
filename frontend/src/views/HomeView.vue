<script setup lang="ts">
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import Checkbox from "primevue/checkbox";
import Button from 'primevue/button'
import {ref} from "vue";
import axios from "axios"

const request = () => {
  axios.post('http://10.0.0.251:3000/request', {
    test: 'test',
  }).then(res => {
    console.log(res)
  }).catch(err => console.log(err))
}

const checked = ref<boolean>(false)
</script>

<template>
    <Accordion :active-index="0">
      <AccordionTab header="Header 1">
        <p class="m-0">Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ad amet assumenda atque aut beatae dolor dolorem, eaque ipsam laboriosam libero natus nesciunt obcaecati officia optio quaerat qui ratione suscipit temporibus.</p>
      </AccordionTab>
      <AccordionTab header="Header 2">
        <p class="m-0">Lorem ipsum dolor sit amet, consectEtur adipisicing elit. Ad amet assumenda atque aut beatae dolor dolorem, eaque ipsam laboriosam libero natus nesciunt obcaecati officia optio quaerat qui ratione suscipit temporibus.</p>
        <Checkbox v-model="checked" :binary="true" />
        <Button label="submit" icon="pi pi-check" @click="request"/>
      </AccordionTab>
    </Accordion>
</template>
