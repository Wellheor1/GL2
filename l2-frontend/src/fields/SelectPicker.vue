<template>
  <select
    v-selectpicker
    class="selectpicker"
    data-width="100%"
    :multiple="multiple"
    :data-actions-box="actions_box"
    :data-none-selected-text="noneText"
    data-select-all-text="Выбрать всё"
    :data-deselect-all-text="deselectText"
    data-live-search="true"
    :data-container="dataContainer"
  >
    <option
      v-for="option in options"
      :key="option.value"
      :value="option.value"
      :selected="option.value === val"
    >
      {{ option.label }}
    </option>
  </select>
</template>

<script lang="ts">
export default {
  name: 'SelectPicker',
  directives: {
    selectpicker: {
      bind(el, binding, vnode) {
        const $el = window.$(el).parent().children('select');
        let v = vnode.context.val;
        if (v === '-1' || !v) {
          if (vnode.context.multiple) v = [];
          else if (vnode.context.options.length > 0) v = vnode.context.options[0].value;
          else v = '';
        }
        if (vnode.context.multiple && !Array.isArray(v)) {
          v = v.split(',');
        } else if (!vnode.context.multiple && typeof v !== 'string' && !(v instanceof String)) {
          v = v.toString();
        }
        $el.selectpicker('val', v);
        vnode.context.update_val(v);
        window.$(el).change(function () {
          const lval = window.$(this).selectpicker('val');
          vnode.context.update_val(lval);
        });
      },
    },
  },
  props: {
    options: {
      type: Array,
      required: true,
    },
    val: {},
    func: {
      type: Function,
      required: true,
    },
    multiple: {
      type: Boolean,
      default: false,
    },
    actions_box: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    noneText: {
      type: String,
      default: 'Ничего не выбрано',
    },
    deselectText: {
      type: String,
      default: 'Отменить весь выбор',
    },
    dataContainer: {
      default: null,
    },
  },
  watch: {
    disabled: {
      immediate: true,
      handler() {
        window.$(this.$el).parent().children('select').prop('disabled', this.disabled)
          .selectpicker('refresh');
      },
    },
  },
  created() {
    this.update_val(this.val);
  },
  methods: {
    update_val(v) {
      this.func(v);
    },
  },
};
</script>
