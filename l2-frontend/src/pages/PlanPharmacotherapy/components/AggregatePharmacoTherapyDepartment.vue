<template>
  <div class="root-agg">
    <div
      v-for="rr in rows"
      :key="rr.pk"
    >
      <table class="table table-responsive table-bordered table-condensed">
        <colgroup>
          <col width="200">
          <col width="300">
          <col
            v-for="d in dates"
            :key="d"
          >
        </colgroup>
        <thead>
          <tr>
            <th
              rowspan="2"
              class="first-cell"
            >
              Пациент
            </th>
            <th
              rowspan="2"
              class="second-cell"
            >
              Наименование ЛП
            </th>
            <th
              v-for="d in dates"
              :key="d"
            >
              {{ d }}
            </th>
          </tr>
          <tr>
            <th
              v-for="d in dates"
              :key="d"
              class="cl-td"
            >
              <div
                v-for="t in timesInDates[d]"
                :key="t"
                class="time"
                :data-datetime="`${d} ${t}`"
              >
                {{ t.split(':')[0] }}
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="r in rr.drugs"
            :key="r.pk"
          >
            <td
              class="patient"
              :class="{ cancel: r.cancel }"
            >
              {{ rr.patient.fio }}, история {{ r.history_num }}
            </td>
            <td>
              <div
                class="drug"
                :class="{ cancel: r.cancel }"
              >
                {{ r.drug }}
              </div>
              <span
                v-tippy
                class="badge badge-primary"
                title="Форма выпуска"
              >{{ r.form_release }}</span>
              <span
                v-tippy
                class="badge badge-primary"
                title="Способ применения"
              >{{ r.method }}</span>
              <span
                v-tippy
                class="badge badge-info"
                title="Дозировка"
              >{{ r.dosage }}</span>
              <span
                v-tippy
                class="badge badge-light"
                title="Дата создания"
              >{{ r.created_at }}</span>
              <span
                v-if="r.step > 1"
                v-tippy
                class="badge badge-warning"
                title="Шаг дней"
              >шаг {{ r.step }} дн</span>
              <template v-if="can_cancel">
                <a
                  v-if="!r.cancel"
                  class="badge badge-secondary"
                  href="#"
                  @click.prevent="cancelRow(r.pk, true)"
                >
                  <i class="fa fa-circle" /> отменить ЛП
                </a>
                <a
                  v-else
                  class="badge badge-secondary"
                  href="#"
                  @click.prevent="cancelRow(r.pk, false)"
                >
                  <i class="fa fa-circle" /> вернуть ЛП
                </a>
              </template>
              <div v-if="r.comment">
                <strong>Комментарий:</strong>&nbsp;{{ r.comment }}
              </div>
            </td>
            <td
              v-for="d in dates"
              :key="d"
              class="cl-td"
            >
              <PharmacotherapyTime
                v-for="t in timesInDates[d]"
                :key="t"
                :data="r.dates[d][t]"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script lang="ts">
import PharmacotherapyTime from '@/fields/PharmacotherapyTime.vue';
import * as actions from '@/store/action-types';

export default {
  name: 'AggregatePharmacoTherapyDepartment',
  components: { PharmacotherapyTime },
  props: {
    direction: {},
    department_pk: null,
    dateRange: null,
  },
  data() {
    return {
      rows: [],
      dates: [],
      times: [],
      timesInDates: {},
      dates_aggregate: '',
    };
  },
  computed: {
    can_cancel() {
      for (const g of this.$store.getters.user_data.groups || []) {
        if (g === 'Врач стационара' || g === 'Admin') {
          return true;
        }
      }
      return false;
    },
  },
  watch: {
    dateRange: {
      handler() {
        this.dates_aggregate = this.dateRange.split('x');
        this.load();
      },
    },
    department_pk: {
      handler() {
        this.load();
      },
    },
  },
  async mounted() {
    this.dates_aggregate = this.dateRange.split('x');
    this.load();
    this.$root.$on('pharmacotherapy-aggregation:reload', () => this.load());
    window.$('.root-agg').on('mouseover mouseout', '[data-datetime]', event => {
      const t$ = window.$(event.target);
      const all$ = window.$(`[data-datetime="${t$.data('datetime')}"]`);
      if (event.type === 'mouseover') {
        all$.addClass('datetime-hover');
      } else {
        all$.removeClass('datetime-hover');
      }
    });
  },
  beforeDestroy() {
    window.$('.root-agg [data-datetime]').off('mouseover mouseout');
  },
  methods: {
    async load() {
      const {
        result, dates, times, timesInDates,
      } = await this.$api('procedural-list/department-procedures', {
        start_date: this.dates_aggregate[0],
        end_date: this.dates_aggregate[1],
        department_pk: this.department_pk,
      });
      this.rows = result;
      this.dates = dates;
      this.times = times;
      this.timesInDates = timesInDates;
      await this.$store.dispatch(actions.DEC_LOADING);
    },
    async cancelRow(pk, cancel) {
      if (cancel) {
        try {
          await this.$dialog.confirm('Вы действительно хотите отменить назначение?');
        } catch (_) {
          return;
        }
      } else {
        try {
          await this.$dialog.confirm('Вы действительно хотите вернуть назначение?');
        } catch (_) {
          return;
        }
      }
      await this.$store.dispatch(actions.INC_LOADING);
      const { ok, message } = await this.$api('procedural-list/procedure-cancel', { pk, cancel });
      if (ok) {
        this.$root.$emit('msg', 'ok', message);
        this.$root.$emit('pharmacotherapy-aggregation:reload');
      } else {
        this.$root.$emit('msg', 'error', message);
      }
      await this.$store.dispatch(actions.DEC_LOADING);
    },
  },
};
</script>

<style scoped lang="scss">
.time {
  display: inline-block;
  width: 30px;
  text-align: center;
  height: 24px;
  font-weight: normal;
  font-size: 12px;
  vertical-align: bottom;
}

.root-agg {
  overflow-x: auto;
}

a.badge:hover {
  background-color: #5f6267;
}

table {
  table-layout: fixed;
  min-width: 100%;
  max-width: none;
  width: auto;

  .cl-td {
    white-space: nowrap;
  }
}

.drug.cancel:not(:hover) {
  text-decoration: line-through;
}

.patient.cancel:not(:hover) {
  text-decoration: line-through;
}

.root-agg {
  position: relative;
}

.table tr > td:first-child,
.table .first-cell,
.table tr > td:nth-child(2),
.table .second-cell {
  background-color: white;
  position: sticky;
  z-index: 2;
  box-shadow: 2px 0 2px rgba(0, 0, 0, 0.1);
}
.table tr > td:first-child,
.table .first-cell {
  left: 0;
  min-width: 200px;
}

.table tr > td:nth-child(2),
.table .second-cell {
  left: 201px;
  min-width: 300px;
}
</style>
