<template>
  <li>
    <a
      href="#"
      @click.prevent="doOpen"
    > Создать направление </a>
    <Modal
      v-if="open"
      ref="modal"
      show-footer="true"
      white-bg="true"
      max-width="1600px"
      width="100%"
      margin-left-right="41px"
      margin-top
      class="an"
      @close="hide_window"
    >
      <span slot="header">Создать направление</span>
      <div
        slot="body"
        class="an-body"
      >
        <div class="d-root">
          <div>
            <div class="overflow-visible">
              <PatientPicker
                v-model="selected_card"
                history_n="false"
                :hide_card_editor="true"
              />
            </div>
          </div>
          <div>
            <div />
          </div>
          <div>
            <div>
              <ResearchesPicker
                v-model="research"
                :hidetemplates="true"
                :oneselect="true"
                :autoselect="false"
                :types-only="[4, 3, 11]"
                kk="cdd"
                :just_search="true"
              />
            </div>
          </div>
          <div>
            <div>
              <SelectedResearches
                :researches="research ? [research] : []"
                :card_pk="card_pk"
                :selected_card="selected_card"
                :valid="true"
                :hide_diagnosis="true"
                :hide_params="true"
                :create_and_open="true"
                kk="cdd"
                :base="bases_obj[internal_base]"
              />
            </div>
          </div>
        </div>
      </div>
      <div slot="footer">
        <div class="row">
          <div class="col-xs-4">
            <button
              class="btn btn-primary-nb btn-blue-nb"
              type="button"
              @click="hide_window"
            >
              Закрыть
            </button>
          </div>
        </div>
      </div>
    </Modal>
  </li>
</template>

<script lang="ts">
import { mapGetters } from 'vuex';

import Modal from '@/ui-cards/Modal.vue';
import ResearchesPicker from '@/ui-cards/ResearchesPicker.vue';
import SelectedResearches from '@/ui-cards/SelectedResearches.vue';
import PatientPicker from '@/ui-cards/PatientPicker.vue';

export default {
  name: 'CreateDescriptiveDirection',
  components: {
    PatientPicker,
    SelectedResearches,
    ResearchesPicker,
    Modal,
  },
  data() {
    return {
      open: false,
      args_to_preselect: null,
      selected_card: {},
      research: null,
    };
  },
  computed: {
    card_pk() {
      return this.selected_card.pk || null;
    },
    ...mapGetters({
      bases: 'bases',
    }),
    bases_obj() {
      return this.bases.reduce(
        (a, b) => ({
          ...a,
          [b.pk]: b,
        }),
        {},
      );
    },
    internal_base() {
      for (const b of this.bases) {
        if (b.internal_type) {
          return b.pk;
        }
      }
      return -1;
    },
  },
  mounted() {
    this.$root.$on('preselect-args', (data) => {
      if (!data) {
        this.args_to_preselect = null;
      } else {
        this.args_to_preselect = data;
      }
    });
    this.$root.$emit('preselect-args-ok');
    this.$root.$on('open-direction-form', () => this.hide_window());
  },
  methods: {
    doOpen() {
      this.open = true;
      if (this.args_to_preselect) {
        const data = { ...this.args_to_preselect, hide: true };
        setTimeout(() => this.$root.$emit('select_card', data), 100);
      }
      this.$root.$emit('no-loader-in-header', true);
    },
    hide_window() {
      this.open = false;
      this.research = null;
      this.selected_card = {};
      this.$root.$emit('no-loader-in-header', false);
      if (this.$refs.modal) {
        this.$refs.modal.$el.style.display = 'none';
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.an-body {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  display: block;
}

.an-body > div {
  align-self: stretch;
}

.d-root {
  height: 100%;
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;

  > div {
    flex-basis: calc(50% - 8px);
    margin: 4px;

    > div {
      height: 100%;
      border: 1px solid rgba(0, 0, 0, 0.3);
      overflow-x: hidden;
      overflow-y: auto;

      &.overflow-visible {
        overflow: visible;
      }
    }
  }
}
</style>
