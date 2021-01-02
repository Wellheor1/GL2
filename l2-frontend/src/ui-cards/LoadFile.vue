<template>
  <fragment>
    <li v-show="Boolean(l2_load_file)">
      <a href="#" @click.prevent="doOpen">
        Загрузка файла
      </a>
      <modal v-if="open" @close="open = loading" show-footer="true" white-bg="true"
             max-width="710px" width="100%" marginLeftRight="auto">
        <span slot="header">Загрузка файла</span>
        <div slot="body">
          <div class="form-group">
            <label for="fileInput">PDF файл</label>
            <input type="file" ref="file" class="form-control-file" id="fileInput" :readonly="loading"
                   @change="handleFileUpload()">
          </div>
          <button style="width: 200px;"
                  type="button" class="btn btn-primary" @click="submit()" :disabled="!Boolean(file) || loading">
            <i class="fa fa-spinner" v-if="loading"></i>
            <span v-else>Загрузить</span>
          </button>
          <h5 v-if="results.length > 0">Сохранённые результаты</h5>
          <ul>
            <li v-for="r in results">{{r.pk}} – {{r.result}}</li>
          </ul>
        </div>
        <div slot="footer">
          <div class="row">
            <div class="col-xs-4">
              <button @click="open = false" class="btn btn-primary-nb btn-blue-nb" type="button" :disabled="loading">
                Закрыть
              </button>
            </div>
          </div>
        </div>
      </modal>
    </li>
  </fragment>
</template>

<script>
import Modal from "@/ui-cards/Modal";
import axios from "axios";

export default {
  components: {Modal},
  name: 'LoadFile',
  data() {
    return {
      open: false,
      loading: false,
      file: '',
      results: [],
    };
  },
  methods: {
    doOpen() {
      this.file = '';
      this.open = true;
      this.results = [];
    },
    handleFileUpload() {
      this.file = this.$refs.file.files[0];
    },
    async submit() {
      this.loading = true;
      try {
        this.results = [];
        const formData = new FormData();
        formData.append('file', this.file);
        const {data} = await axios.post('/api/parse-file/loadfile',
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        );
        this.results = data.results;
        this.$refs.file.value = '';
        this.file = '';
        okmessage('Файл загружен');
      } catch (e) {
        console.error(e);
        errmessage('Ошибка');
      }
      this.loading = false;
    },
  },
  computed: {
    l2_load_file() {
      return this.$store.getters.modules.l2_load_file;
    },
  },
}
</script>

<style lang="scss" scoped>
</style>