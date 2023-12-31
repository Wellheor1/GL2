<template>
  <div
    ref="root"
    class="split content root-content"
  >
    <div
      ref="ct"
      style="display: flex"
    >
      <div
        ref="tl"
        class="split content"
        style="padding: 0;"
      >
        <PatientPicker
          v-model="selected_card"
          directive_from_need="true"
          search_results="false"
          history_n="false"
          bottom_picker="true"
        >
          <div
            slot="for_card_bottom"
            class="bottom-inner"
          >
            <router-link
              v-if="can_create_directions && selected_card.pk !== -1"
              :to="directions_url"
            >
              <span>Создать направления</span>
            </router-link>
          </div>
        </PatientPicker>
      </div>
      <div
        ref="tr"
        class="split content"
        style="overflow: visible;display: flex;padding-bottom: 0"
      >
        <StatisticsTicketCreator
          :base="selected_card.base"
          :ofname="selected_card.ofname"
          :card_pk="selected_card.pk"
        />
      </div>
    </div>
    <div
      ref="cb"
      class="split content"
      style="padding: 0;"
    >
      <StatisticsTicketsViewer />
    </div>
  </div>
</template>

<script lang="ts">
import Split from 'split.js';

import PatientPicker from '@/ui-cards/PatientPicker.vue';
import StatisticsTicketCreator from '@/ui-cards/StatisticsTicketCreator.vue';
import StatisticsTicketsViewer from '@/ui-cards/StatisticsTicketsViewer.vue';

export default {
  name: 'StatisticsTickets',
  components: {
    PatientPicker,
    StatisticsTicketCreator,
    StatisticsTicketsViewer,
  },
  data() {
    return {
      selected_card: {
        pk: -1, base: {}, ofname: -1, ofname_dep: -1, operator: false, history_num: '',
      },
    };
  },
  computed: {
    directions_url() {
      return {
        name: 'directions',
        query: {
          base_pk: this.selected_card.base.pk,
          card_pk: this.selected_card.pk,
          ofname: this.selected_card.ofname,
          ofname_dep: this.selected_card.ofname_dep,
        },
      };
    },
    can_create_directions() {
      if ('groups' in this.$store.getters.user_data) {
        for (const g of this.$store.getters.user_data.groups) {
          if (g === 'Лечащий врач' || g === 'Оператор лечащего врача') {
            return true;
          }
        }
      }
      return false;
    },
  },
  mounted() {
    window.$(document).ready(() => {
      this.resize();
      window.$(window).resize(() => {
        this.resize();
      });

      Split([this.$refs.ct, this.$refs.cb], {
        direction: 'vertical',
        gutterSize: 5,
        cursor: 'row-resize',
        minSize: 200,
        sizes: [45, 55],
        onDrag: () => this.resize,
      });

      Split([this.$refs.tl, this.$refs.tr], {
        gutterSize: 5,
        cursor: 'col-resize',
        minSize: 200,
        onDrag: () => this.resize,
        elementStyle(dimension, size, gutterSize) {
          return {
            'flex-basis': `calc(${size}% - ${gutterSize}px)`,
          };
        },
        gutterStyle(dimension, gutterSize) {
          return {
            'flex-basis': `${gutterSize}px`,
          };
        },
      });
    });
  },
  methods: {
    resize() {
      const $fp = window.$(this.$refs.root);
      $fp.height(window.$(window).height() - $fp.position().top - 11);
    },
  },
};
</script>

<style scoped lang="scss">
.root-content {
  position: absolute;
  top: 36px;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
