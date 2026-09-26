<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import RunDetail from '../components/RunDetail.vue'
const items = ref([]); const openId = ref(null); const detail = ref(null)
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
async function toggle(id) {
  if (openId.value === id) { openId.value = null; detail.value = null; return }
  detail.value = await getJSON(`/api/runs/${id}`)
  openId.value = id
}
</script>
<template>
  <div class="page"><h1>记录</h1>
    <ul>
      <li v-for="r in items" :key="r.id">
        <a href="#" @click.prevent="toggle(r.id)">
          #{{ r.id }} {{ r.wall_name }} →
          <template v-if="r.result.mode==='compare'">
            <span class="roll-chip">对照</span>
            {{ r.result.roll_name_a }} {{ r.result.a.rolls }} 卷 / {{ r.result.roll_name_b }} {{ r.result.b.rolls }} 卷
            · 差额 {{ r.result.delta_rolls }} 卷
          </template>
          <template v-else>{{ r.roll_name }} → {{ r.result.rolls }} 卷</template>
        </a>
        <RunDetail v-if="openId===r.id && detail" :run="detail" />
      </li>
    </ul>
  </div>
</template>
