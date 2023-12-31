<template>
  <div>
    <div class="input-group">
      <input
        v-model="query"
        type="text"
        class="form-control"
        placeholder="Введите запрос"
        autofocus
        maxlength="255"
        @keyup.enter="search"
      >
      <span class="input-group-btn"><button
        style="margin-right: -2px"
        class="btn last btn-blue-nb"
        type="button"
        :disabled="!query_valid || inLoading"
        @click="search"
      >Поиск</button></span>
    </div>

    <table class="table table-bordered">
      <colgroup>
        <col width="127">
        <col>
      </colgroup>
      <tbody>
        <tr>
          <td
            style="max-width: 127px;"
            class="table-header-row"
          >
            ФИО:
          </td>
          <td
            style="max-width: 99%;"
            class="table-content-row"
          >
            {{ selected_individual.family }}
            {{ selected_individual.name }}
            {{ selected_individual.patronymic }}
          </td>
        </tr>
        <tr>
          <td
            style="max-width: 127px;"
            class="table-header-row"
          >
            Пол:
          </td>
          <td
            style="max-width: 99%;"
            class="table-content-row"
          >
            {{ selected_individual.sex }}
          </td>
        </tr>
        <tr>
          <td class="table-header-row">
            Дата рождения:
          </td>
          <td class="table-content-row">
            {{ selected_individual.birthday }}
          </td>
        </tr>
        <tr>
          <td class="table-header-row">
            Возраст:
          </td>
          <td class="table-content-row">
            {{ selected_individual.age }}
          </td>
        </tr>
      </tbody>
    </table>
    <slot
      v-if="loaded"
      name="for_card"
      style="margin-top: 5px"
    >
      <div class="text-right">
        <a
          v-if="return_base && return_card"
          :href="directions_url"
          class="fli"
        >Вернуться в направления</a>
      </div>
    </slot>
    <slot
      name="for_all"
      style="margin-top: 5px"
    />
    <Modal
      v-show="showModal"
      ref="modal"
      show-footer="true"
      @close="hide_modal"
    >
      <span slot="header">Найдено несколько пациентов</span>
      <div slot="body">
        <table
          class="table table-responsive table-bordered table-hover"
          style="background-color: #fff;max-width: 650px"
        >
          <colgroup>
            <col>
            <col width="40">
            <col width="140">
            <col width="120">
          </colgroup>
          <thead>
            <tr>
              <th>ФИО</th>
              <th class="text-center">
                Пол
              </th>
              <th class="text-center">
                Дата рождения
              </th>
              <th>Возраст</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, i) in founded_individuals"
              :key="row.pk"
              class="cursor-pointer"
              @click="select_individual(i)"
            >
              <td>{{ row.family }} {{ row.name }} {{ row.patronymic }}</td>
              <td class="text-center">
                {{ row.sex }}
              </td>
              <td class="text-center">
                {{ row.birthday }}
              </td>
              <td>{{ row.age }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div
        slot="footer"
        class="text-center"
      >
        <small>Показано не более 25-и записей</small>
      </div>
    </Modal>
  </div>
</template>

<script lang="ts">
import * as actions from '@/store/action-types';
import patientsPoint from '@/api/patients-point';

import Modal from './Modal.vue';

export default {
  name: 'IndividualPicker',
  components: { Modal },
  props: {
    directive_from_need: {
      default: 'false',
      type: String,
    },
    search_results: {
      default: 'false',
      type: String,
    },
    history_n: {
      default: 'true',
      type: String,
    },
    value: {},
  },
  data() {
    return {
      query: '',
      search_type: 'auto',
      showModal: false,
      founded_individuals: [],
      selected_individual: {},
      loaded: false,
      search_after_loading: false,
      return_base: null,
      return_card: null,
    };
  },
  computed: {
    directions_url() {
      return `/ui/directions?base_pk=${this.return_base}&card_pk=${this.return_card}`;
    },
    normalized_query() {
      return this.query.trim();
    },
    query_valid() {
      return this.normalized_query.length > 1;
    },
    inLoading() {
      return this.$store.getters.inLoading;
    },
  },
  watch: {
    inLoading() {
      if (!this.inLoading && this.search_after_loading) {
        this.search();
      }
    },
  },
  created() {
    const params = new URLSearchParams(window.location.search);
    const individualPk = params.get('individual_pk');
    const basePk = params.get('base_pk');
    const cardPk = params.get('card_pk');
    if (individualPk) {
      window.history.pushState('', '', window.location.href.split('?')[0]);
      this.query = `individual_pk:${individualPk}`;
      this.search_after_loading = true;
      if (basePk && cardPk) {
        this.return_base = basePk;
        this.return_card = cardPk;
      }
    }

    this.$root.$on('search', () => {
      this.search();
    });
  },
  methods: {
    hide_modal() {
      this.showModal = false;
      if (this.$refs.modal) {
        this.$refs.modal.$el.style.display = 'none';
      }
    },
    select_individual(index) {
      this.hide_modal();
      this.selected_individual = this.founded_individuals[index];
      this.emit_input();
      this.loaded = true;
    },
    emit_input() {
      let pk = -1;
      if ('pk' in this.selected_individual) pk = this.selected_individual.pk;
      this.$emit('input', pk);
    },
    clear() {
      this.loaded = false;
      this.selected_individual = {};
      this.founded_individuals = [];
      if (this.query.includes('individual_pk:')) {
        this.query = '';
      }
      this.emit_input();
    },
    search() {
      this.search_after_loading = false;
      if (!this.query_valid || this.inLoading) return;
      window.$('input').each(function () {
        window.$(this).trigger('blur');
      });
      if (!this.query.includes('individual_pk:')) {
        this.return_base = null;
        this.return_card = null;
      }
      this.$store.dispatch(actions.ENABLE_LOADING, { loadingLabel: 'Поиск пациента' });
      patientsPoint.searchIndividual(this, 'query').then((result) => {
        this.clear();
        if (result.results) {
          this.founded_individuals = result.results;
          if (this.founded_individuals.length > 1) {
            this.$refs.modal.$el.style.display = 'flex';
            this.showModal = true;
          } else if (this.founded_individuals.length === 1) {
            this.select_individual(0);
          } else {
            this.$root.$emit('msg', 'error', 'Пациентов по такому запросу не найдено');
          }
        } else {
          this.$root.$emit('msg', 'error', 'Ошибка на сервере');
        }
      }).catch((error) => {
        this.$root.$emit('msg', 'error', `Ошибка на сервере\n${error.message}`);
      }).finally(() => {
        this.$store.dispatch(actions.DISABLE_LOADING);
      });
    },
  },
};
</script>

<style scoped lang="scss">
  table {
    table-layout: fixed;
    padding: 0;
    margin: 5px 0 0;
  }

  td:not(.select-td) {
    padding: 2px !important;
  }

  .table-header-row {
    font-weight: bolder;
    overflow: hidden;
    text-overflow: ellipsis;
    vertical-align: middle;
  }

  .table-content-row {
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>

<style lang="scss">
  .select-td {
    padding: 0 !important;

    .bootstrap-select {
      height: 38px;
      display: flex !important;
      button {
        border: none !important;
        border-radius: 0 !important;
        .filter-option {
          text-overflow: ellipsis;
        }
      }
    }
  }

  .fli {
    text-decoration: underline;
    margin-left: 5px;
  }

  .fli:hover {
    text-decoration: none;
  }
</style>
