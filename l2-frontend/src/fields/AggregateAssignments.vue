<template>
  <div>
    <div class="print-div">
      <div class="button">
        <button
          v-tippy
          title="печать"
          class="btn last btn-blue-nb"
          @click="printForm"
        >
          печать
        </button>
      </div>
    </div>
    <div>
      <VeTable
        :columns="columns"
        :table-data="assignments"
      />
      <div
        v-show="assignments.length === 0"
        class="empty-list"
      >
        Нет записей
      </div>
      <div class="flex-space-between">
        <VePagination
          :total="assignments.length"
          :page-index="page"
          :page-size="pageSize"
          :page-size-option="pageSizeOption"
          @on-page-number-change="pageNumberChange"
          @on-page-size-change="pageSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  onMounted, ref,
} from 'vue';
import {
  VeLocale,
  VePagination,
  VeTable,
} from 'vue-easytable';

import 'vue-easytable/libs/theme-default/index.css';
import * as actions from '@/store/action-types';
import api from '@/api';
import { useStore } from '@/store';
import ruRu from '@/locales/ve';

VeLocale.use(ruRu);

const props = defineProps<{
  direction: number;
}>();

const columns = ref([
  {
    field: 'direction_id', key: 'direction_id', title: '№ напр.', width: 100,
  },
  {
    field: 'research_title', key: 'research_title', title: 'Медицинское вмешательство', align: 'left',
  },
  {
    field: 'create_date', key: 'create_date', title: 'Дата назначения', align: 'center', width: 150,
  },
  {
    field: 'who_assigned', key: 'who_assigned', title: 'ФИО назначившего', align: 'center', width: 200,
  },
  {
    field: 'time_confirmation', key: 'time_confirmation', title: 'Дата и время подтверждения', align: 'center', width: 150,
  },
  {
    field: 'who_confirm', key: 'who_confirm', title: 'ФИО подтвердившего', align: 'center', width: 200,
  },
]);
const store = useStore();
const pageSize = ref(30);
const page = ref(1);
const pageSizeOption = ref([30, 50, 100, 300]);
const pageNumberChange = (number: number) => {
  page.value = number;
};
const pageSizeChange = (size: number) => {
  pageSize.value = size;
};
const assignments = ref([]);

const getAssignments = async () => {
  await store.dispatch(actions.INC_LOADING);
  const results = await api('stationar/get-assignments', { direction_id: props.direction });
  await store.dispatch(actions.DEC_LOADING);
  assignments.value = results.data;
};

const printForm = () => {
  window.open(`/forms/pdf?type=107.03&&hosp_pk=${props.direction}`);
};

onMounted(getAssignments);

</script>

<style scoped>
.empty-list {
  width: 85px;
  margin: 20px auto;
}
.flex-space-between {
  display: flex;
  justify-content: space-between;
}
.print-div {
  width: 75px;
  margin-bottom: 5px;
}
.button {
  width: 100%;
  display: flex;
  flex-wrap: nowrap;
  flex-direction: row;
  justify-content: stretch;
}
.btn {
  align-self: stretch;
  flex: 1;
  padding: 6px 0;
}
</style>
