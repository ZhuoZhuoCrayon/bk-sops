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
    <div class="functionalization-wrapper">
        <div :class="['task-info', { 'functor-task-info': userRights.function }]">
            <span class="task-info-title">{{ $t('任务信息') }}</span>
            <div class="task-info-division-line"></div>
            <div class="common-form-item">
                <label class="required">{{ $t('任务名称') }}</label>
                <div class="common-form-content">
                    <bk-input
                        class="task-name"
                        name="taskName"
                        v-model="name"
                        v-validate="taskNameRule">
                    </bk-input>
                    <span class="common-error-tip error-msg">{{ errors.first('taskName') }}</span>
                </div>
            </div>
        </div>
        <div class="param-info">
            <div class="param-info-title">
                <span>
                    {{ $t('参数信息') }}
                </span>
            </div>
            <div class="param-info-division-line"></div>
            <div v-if="!isVariableEmpty" class="form-wrapper" v-bkloading="{ isLoading: isConfigLoading, opacity: 1 }">
                <TaskParamEdit
                    ref="TaskParamEdit"
                    :constants="pipelineData.constants"
                    @onChangeConfigLoading="changeLoading">
                </TaskParamEdit>
            </div>
            <NoData v-else></NoData>
        </div>
        <div class="action-wrapper">
            <bk-button
                class="preview-button"
                @click="onShowPreviewDialog">
                {{ $t('预览') }}
            </bk-button>
            <bk-button
                theme="primary"
                :class="['task-claim-button', {
                    'btn-permission-disable': !hasPermission(['claim'], instanceActions, instanceOperations)
                }]"
                :loading="isSubmit"
                v-cursor="{ active: !hasPermission(['claim'], instanceActions, instanceOperations) }"
                @click="onTaskClaim">
                {{ $t('认领') }}
            </bk-button>
        </div>
        <bk-dialog
            :value="previewDialogShow"
            :mask-close="false"
            :header-position="'left'"
            :has-footer="false"
            :ext-cls="'common-dialog'"
            :title="$t('任务流程预览')"
            width="1000"
            @cancel="onCancel">
            <NodePreview
                v-if="canvasShow"
                ref="nodePreviewRef"
                :preview-data-loading="previewDataLoading"
                :canvas-data="formatCanvasData(previewData)"
                :preview-bread="previewBread"
                @onNodeClick="onNodeClick"
                @onSelectSubflow="onSelectSubflow">
            </NodePreview>
        </bk-dialog>
    </div>
