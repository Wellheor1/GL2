<template>
  <div v-frag>
    <div class="row">
      <div
        class="col-xs-6"
        style="padding-right: 0;"
      >
        <table class="table table-bordered table-condensed">
          <thead>
            <tr>
              <th colspan="2">
                М
              </th>
            </tr>
            <tr>
              <th>Возраст</th>
              <th>Значение</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in m"
              :key="row.key"
            >
              <td class="cl-td">
                <input
                  v-model="row.key"
                  type="text"
                  class="form-control"
                >
              </td>
              <td class="cl-td">
                <input
                  v-model="row.value"
                  type="text"
                  class="form-control"
                >
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div
        class="col-xs-6"
        style="padding-left: 0;"
      >
        <table class="table table-bordered table-condensed">
          <thead>
            <tr>
              <th colspan="2">
                Ж
              </th>
            </tr>
            <tr>
              <th>Возраст</th>
              <th>Значение</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in f"
              :key="row.key"
            >
              <td class="cl-td">
                <input
                  v-model.trim="row.key"
                  type="text"
                  class="form-control"
                >
              </td>
              <td class="cl-td">
                <input
                  v-model.trim="row.value"
                  type="text"
                  class="form-control"
                >
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <button
      class="btn btn-default btn-primary-nb btn-sm mt5"
      @click="addRefEmptyRow"
    >
      <i class="fa fa-plus" />
    </button>
  </div>
</template>

<script lang="ts">
export default {
  name: 'RefEditor',
  props: {
    reference: {},
  },
  data() {
    return {
      m: this.makeRows(this.reference.m),
      f: this.makeRows(this.reference.f),
    };
  },
  watch: {
    m: {
      deep: true,
      immediate: true,
      handler() {
        this.emit();
      },
    },
    f: {
      deep: true,
      immediate: true,
      handler() {
        this.emit();
      },
    },
  },
  mounted() {
    if (Object.keys(this.m).length === 0) {
      this.addRefEmptyRowToObj(this.m);
    }
    if (Object.keys(this.f).length === 0) {
      this.addRefEmptyRowToObj(this.f);
    }
  },
  methods: {
    emit() {
      // eslint-disable-next-line vue/no-mutating-props
      this.reference.m = this.makeObj(this.m);
      // eslint-disable-next-line vue/no-mutating-props
      this.reference.f = this.makeObj(this.f);
    },
    makeObj(o) {
      return o.reduce((a, b) => ({ [b.key]: b.value, ...a }), {});
    },
    makeRows(r) {
      return Object.keys(r).map((k) => ({ key: k, value: r[k] }));
    },
    addRefEmptyRow() {
      this.addRefEmptyRowToObj(this.m);
      this.addRefEmptyRowToObj(this.f);
    },
    addRefEmptyRowToObj(o) {
      if (!o.find((r) => r.key === '')) {
        o.push({ key: '', value: '' });
      }
    },
  },
};
</script>
