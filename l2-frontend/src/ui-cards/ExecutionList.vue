<template>
  <div v-frag>
    <a
      href="#"
      @click.prevent="doOpen"
    >
      Лист исполнения
    </a>
    <MountingPortal
      v-if="open"
      mount-to="#portal-place"
      name="ExecutionList"
      append
    >
      <Modal
        show-footer="true"
        white-bg="true"
        max-width="710px"
        width="100%"
        margin-left-right="auto"
        @close="open = false"
      >
        <span slot="header">Создание листа исполнения</span>
        <div slot="body">
          <div class="filters">
            <div class="date-filter">
              <div><strong>Дата приёма материала</strong></div>
              <DateRange v-model="date_range" />
            </div>
            <div style="margin-top: 10px">
              <ResearchesPicker
                v-model="selected_researches"
                autoselect="none"
                :just_search="true"
                :hidetemplates="true"
                style="border-top: 1px solid #eaeaea;border-bottom: 1px solid #eaeaea;height: 350px;"
                :types-only="[2]"
              />
            </div>
            <div style="margin-top: 10px">
              <button
                type="button"
                class="btn btn-primary-nb"
                style="margin-bottom: 10px"
                @click="createlist(3)"
              >
                Создать таблицу исполнения (по не подтверждённым)
              </button>
              <button
                type="button"
                class="btn btn-primary-nb"
                style="margin-bottom: 10px"
                @click="createlist(1)"
              >
                Создать лист по выбранному периоду
              </button>
            </div>
          </div>
        </div>
        <div slot="footer">
          <div class="row">
            <div class="col-xs-4">
              <button
                class="btn btn-primary-nb btn-blue-nb"
                type="button"
                @click="open = false"
              >
                Закрыть
              </button>
            </div>
          </div>
        </div>
      </Modal>
    </MountingPortal>
  </div>
</template>

<script lang="ts">
import moment from 'moment';

import Modal from '@/ui-cards/Modal.vue';
import DateRange from '@/ui-cards/DateRange.vue';
import ResearchesPicker from '@/ui-cards/ResearchesPicker.vue';

export default {
  name: 'ExecutionList',
  components: { ResearchesPicker, Modal, DateRange },
  data() {
    return {
      open: false,
      date_range: [moment().format('DD.MM.YYYY'), moment().format('DD.MM.YYYY')],
      selected_researches: [],
    };
  },
  methods: {
    doOpen() {
      this.open = true;
      this.selected_researches = [];
      this.date_range = [moment().format('DD.MM.YYYY'), moment().format('DD.MM.YYYY')];
    },
    createlist(type) {
      const [ds, de] = this.date_range;
      if (this.selected_researches.length === 0) {
        // @ts-ignore
        // eslint-disable-next-line no-undef
        window.$.amaran({
          theme: 'awesome wrn',
          content: {
            title: 'Создание невозможно',
            message: 'Ничего не выбрано',
            info: '',
            icon: 'fa fa-exclamation',
          },
          position: 'bottom right',
          delay: 6000,
        });
        return;
      }
      const res = JSON.stringify(this.selected_researches);
      switch (type) {
        case 3:
          window.open(`/mainmenu/receive/execlist?type=nonconfirmed&datestart=${ds}&dateend=${de}&researches=${res}`, '_blank');
          break;
        default:
          window.open(`/directions/execlist?type=${type}&datestart=${ds}&dateend=${de}&researches=${res}`, '_blank');
          break;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.date-filter {
  width: 182px;
}
</style>
