<template>
  <div v-if="visible">
    <slot />
  </div>
</template>

<script lang="ts">
import { vField } from './visibility-triggers';

export default {
  name: 'VisibilityFieldWrapper',
  props: ['group', 'groups', 'formula', 'patient'],
  computed: {
    visible() {
      return vField(this.group, this.groups, this.formula, this.patient);
    },
  },
};
</script>
