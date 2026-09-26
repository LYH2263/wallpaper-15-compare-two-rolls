<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
</script>
<template>
  <div class="page"><h1>记录</h1><ul><li v-for="r in items" :key="r.id">
    <router-link :to="`/history/${r.id}`">
      <template v-if="r.result?.mode === 'compare'">{{ r.wall_name }} → {{ r.result.roll_a.name }} {{ r.result.side_a.rolls }} 卷 vs {{ r.result.roll_b.name }} {{ r.result.side_b.rolls }} 卷（对照）</template>
      <template v-else>{{ r.wall_name }} → {{ r.result?.rolls }} 卷</template>
    </router-link>
  </li></ul></div>
</template>
