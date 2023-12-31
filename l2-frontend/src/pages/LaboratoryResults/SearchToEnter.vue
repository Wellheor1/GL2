<template>
  <div>
    <div class="filters">
      <form
        autocomplete="off"
        @submit.prevent
      >
        <input
          autocomplete="false"
          name="hidden"
          type="text"
          style="display: none;"
        >
        <div class="input-group">
          <span
            v-for="(title, key) in modes"
            :key="`${key}-${title}`"
            class="input-group-btn"
          >
            <a
              href="#"
              class="top-inner-select"
              :class="key === mode && 'active'"
              @click.prevent="mode = key"
            >
              <span>{{ title }}</span>
            </a>
          </span>
          <input
            ref="q"
            v-model="q"
            type="text"
            maxlength="13"
            class="form-control"
            autofocus
            :placeholder="mode === 'direction' ? 'номер направления' : 'номер ёмкости'"
            @keyup.enter="search"
          >
          <span class="input-group-btn">
            <button
              style="margin-right: -1px;"
              type="button"
              class="btn btn-blue-nb"
              @click="search"
            >Поиск</button>
          </span>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { SEARCH_MODES, SEARCH_MODES_TITLES } from '@/pages/LaboratoryResults/constants';
import * as actions from '@/store/action-types';

export default {
  name: 'SearchToEnter',
  props: {
    laboratory: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      mode: SEARCH_MODES.DIRECTION,
      modes: SEARCH_MODES_TITLES,
      q: '',
      pkAfterSearch: null,
    };
  },
  watch: {
    mode() {
      window.$(this.$refs.q).focus();
    },
    q() {
      this.q = this.q.replace(/\D/g, '');
    },
  },
  mounted() {
    this.$root.$on('laboratory:results:search', (mode, pk, pkAfterSearch) => {
      this.mode = mode;
      this.q = String(pk);
      this.pkAfterSearch = pkAfterSearch;
      this.search();
    });
  },
  methods: {
    async search() {
      await this.$store.dispatch(actions.INC_LOADING);
      const { ok, data, msg } = await this.$api('laboratory/search', this, ['q', 'mode', 'laboratory']);
      if (ok) {
        this.q = '';
        this.$root.$emit('laboratory:results:show-direction', data, this.pkAfterSearch);
        this.pkAfterSearch = null;
      } else {
        this.$root.$emit('msg', 'error', msg || 'Не найдено');
      }
      await this.$store.dispatch(actions.DEC_LOADING);
    },
  },
};
</script>

<style scoped lang="scss">
.filters {
  background-color: #edeeef;

  form {
    .btn,
    .form-control,
    .top-inner-select {
      border-radius: 0 !important;
      padding: 6px 4px !important;
      font-size: 12px;
      height: 34px;
    }
  }
}

.top-inner-select {
  align-self: stretch;
  display: flex;
  align-items: center;
  text-decoration: none;
  cursor: pointer;
  flex: 1;
  margin: 0;
  font-size: 12px;
  min-width: 0;
  background-color: #aab2bd;
  color: #fff;

  &:hover {
    background-color: #434a54;
  }

  &.active {
    background: #8d98a7 !important;
    color: #fff;
  }

  &.disabled {
    color: #fff;
    cursor: not-allowed;
    opacity: 0.8;
    background-color: rgba(255, 255, 255, 0.7) !important;
  }

  span {
    display: block;
    text-overflow: ellipsis;
    overflow: hidden;
    word-break: keep-all;
    max-height: 2.2em;
    line-height: 1.1em;
    margin: 0 auto;
  }
}
</style>
