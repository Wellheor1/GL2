<template>
  <div v-tippy="V_TIPPY_PROPS">
    <span class="rps">{{ research.short_title || research.title }}</span>
    <div
      v-if="research.full_title || research.code || force_tippy || research.auto_deselect"
      :id="tid"
    >
      <div class="rtitle">
        {{ research.full_title || research.title }}
      </div>
      <span
        v-if="research.code"
        class="s-code"
      >{{ research.code }}</span>
      <span
        v-if="research.auto_deselect"
        class="auto-deselect"
      >шаблон назначений</span>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  name: 'ResearchPick',
  props: {
    research: {
      type: Object,
      required: true,
    },
    force_tippy: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    const tid = `research-pick-tip-${this.research.pk}-${Math.floor(Math.random() * 100000)}`;
    return {
      tid,
      V_TIPPY_PROPS: {
        html: `#${tid}`,
        reactive: true,
        arrow: true,
        delay: [500, 0],
        animation: 'fade',
        duration: 0,
        theme: 'light',
      },
    };
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

.s-code {
  font-size: 12px;
  margin-top: 5px;
}

.rtitle {
  font-size: 14px;
  max-width: 280px;
  text-align: justify;
  font-weight: 400;
}
</style>
