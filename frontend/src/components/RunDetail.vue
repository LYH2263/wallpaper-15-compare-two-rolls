<script setup>
import { computed } from 'vue'

const props = defineProps({
  run: { type: Object, required: true },
})

const isCompare = computed(() => props.run.result?.mode === 'compare')
</script>

<template>
  <div class="run-detail">
    <template v-if="isCompare">
      <p>
        对照：{{ run.result.roll_name_a }} <small>#{{ run.result.roll_id_a }}</small>
        vs {{ run.result.roll_name_b }} <small>#{{ run.result.roll_id_b }}</small>
      </p>
      <p>
        A 侧 {{ run.result.a.rolls }} 卷（{{ run.result.a.drops }} 条）
        · B 侧 {{ run.result.b.rolls }} 卷（{{ run.result.b.drops }} 条）
        · 差额 {{ run.result.delta_rolls }} 卷
      </p>
    </template>
    <template v-else>
      <p>单卷：{{ run.roll_name || '#' + run.result.roll_id }}</p>
      <p>{{ run.result.rolls }} 卷 · {{ run.result.drops }} 条 · 每条 {{ run.result.drop_len_m }}m</p>
    </template>
    <p v-if="run.note" class="run-note">备注：{{ run.note }}</p>
  </div>
</template>

<style scoped>
.run-detail { background: #fff; border: 1px dashed #6b4226; padding: 0.5rem 0.75rem; margin: 0.25rem 0 0.5rem; }
.run-detail p { margin: 0.25rem 0; }
.run-detail small { color: #6b4226; }
.run-note { color: #6b4226; }
</style>
