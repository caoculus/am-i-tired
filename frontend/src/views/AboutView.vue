<script setup lang="ts">
import AccordionTab from 'primevue/accordiontab'
import Accordion from 'primevue/accordion'
import Divider from 'primevue/divider'
import Card from 'primevue/card'
</script>
<template>
  <div class="flex flex-row">
   <div class="w-1/2 mt-4 ml-4 bg-surface-800">
     <Card>
       <template #header>
         <h1 class="text-4xl text-white">Motivations for this project</h1>
       </template>
       <template #content>
         <p>
           There are two main downsides to working while tired (as seen on the right),
           But there times where we don't even know that we are tired, so this app act
           as a quick way for us to know when to rest.
         </p>
       </template>
     </Card>
   </div>
    <Divider layout="vertical"/>
    <div class="w-1/2 mt-4">
      <Accordion :active-index="0">
        <AccordionTab header="Reduced Cognitive Function">
          <p class="m-0">Fatigue hinders your focus, memory, and decision-making abilities. This can lead to errors in judgement, especially in critical tasks.  Studies have shown a connection between fatigue and increased accidents in the workplace</p>
        </AccordionTab>
        <AccordionTab header="Increased Stress and Weakened Immune System: ">
          <p class="m-0">When you're pushing through exhaustion, your body produces more stress hormones like cortisol. Over time, chronically elevated cortisol levels can weaken your immune system, making you more susceptible to illnesses</p>
        </AccordionTab>
      </Accordion>
    </div>
  </div>
</template>
