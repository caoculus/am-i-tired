<script setup lang="ts">
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import Card from 'primevue/card'
</script>

<template>
    <Accordion :active-index="0">
      <AccordionTab header="Start Here">
        <p class="m-0">Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ad amet assumenda atque aut beatae dolor dolorem, eaque ipsam laboriosam libero natus nesciunt obcaecati officia optio quaerat qui ratione suscipit temporibus.</p>
      </AccordionTab>
      <AccordionTab header="Header 2">
        <p class="m-0">Lorem ipsum dolor sit amet, consectEtur adipisicing elit. Ad amet assumenda atque aut beatae dolor dolorem, eaque ipsam laboriosam libero natus nesciunt obcaecati officia optio quaerat qui ratione suscipit temporibus.</p>
      </AccordionTab>
    </Accordion>
</template>
