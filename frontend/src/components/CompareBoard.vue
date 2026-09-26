<script setup>
import { computed } from 'vue'
import DropStripBar from './DropStripBar.vue'
const props = defineProps({ rollA: Object, rollB: Object, sideA: Object, sideB: Object })
const delta = computed(() => (props.sideB?.rolls ?? 0) - (props.sideA?.rolls ?? 0))
const deltaText = computed(() => {
  const d = delta.value
  if (d === 0) return '两侧用量相同'
  return `${d > 0 ? 'B' : 'A'} 侧多 ${Math.abs(d)} 卷`
})
</script>
<template>
  <div class="compare-board">
    <section class="compare-side">
      <h3>A · {{ rollA?.name }}</h3>
      <p><strong>{{ sideA?.rolls }} 卷</strong> · {{ sideA?.drops }} 条 · 每条 {{ sideA?.drop_len_m }}m</p>
      <DropStripBar :drops="sideA?.drops" :drop-len="sideA?.drop_len_m" :rolls="sideA?.rolls" />
    </section>
    <section class="compare-side">
      <h3>B · {{ rollB?.name }}</h3>
      <p><strong>{{ sideB?.rolls }} 卷</strong> · {{ sideB?.drops }} 条 · 每条 {{ sideB?.drop_len_m }}m</p>
      <DropStripBar :drops="sideB?.drops" :drop-len="sideB?.drop_len_m" :rolls="sideB?.rolls" />
    </section>
  </div>
  <p class="compare-delta">差额：{{ deltaText }}</p>
</template>
