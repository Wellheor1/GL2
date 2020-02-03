<template>
  <div>
    <div class="row">
      <div class="col-xs-3" style="padding-right: 0">
        <button class="btn btn-block" style="white-space: normal;text-align: left;" title="Загрузить последний результат"
                v-if="!readonly"
                @click="loadLast"
                v-tippy="{ placement : 'bottom', arrow: true }">
            {{title}}&nbsp;&nbsp;<i class="fa fa-circle"></i>
        </button>
        <div v-else class="btn btn-block" style="white-space: normal;text-align: left;">{{title}}</div>
      </div>
      <div class="col-xs-9 base">
        <textarea :readonly="readonly" :rows="lines" class="form-control"
                  v-if="lines > 1" v-model="val"></textarea>
        <input :readonly="readonly" class="form-control" v-else v-model="val"/>
      </div>
    </div>
    <a v-if="direction" class="a-under" href="#" @click.prevent="print_results">
      печать результатов направления {{direction}}
    </a>
  </div>
</template>

<script>
    import researches_point from '../api/researches-point'
    import directions_point from '../api/directions-point'

    export default {
        name: 'SearchFieldValueField',
        props: {
            readonly: {
                type: Boolean
            },
            fieldPk: {
                type: String,
                required: true,
            },
            clientPk: {
                type: Number,
                required: true,
            },
            value: {
                required: false,
            },
            lines: {
                type: Number,
            },
            raw: {
                type: Boolean,
                required: false,
                default: false,
            },
        },
        data() {
            return {
                val: this.value,
                title: '',
                direction: null,
            }
        },
        mounted() {
            researches_point.fieldTitle({pk: this.fieldPk}).then(data => {
                const titles = new Set([data.research, data.group, data.field])
                this.title = [...titles].filter(t => !!t).join(' – ')
                this.checkDirection()

                setTimeout(() => {
                  if (!this.val || this.val === '') {
                      this.loadLast()
                  }
                }, 200)
            })
        },
        watch: {
            val() {
                this.changeValue(this.val)
            },
        },
        model: {
            event: 'modified'
        },
        methods: {
            checkDirection() {
                const res = /направление (\d+)\)$/gm.exec(this.val)
                this.direction = !res ? null : parseInt(res[1])
            },
            changeValue(newVal) {
                this.$emit('modified', newVal)
            },
            async loadLast() {
                this.direction = null;
                const {result} = await directions_point.lastFieldResult(this, [
                    'fieldPk',
                    'clientPk',
                ])
                if (result) {
                    this.direction = result.direction;
                    if (this.raw) {
                        this.val = result.value;
                    }
                    else {
                        this.val = `${result.value} (${result.date}, направление ${result.direction})`;
                    }
                } else {
                    errmessage(`Результат не найден (${this.title})!`)
                }
            },
            print_results() {
                this.$root.$emit('print:results', [this.direction])
            },
        },
    }
</script>

<style scoped>
  .base input, .base textarea {
    z-index: 1;
  }

  div.btn:hover {
    cursor: default;
  }
</style>