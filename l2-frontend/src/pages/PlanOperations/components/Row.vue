<template>
  <tr :class="{ 'cancel-row': data.canceled && !edit_plan_operation }">
    <td>
      {{ data.date }}
    </td>
    <td>
      <a
        :href="directionHref"
        target="_blank"
        class="a-under"
      >
        {{ data.direction }}
      </a>
    </td>
    <td>{{ data.fio_patient }} <br>{{ data.birthday }}<br>{{ data.weight }}</td>
    <td>
      {{ data.type_operation }}
    </td>
    <td>
      {{ hirurgs[data.doc_operate_id].label }}
    </td>
    <td>
      {{ hirurgs[data.doc_operate_id].podr }}
    </td>
    <td>
      <Treeselect
        v-model="/* eslint-disable-line vue/no-mutating-props */ data.doc_anesthetist_id"
        :multiple="false"
        :disable-branch-nodes="true"
        :options="anestesiologs"
        placeholder="Анестезиолог не выбран"
        :disabled="!can_edit_anestesiologs"
        :append-to-body="true"
      />
    </td>
    <td>
      <button
        v-tippy
        title="Редактирование"
        class="btn btn-blue-nb"
        type="button"
        tabindex="-1"
        :disabled="!can_edit_operations"
        @click="edit_plan_operation = true"
      >
        <i class="fa fa-pencil" />
      </button>
      <PlanOperationEdit
        v-if="edit_plan_operation"
        :pk_plan="data.pk_plan"
        :pk_hirurg="data.doc_operate_id"
        :date="data.date_raw"
        :operation="data.type_operation"
        :direction="data.direction"
        :patient_fio="`${data.fio_patient}, ${data.birthday}`"
        :card_pk="data.patient_card"
        :cancel_operation="data.canceled"
      />
    </td>
  </tr>
</template>

<script lang="ts">
import Treeselect from '@riophae/vue-treeselect';

import '@riophae/vue-treeselect/dist/vue-treeselect.css';
import * as actions from '@/store/action-types';
import plansPoint from '@/api/plans-point';

import PlanOperationEdit from '../../../modals/PlanOperationEdit.vue';

export default {
  name: 'Row',
  components: { PlanOperationEdit, Treeselect },
  props: {
    data: {
      type: Object,
      required: true,
    },
    hirurgs: {
      type: Object,
      required: true,
    },
    anestesiologs: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      edit_plan_operation: false,
    };
  },
  computed: {
    anestesiologId() {
      return this.data.doc_anesthetist_id;
    },
    can_edit_operations() {
      return (this.$store.getters.user_data.groups || []).includes('Управление планами операций');
    },
    can_edit_anestesiologs() {
      return (this.$store.getters.user_data.groups || []).includes('Управление анестезиологами');
    },
    directionHref() {
      // eslint-disable-next-line max-len
      return `/ui/stationar#{%22pk%22:${this.data.direction},%22opened_list_key%22:null,%22opened_form_pk%22:null,%22every%22:false}`;
    },
  },
  watch: {
    async anestesiologId() {
      await this.$store.dispatch(actions.INC_LOADING);
      await plansPoint.changeAnestesiolog({
        plan_pk: this.data.pk_plan,
        doc_anesthetist_pk: this.anestesiologId,
      });
      this.$root.$emit('msg', 'ok', 'Анестезиолог изменён');
      await this.$store.dispatch(actions.DEC_LOADING);
    },
  },
  mounted() {
    this.$root.$on('hide_plan_operations', () => {
      this.edit_plan_operation = false;
    });
  },
};
</script>

<style scoped lang="scss">
.cancel-row {
  td,
  th {
    opacity: 0.6;
    text-decoration: line-through;
  }

  &:hover {
    td,
    th {
      opacity: 1;
      text-decoration: none;
    }
  }
}
</style>
