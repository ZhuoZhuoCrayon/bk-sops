/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="advance-search-wrapper">
        <div class="operation-area clearfix">
            <div class="operation-btn">
                <slot name="operation"></slot>
            </div>
            <advance-search
                v-if="isShowSearch"
                @input="onSearchInput"
                @onShow="onAdvanceOpen"
                :is-advance-open.sync="isAdvanceOpen"
                :value="searchConfig.value"
                :input-placeholader="searchConfig.placeholder">
                <template slot="extend">
                    <slot name="search-extend"></slot>
                </template>
            </advance-search>
        </div>
        <div class="advanced-form-area" v-if="isAdvanceOpen">
            <div class="search-record" v-if="recordsData.length > 0">
                <p class="record-title">{{ $t('历史记录') }}</p>
                <div class="record-list">
                    <bk-radio-group v-model="selectedRecord" @change="handleRecordSelect">
                        <bk-radio
                            class="record-item"
                            v-for="item in recordsData"
                            :key="item.id"
                            :value="item.id">
                            <template v-for="form in item.data">
                                <div
                                    :class="['form-history', {
                                        'en': lang === 'en',
                                        'daterange': form.type === 'dateRange'
                                    }]"
                                    :key="form.key"
                                    :title="form.value">
                                    <span class="label">{{ form.label }}{{ $t('：') }}</span>
                                    <span class="value">{{ form.value }}</span>
                                </div>
                            </template>
                        </bk-radio>
                    </bk-radio-group>
                </div>
            </div>
            <div class="advanced-search-form">
                <bk-form form-type="inline" :model="formData">
                    <bk-form-item
                        v-for="item in searchForm"
                        :key="item.key"
                        :property="item.key"
                        :label="item.label">
                        <template v-if="item.type === 'select'">
                            <bk-select
                                style="width: 260px;"
                                :placeholder="item.placeholder"
                                :loading="item.loading"
                                :clearable="true"
                                :searchable="true"
                                v-model="formData[item.key]"
                                @clear="onClearFormItem(item.key)"
                                @change="onChangeFormItem($event, item.key, item.type)">
                                <bk-option
                                    v-for="option in item.list"
                                    :key="option.value"
                                    :id="option.value"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </template>
                        <template v-if="item.type === 'dateRange'">
                            <bk-date-picker
                                :value="formData[item.key]"
                                type="daterange"
                                format="yyyy-MM-dd"
                                :placeholder="item.placeholder"
                                @change="onChangeFormItem($event, item.key, item.type)">
                            </bk-date-picker>
                        </template>
                        <template v-if="item.type === 'input'">
                            <bk-input
                                style="width: 260px;"
                                class="search-input"
                                v-model.trim="formData[item.key]"
                                :placeholder="item.placeholder">
                            </bk-input>
                        </template>
                    </bk-form-item>
                    <bk-form-item class="query-button">
                        <bk-button class="query-primary" theme="primary" @click.prevent="submit">{{$t('搜索')}}</bk-button>
                        <bk-button class="query-cancel" @click.prevent="onResetForm">{{$t('清空')}}</bk-button>
                    </bk-form-item>
                </bk-form>
            </div>
        </div>
    </div>
