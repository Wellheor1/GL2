<template>
  <input
    v-model="val"
    v-datepicker
    type="text"
    class="form-control no-context"
    maxlength="10"
  >
</template>

<script lang="ts">
export default {
  name: 'DateField',
  directives: {
    datepicker: {
      bind(el, binding, vnode) {
        window.$(el).datepicker({
          format: 'dd.mm.yyyy',
          todayBtn: 'linked',
          language: 'ru',
          autoclose: true,
          todayHighlight: true,
          enableOnReadonly: true,
          orientation: 'top left',
        }).on('changeDate', () => {
          // eslint-disable-next-line no-param-reassign
          vnode.context.val = window.$(el).val();
          vnode.context.$emit('update:val', window.$(el).val());
        });
      },
    },
  },
  props: {
    def: {
      type: String,
      required: false,
      default: '',
    },
  },
  data() {
    return {
      val: this.def,
    };
  },
};
</script>

<style scoped>
  .form-control {
    padding-left: 2px;
    padding-right: 2px;
    text-align: center;
  }
</style>
