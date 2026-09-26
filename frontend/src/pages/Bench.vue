<script setup>
import { onMounted, ref } from 'vue'
import { errText, getJSON, postJSON } from '../api'
import CompareBoard from '../components/CompareBoard.vue'
import DropStripBar from '../components/DropStripBar.vue'
const walls = ref([]); const rolls = ref([]); const wallId = ref(1); const rollId = ref(1); const rollIdB = ref(''); const out = ref(null); const err = ref('')
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
})
async function run(save) {
  err.value = ''; out.value = null
  const comparing = rollIdB.value !== ''
  try {
    if (save) {
      const body = { wall_id: wallId.value, roll_id: rollId.value, save: true }
      if (comparing) body.roll_id_b = rollIdB.value
      out.value = await postJSON('/api/estimate', body)
    } else {
      let q = `/api/estimate?wall_id=${wallId.value}&roll_id=${rollId.value}`
      if (comparing) q += `&roll_id_b=${rollIdB.value}`
      out.value = await getJSON(q)
    }
  } catch (e) { err.value = errText(e) }
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
  <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <select v-model="rollIdB"><option value="">（不对照）</option><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
  <p v-if="err" class="warn">{{ err }}</p>
  <div v-if="out && out.mode === 'compare'">
    <CompareBoard :roll-a="out.roll_a" :roll-b="out.roll_b" :side-a="out.side_a" :side-b="out.side_b" />
    <p v-if="out.run_id">已存为记录 #{{ out.run_id }}</p>
  </div>
  <div v-else-if="out"><strong>{{ out.rolls }} 卷</strong> · {{ out.drops }} 条 · 每条 {{ out.drop_len_m }}m
  <DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" /></div>
  </div>
</template>