</template>
<script>
    import { mapState } from 'vuex'
    import moment from 'moment'
    import i18n from '@/config/i18n/index.js'
    import { random4 } from '@/utils/uuid.js'
    import tools from '@/utils/tools.js'
    import AdvanceSearch from './AdvanceSearch.vue'

    export default {
        name: 'AdvanceSearchForm',
        components: {
            AdvanceSearch
        },
        props: {
            isShowSearch: {
                type: Boolean,
                default: true
            },
            id: {
                type: String,
                default: ''
            },
            showRecord: {
                type: Boolean,
                default: true
            },
            searchConfig: {
                type: Object,
                default: () => ({
                    placeholder: i18n.t('请输入'),
                    value: ''
                })
            },
            searchForm: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                isAdvanceOpen: false,
                records: [],
                selectedRecord: null,
                searchValue: '',
                formData: {}
            }
        },
        computed: {
            ...mapState({
                username: state => state.username,
                lang: state => state.lang
            }),
            recordsData () {
                const searchObj = {}
                this.searchForm.forEach(item => {
                    searchObj[item.key] = item
                })
                const list = this.records.map(recordItem => {
                    const id = recordItem.id
                    let data = Object.keys(recordItem.form).map(key => {
                        const form = searchObj[key]
                        if (!form) {
                            return
                        }

                        const { label, type } = form
                        let value = ''
                        if (form.type === 'select') {
                            const option = form.list.find(opt => opt.value === recordItem.form[key])
                            value = option ? option.name : '--'
                        } else if (form.type === 'dateRange') {
                            const timeStr = []
                            recordItem.form[key].forEach(timeItem => {
                                if (timeItem) {
                                    timeStr.push(timeItem)
                                }
                            })
                            value = timeStr.length > 0 ? timeStr.join(' - ') : '--'
                        } else {
                            value = recordItem.form[key] ? recordItem.form[key] : '--'
                        }
                        return { label, value, type }
                    })

                    const datetimeIndex = data.findIndex(i => i.type === 'dateRange')
                    if (datetimeIndex > -1) {
                        const datetimeForm = data.splice(datetimeIndex, 1)
                        data = data.concat(datetimeForm)
                    }

                    return { id, data }
                })
                
                return list
            }
        },
        created () {
            this.searchForm.forEach(m => {
                this.$set(this.formData, m.key, m.value)
            })
            if (this.showRecord) {
                this.records = this.getSearchRecords()
            }
        },
        methods: {
            getSearchRecords () {
                const records = JSON.parse(localStorage.getItem(`advanced_search_record`))
                if (records !== null && records[this.username] && records[this.username][this.id]) {
                    return records[this.username][this.id]
                }
                return []
            },
            setSearchRecords (data) {
                if (!this.dataShouldStoreInStorage(data)) {
                    return
                }
                const id = random4()
                let records = JSON.parse(localStorage.getItem(`advanced_search_record`))
                if (records === null) {
                    records = {}
                }
                if (!records[this.username]) {
                    records[this.username] = {}
                }

                if (!records[this.username][this.id]) {
                    records[this.username][this.id] = [{
                        id,
                        form: this.formData
                    }]
                } else {
                    if (records[this.username][this.id].length === 4) {
                        records[this.username][this.id].shift()
                    }
                    records[this.username][this.id].push({
                        id,
                        form: this.formData
                    })
                }
                localStorage.setItem(`advanced_search_record`, JSON.stringify(records))
            },
            /**
             * 校验数据是否应该添加到历史记录中
             * 不能添加的两种情况：
             * 1.所有表单项都为空
             * 2.历史记录中已存在相同的表单值
             * 高级搜索表单类型较简单，只判断字符串是否为空、数组长度为0以及数据里每项元素是否为空，对象是否为空
             * @param {Object} data 数据对象
             */
            dataShouldStoreInStorage (data) {
                const isFormEmpty = Object.keys(data).every(item => {
                    const dataItem = data[item]
                    if (typeof dataItem === 'string') {
                        return dataItem === ''
                    } else if (Array.isArray(dataItem)) {
                        return dataItem.length === 0 || dataItem.every(i => i === '')
                    } else if (Object.prototype.toString.call(dataItem) === '[object object]') {
                        return Object.keys(dataItem).length === 0 // 只判断空对象
                    }
                    return false
                })
                if (isFormEmpty) {
                    return false
                }
                return this.records.every(record => {
                    return Object.keys(record.form).some(key => {
                        return !tools.isDataEqual(record.form[key], data[key])
                    })
                })
            },
            handleRecordSelect (value) {
                const record = this.records.find(item => item.id === value)
                this.formData = tools.deepClone(record.form)
            },
            onSearchInput (val) {
                this.$emit('onSearchInput', val)
            },
            onAdvanceOpen (val) {
                this.isAdvanceOpen = val === undefined ? !this.isAdvanceOpen : val
            },
            onClearFormItem (key) {
                this.formData[key] = ''
            },
            onChangeFormItem (val, key, type) {
                if (type === 'dateRange') {
                    val = val.map(item => {
                        return item instanceof Date ? moment(item).format('yyyy-MM-dd') : item
                    })
                }
                this.formData[key] = val
            },
            submit () {
                if (this.showRecord) {
                    this.setSearchRecords(this.formData)
                    this.records = this.getSearchRecords()
                    this.selectedRecord = null
                }
                this.$emit('submit', this.formData)
            },
            onResetForm () {
                Object.keys(this.formData).forEach(key => {
                    this.$set(this.formData, key, '')
                })
                this.$emit('submit', this.formData)
            }
        }
    }
</script>

<style lang='scss' scoped>
@import '@/scss/config.scss';
.advance-search-wrapper {
    width: 100%;
    .operation-area {
        margin: 20px 0;
        .operation-btn {
            float: left;
        }
    }
    .search-record {
        padding: 0 30px;
        color: #63656e;
        background: #fafbfd;
        border: 1px solid #dcdee5;
        border-bottom: none;
        .record-title {
            padding: 20px 0;
            border-bottom: 1px solid #dcdee5;
        }
        .record-list {
            padding: 10px 0;
        }
        .record-item {
            display: flex;
            align-items: center;
            margin-bottom: 22px;
            &:last-child {
                margin-bottom: 0;
            }
        }
    }
    /deep/ .form-history {
        float: left;
        margin-right: 12px;
        width: 160px;
        line-height: 22px;
        font-size: 12px;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        &.daterange {
            width: 224px;
        }
        &.en {
            width: 184px;
            &.daterange {
                width: 272px;
            }
        }
        .label {
            color: #c4c6cc;
        }
    }
    .advanced-search-form {
        margin-bottom: 20px;
        padding: 0px 30px 20px;
        background: #ffffff;
        border: 1px solid #dde4eb;
        border-radius: 2px;
        /deep/ .bk-form-item {
            float: left;
            height: 32px;
            margin-top: 20px !important;
            margin-left: 8px;
            .bk-label {
                min-width: 160px !important;
            }
        }
        .query-button {
            margin-left: 168px;
            .query-cancel {
                margin-left: 5px;
            }
        }
    }
}
</style>
