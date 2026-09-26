<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import CompareBoard from '../components/CompareBoard.vue'
import DropStripBar from '../components/DropStripBar.vue'
const walls = ref([]); const rolls = ref([]); const wallId = ref(1); const rollId = ref(1); const rollIdB = ref(0); const out = ref(null); const err = ref('')
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
})
async function run(save) {
  err.value = ''
  try {
    if (rollIdB.value) {
      out.value = save
        ? await postJSON('/api/estimate', { wall_id: wallId.value, roll_id: rollId.value, roll_id_b: rollIdB.value, save: true })
        : await getJSON(`/api/estimate?wall_id=${wallId.value}&roll_id=${rollId.value}&roll_id_b=${rollIdB.value}`)
    } else {
      out.value = save
        ? await postJSON('/api/estimate', { wall_id: wallId.value, roll_id: rollId.value, save: true })
        : await getJSON(`/api/estimate?wall_id=${wallId.value}&roll_id=${rollId.value}`)
    }
  } catch (e) {
    out.value = null
    err.value = e.message
  }
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
  <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <select v-model.number="rollIdB">
    <option :value="0">（单卷）</option>
    <option v-for="r in rolls" :key="r.id" :value="r.id">对照：{{ r.name }}</option>
  </select>
  <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
  <p v-if="err" class="warn">{{ err }}</p>
  <CompareBoard v-if="out && out.mode==='compare'" :roll-a="out.roll" :roll-b="out.roll_b" :a="out.a" :b="out.b" :delta-rolls="out.delta_rolls" />
  <div v-else-if="out"><strong>{{ out.rolls }} 卷</strong> · {{ out.drops }} 条 · 每条 {{ out.drop_len_m }}m
  <DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" /></div>
  </div>
</template>
