<template>
  <div>
    <span class="rps">
      {{ category.title }}<span v-if="category.selected > 0"> ({{ category.selected }})</span>
    </span>
  </div>
</template>

<script lang="ts">
export default {
  name: 'CategoryPick',
  props: {
    category: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style scoped>
.rps {
  display: block;
  text-overflow: ellipsis;
  overflow: hidden;
  word-break: keep-all;
  max-height: 2.2em;
  line-height: 1.1em;
  cursor: pointer;
}
</style>
