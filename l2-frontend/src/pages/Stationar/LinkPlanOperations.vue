<template>
  <a
    class="a-under"
    :href="`/ui/stationar#{%22pk%22:${direction},%22opened_list_key%22:null,%22opened_form_pk%22:null,%22every%22:false}`"
    @click="load"
  >
    И/б №{{ direction }}
  </a>
</template>

<script lang="ts">
export default {
  name: 'LinkPlanOperations',
  props: {
    direction: {
      type: String,
      required: true,
    },
  },
  methods: {
    load() {
      this.$root.$emit('open-history', this.direction);
    },
  },
};
</script>
