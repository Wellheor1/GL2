<template>
  <div class="chats-body">
    <div class="chats-body__header">
      <div
        v-if="!search"
        class="chats-body__header-title"
      >
        <template v-if="forSelect">
          Выберите пользователей
        </template>
        <template v-else>
          L2.Сообщения
        </template>
        <div
          class="chats-body__header-search"
          @click="openSearch"
        >
          <i class="fa fa-search" />
        </div>
        <template v-if="!forSelect">
          <div
            v-tippy
            class="chats-body__header-alerts"
            :title="`Уведомления: ${alertsEnabled ? 'включены' : 'выключены'}`"
            @click="toggleAlerts"
          >
            <i
              class="fa"
              :class="alertsEnabled ? 'fa-bell' : 'fa-bell-slash'"
            />
          </div>
          <div
            v-tippy
            class="chats-body__header-multisend"
            title="Отправить сообщение множеству пользователей"
            @click="openMultisendDialog"
          >
            <i
              class="fa fa-envelopes-bulk"
            />
          </div>
        </template>
      </div>
      <div
        v-else
        class="chats-body__header-search-input"
      >
        <input
          ref="searchInput"
          v-model.trim="q"
          type="text"
          placeholder="Поиск"
          @keyup.escape="search = false"
        >
        <div
          class="chats-body__header-search-input-cancel"
          @click="search = false"
        >
          <i class="fa fa-times" />
        </div>
      </div>
      <div class="chats-body__header-loading">
        <div
          v-if="chatsLoading"
          class="chats-body__header-loading-indicator"
        >
          <i class="fa fa-spinner fa-spin" />
        </div>
      </div>
    </div>
    <div class="chats-scroll">
      <ChatDepartment
        v-if="unreadDepartment && !search"
        key="unread"
        :department="unreadDepartment"
      />
      <ChatDepartment
        v-for="department in chatsDepartments"
        :key="department.id"
        :department="department"
        :force-opened="search"
        :for-select="forSelect"
        :search="search ? q : ''"
        @select="selectUsersDepartment(department.id, $event)"
      />
    </div>
  </div>
</template>

<script lang="ts">
import * as actions from '@/store/action-types';
import ChatDepartment from '@/ui-cards/Chat/ChatDepartment.vue';

export default {
  name: 'ChatsBody',
  components: { ChatDepartment },
  props: {
    forSelect: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      search: false,
      q: '',
      selectedUsersByDepartment: {},
      selectedUsers: [],
    };
  },
  computed: {
    chatsDepartments() {
      return this.$store.getters.chatsDepartments || [];
    },
    chatsLoading() {
      return this.$store.getters.chatsLoading;
    },
    alertsEnabled() {
      return !this.$store.getters.chatsDisableAlerts;
    },
    unreadDepartment() {
      if (this.forSelect || this.$store.getters.chatsUnreadDialogsUsers.length === 0) {
        return null;
      }
      return {
        id: -100,
        title: 'Непрочитанные',
        users: this.$store.getters.chatsUnreadDialogsUsers,
      };
    },
  },
  watch: {
    selectedUsers: {
      handler() {
        this.$emit('select', this.selectedUsers);
      },
      deep: true,
      immediate: true,
    },
  },
  methods: {
    openSearch() {
      this.search = true;
      this.$nextTick(() => {
        this.$refs.searchInput.focus();
      });
    },
    enableAlerts() {
      this.$store.dispatch(actions.CHATS_SET_DISABLE_ALERTS, { disableAlerts: false });
    },
    disableAlerts() {
      this.$store.dispatch(actions.CHATS_SET_DISABLE_ALERTS, { disableAlerts: true });
    },
    toggleAlerts() {
      if (this.alertsEnabled) {
        this.disableAlerts();
      } else {
        this.enableAlerts();
      }
    },
    openMultisendDialog() {
      this.$store.dispatch(actions.CHATS_OPEN_DIALOG_BY_ID, { dialogId: -1000 });
    },
    selectUsersDepartment(department, users) {
      this.selectedUsersByDepartment[department] = users;

      const userIds = [];
      for (const departmentId of Object.keys(this.selectedUsersByDepartment)) {
        userIds.push(...this.selectedUsersByDepartment[departmentId]);
      }

      this.selectedUsers = userIds;
    },
  },
};
</script>

<style scoped lang="scss">
.chats-body {
  width: 100%;
  height: 100%;
  overflow: hidden;

  &__header {
    width: 100%;
    height: 30px;
    border-bottom: 1px solid #d0d0d0;
    display: flex;
    align-items: center;
    padding: 0 10px;

    &-title {
      font-size: 16px;
      font-weight: 500;
      color: #333;
    }

    &-search, &-alerts, &-multisend {
      display: inline-block;
      margin-left: 10px;
      cursor: pointer;
      color: #999;
      transition: color 0.2s ease;

      &:hover {
        color: #333;
      }
    }

    &-alerts {
      width: 20px;
      text-align: center;
    }

    &-search-input {
      width: 100%;
      height: 100%;
      margin-right: 20px;
      margin-left: -10px;
      display: flex;
      align-items: center;
      padding: 0 10px;
      background: #f5f5f5;
      border-radius: 0;

      input {
        width: 100%;
        height: 100%;
        border: none;
        outline: none;
        background: transparent;
        font-size: 14px;
        color: #333;
      }

      &-cancel {
        margin-left: 10px;
        cursor: pointer;
        color: #999;
        transition: color 0.2s ease;

        &:hover {
          color: #333;
        }
      }
    }

    &-loading {
      margin-left: auto;

      &-indicator {
        font-size: 16px;
        color: #999;
      }
    }
  }
}

.chats-scroll {
  width: 100%;
  height: calc(100% - 30px);
  overflow-y: auto;
}
</style>
