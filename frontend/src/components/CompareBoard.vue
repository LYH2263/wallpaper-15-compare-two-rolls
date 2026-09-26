<script setup>
import DropStripBar from './DropStripBar.vue'

defineProps({
  rollA: { type: Object, required: true },
  rollB: { type: Object, required: true },
  a: { type: Object, required: true },
  b: { type: Object, required: true },
  deltaRolls: { type: Number, required: true },
})
</script>

<template>
  <div class="compare-board">
    <section class="compare-side">
      <h2>A · {{ rollA.name }} <small>#{{ rollA.id }}</small></h2>
      <p><strong>{{ a.rolls }} 卷</strong> · {{ a.drops }} 条 · 每条 {{ a.drop_len_m }}m · 每卷 {{ a.strips_per_roll }} 条</p>
      <DropStripBar :drops="a.drops" :drop-len="a.drop_len_m" :rolls="a.rolls" />
    </section>
    <section class="compare-side">
      <h2>B · {{ rollB.name }} <small>#{{ rollB.id }}</small></h2>
      <p><strong>{{ b.rolls }} 卷</strong> · {{ b.drops }} 条 · 每条 {{ b.drop_len_m }}m · 每卷 {{ b.strips_per_roll }} 条</p>
      <DropStripBar :drops="b.drops" :drop-len="b.drop_len_m" :rolls="b.rolls" />
    </section>
    <p class="compare-delta">差额 {{ deltaRolls }} 卷</p>
  </div>
</template>

<style scoped>
.compare-board { display: flex; gap: 1rem; flex-wrap: wrap; align-items: flex-start; margin-top: 0.75rem; }
.compare-side { flex: 1 1 16rem; background: #fff; border: 1px dashed #6b4226; padding: 0.5rem 0.75rem; }
.compare-side h2 { margin: 0.25rem 0; font-size: 1.05rem; }
.compare-side small { color: #6b4226; }
.compare-delta { flex-basis: 100%; margin: 0.25rem 0; font-weight: bold; color: #6b4226; }
</style>