</template>
<script>
    import { mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import permission from '@/mixins/permission.js'
    import NoData from '@/components/common/base/NoData.vue'
    import TaskParamEdit from '../TaskParamEdit.vue'
    import NodePreview from '../NodePreview.vue'

    export default {
        name: 'TaskFunctionalization',
        inject: ['reload'],
        components: {
            NoData,
            TaskParamEdit,
            NodePreview
        },
        mixins: [permission],
        props: [
            'project_id', 'template_id', 'instance_id', 'instanceFlow', 'instanceName',
            'instanceActions', 'instanceOperations', 'instanceResource'
        ],
        data () {
            return {
                isSubmit: false,
                isConfigLoading: false,
                previewDialogShow: false,
                canvasShow: false,
                previewDataLoading: false,
                name: this.instanceName,
                nodeSwitching: false,
                pipelineData: JSON.parse(this.instanceFlow),
                previewData: JSON.parse(this.instanceFlow),
                taskNameRule: {
                    required: true,
                    max: STRING_LENGTH.TASK_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                previewBread: []
            }
        },
        computed: {
            ...mapState({
                'userRights': state => state.userRights
            }),
            isVariableEmpty () {
                return Object.keys(this.pipelineData.constants).length === 0
            }
        },
        watch: {
            /** HACK
             * magicbox V2.1.8 版本，dialog 组件在切换为显示状态后，画布组件开始渲染，
             * 弹窗内容区域 display 属性仍为 none，在 $nextTick 里才变更，
             * 导致画布组件首次渲染时因为容器高度为 0，连线不能正确渲染位置
             */
            previewDialogShow (val) {
                if (val) {
                    setTimeout(() => {
                        this.canvasShow = true
                    }, 0)
                } else {
                    this.canvasShow = false
                }
            }
        },
        methods: {
            ...mapActions('task/', [
                'claimFuncTask'
            ]),
            formatCanvasData (pipelineData) {
                const { line, location, gateways } = pipelineData
                const branchConditions = {}
                for (const gKey in gateways) {
                    const item = gateways[gKey]
                    if (item.conditions) {
                        branchConditions[item.id] = Object.assign({}, item.conditions)
                    }
                }
                return {
                    lines: line,
                    locations: location.map(item => {
                        return { ...item, mode: 'preview', checked: true }
                    }),
                    branchConditions
                }
            },
            updateCanvas () {
                this.previewDataLoading = true
                this.$nextTick(() => {
                    this.previewDataLoading = false
                })
            },
            changeLoading (val) {
                this.isConfigLoading = val
            },
            onTaskClaim () {
                if (this.isSubmit) return

                if (!this.hasPermission(['claim'], this.instanceActions, this.instanceOperations)) {
                    const resourceData = {
                        name: this.instanceName,
                        id: this.instance_id,
                        auth_actions: this.instanceActions
                    }
                    this.applyForPermission(['claim'], resourceData, this.instanceOperations, this.instanceResource)
                    return
                }

                this.isSubmit = true
                this.$validator.validateAll().then(async (result) => {
                    if (!result) return
                    const formData = {}
                    if (this.$refs.TaskParamEdit) {
                        const variables = this.$refs.TaskParamEdit.getVariableData()
                        for (const key in variables) {
                            formData[key] = variables[key].value
                        }
                    }
                    const data = {
                        name: this.name,
                        instance_id: this.instance_id,
                        project_id: this.project_id,
                        constants: JSON.stringify(formData)
                    }
                    try {
                        const res = await this.claimFuncTask(data)
                        if (res.result) {
                            this.reload()
                        } else {
                            errorHandler(res, this)
                        }
                    } catch (e) {
                        errorHandler(e, this)
                    } finally {
                        this.isSubmit = false
                    }
                })
            },
            onShowPreviewDialog () {
                this.previewBread.push({
                    name: this.name,
                    data: this.previewData
                })
                this.previewDialogShow = true
            },
            onCancel () {
                this.previewDialogShow = false
                this.previewDataLoading = false
                this.previewData = tools.deepClone(this.pipelineData)
                this.previewBread = []
            },
            onSelectSubflow (data, index) {
                this.previewData = data
                this.previewBread.splice(index + 1)
                this.updateCanvas()
            },
            onNodeClick (id) {
                const activity = this.previewData.activities[id]
                if (!activity || activity.type !== 'SubProcess') {
                    return
                }
            
                const previewData = activity.pipeline
                this.previewBread.push({
                    data: previewData,
                    name: activity.name
                })
                this.previewData = previewData
                this.updateCanvas()
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.functionalization-wrapper {
    position: relative;
    padding: 0 40px;
    padding-top: 30px;
    min-height: calc(100vh - 50px - 139px);
    background-color: #ffffff;
    @media screen and (max-width: 1300px){
        width: calc(100% - 80px);
    }
    /deep/ .no-data-wrapper {
        margin: 100px 0;
    }
    .operation-header {
        margin-top: -20px;
        padding: 0 0 0 10px;
        height: 50px;
        border-bottom: 1px solid $commonBorderColor;
        line-height: 50px;
        background-color: $commonBgColor;
    .bread-crumbs-wrapper {
        display: inline-block;
        font-size: 14px;
        .path-item {
            display: inline-block;
            .node-name {
                margin: 0 4px;
                color: $blueDefault;
                cursor: pointer;
            }
            &:last-child {
                .node-name {
                    cursor: pointer;
                    &:last-child {
                        color: $greyDefault;
                        cursor: text;
                    }
                }
            }
        }
    }
    .operation-container {
        float: right;
        .operation-btn {
            float: left;
            width: 60px;
            height: 49px;
            line-height: 49px;
            font-size: 22px;
            text-align: center;
            color: $greyDisable;
            &.clickable {
                color: $greyDefault;
                cursor: pointer;
                &:hover {
                    color: $greenDefault;
                }
                &.actived {
                    color: $greenDefault;
                    background: $whiteDefault;
                }
            }
            &.common-icon-dark-paper {
                border-left: 1px solid $commonBorderColor;
            }
        }
    }
}
}
.task-info, .param-info {
    margin-top: 15px;
    padding-bottom: 20px;
    .task-info-title, .param-info-title {
        font-size: 14px;
        font-weight: 600;
        color: #313238;
    }
    .task-info-division-line, .param-info-division-line {
        margin: 5px 0 30px;
        height: 1px;
        border: 0px;
        background-color: #cacedb;
    }
    .common-form-item {
        label {
            color: #313238;
            font-weight: normal;
        }
    }
}
.param-info  {
    padding-bottom: 80px;
}
.functor-task-info {
    padding-bottom: 0px;
}
.task-param-wrapper {
    width: 620px;
}
.form-wrapper {
    min-height: 200px;
}
.action-wrapper {
    position: absolute;
    bottom: 0;
    width: 100%;
    height: 72px;
    line-height: 72px;
    margin: 0 -40px;
    border-top: 1px solid #cacedb;
    background-color: #ffffff;
    text-align: left;
    button {
        margin-top: -7px;
    }
    .preview-button {
        padding: 0px;
        margin-left: 40px;
        width: 90px;
        height: 32px;
        line-height: 32px;
        color: #313238;
    }
    .task-claim-button {
        width: 140px;
    }
}
.task-name {
    max-width: 500px;
}
/deep/ .bk-dialog-body {
    height: 420px;
    background-color: #f4f7fa;
}
/deep/ .pipeline-canvas{
    .tool-wrapper {
        top: 20px;
        left: 40px;
    }
}
</style>
