<template>
  <tr
    :class="{
      'cancel-row': data.canceled,
      'approved-row': data.status === 3,
      'patient-created': data.created_by_patient && data.status !== 3,
    }"
  >
    <td
      v-tippy="vtp"
      :title="data.tooltip_data"
    >
      {{ data.date }}
      <a
        href="#"
        class="a-under"
        @click.prevent="open_messages_data(data.pk_plan, data.patient_card)"
      >
        Сообщения: {{ data.messages.count }}</a>
    </td>
    <td
      v-tippy="vtp"
      :title="data.tooltip_data"
    >
      {{ data.fio_patient }}<br>
      {{ data.phone }}
      <div
        v-for="row of data.uploaded_file"
        :key="row.file"
      >
        <i class="fas fa-file-download" />
        <a
          :href="row.file"
          target="_blank"
          class="a-under"
        >
          {{ row.fileName }}
        </a>
      </div>
    </td>
    <td
      v-tippy="vtp"
      :title="data.tooltip_data"
    >
      <div>{{ data.research_title }}</div>
      <div v-if="data.depart_title">
        — {{ data.depart_title }}
      </div>
    </td>
    <td
      v-tippy="vtp"
      :title="data.tooltip_data"
    >
      {{ data.diagnos }}
    </td>
    <td
      v-tippy="vtp"
      :title="data.tooltip_data"
      class="td-comment"
    >
      {{ data.comment }}
    </td>
    <td>
      <template v-if="!data.canceled && data.status !== 3">
        <HospPlanScheduleButton :data="data" />
        <div class="spacer" />
        <HospPlanCancelButton :data="data" />
      </template>
      <template v-else-if="data.slot">
        {{ data.slot }}
      </template>
    </td>
  </tr>
</template>

<script lang="ts">
import HospPlanScheduleButton from '@/ui-cards/HospPlanScheduleButton.vue';
import HospPlanCancelButton from '@/ui-cards/HospPlanCancelButton.vue';

export default {
  name: 'Row',
  components: {
    HospPlanScheduleButton,
    HospPlanCancelButton,
  },
  props: {
    data: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      vtp: {
        placement: 'top',
        arrow: true,
        interactive: true,
        theme: 'dark longread',
      },
    };
  },
  methods: {
    open_messages_data(pk, card) {
      this.$root.$emit('open_messages_data', { pk, card });
    },
  },
};
</script>

<style scoped lang="scss">
.cancel-row {
  td,
  th {
    opacity: 0.6;
    text-decoration: line-through;
    background-color: linen;
  }

  &:hover {
    td,
    th {
      opacity: 1;
      text-decoration: none;
    }
  }
}

.approved-row {
  td,
  th {
    background-color: #a9cfbb;
  }
}

.patient-created {
  td,
  th {
    background-color: #e2effb;
    opacity: 0.8;
  }
}

.td-comment {
  white-space: pre-wrap;
}
</style>
