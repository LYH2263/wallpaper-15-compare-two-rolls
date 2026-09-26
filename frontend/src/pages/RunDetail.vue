<script setup>
import { onMounted, ref } from 'vue'
import { errText, getJSON } from '../api'
import CompareBoard from '../components/CompareBoard.vue'
import DropStripBar from '../components/DropStripBar.vue'
const props = defineProps({ id: String })
const run = ref(null); const err = ref('')
onMounted(async () => {
  try { run.value = await getJSON(`/api/runs/${props.id}`) } catch (e) { err.value = errText(e) }
})
</script>
<template>
  <div class="page"><h1>记录 #{{ id }}</h1>
  <p v-if="err" class="warn">{{ err }}</p>
  <div v-if="run">
    <p>{{ run.wall_name }} · {{ run.created_at }}<template v-if="run.note"> · {{ run.note }}</template></p>
    <div v-if="run.result?.mode === 'compare'">
      <CompareBoard :roll-a="run.result.roll_a" :roll-b="run.result.roll_b" :side-a="run.result.side_a" :side-b="run.result.side_b" />
    </div>
    <div v-else>
      <strong>{{ run.result?.rolls }} 卷</strong> · {{ run.result?.drops }} 条 · 每条 {{ run.result?.drop_len_m }}m
      <DropStripBar :drops="run.result?.drops" :drop-len="run.result?.drop_len_m" :rolls="run.result?.rolls" />
    </div>
  </div>
  </div>
</template>
