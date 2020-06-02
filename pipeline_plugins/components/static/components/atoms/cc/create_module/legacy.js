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
(function () {
    $.atoms.cc_create_module = [
        {
            tag_code: "biz_cc_id",
            type: "select",
            attrs: {
                name: gettext("业务"),
                hookable: true,
                remote: true,
                remote_url: $.context.get('site_url') + 'pipeline/cc_get_business_list/',
                remote_data_init: function (resp) {
                    return resp.data;
                },
                disabled: !$.context.canSelectBiz(),
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            methods: {
                _tag_init: function () {
                    if (this.value) {
                        return
                    }
                    this._set_value($.context.getBkBizId())
                }
            }
        },
        {
            tag_code: "cc_set_select_method",
            type: "radio",
            attrs: {
                name: gettext("填参方式"),
                hookable: false,
                items: [
                    {value: "topo", name: gettext("拓扑选择")},
                    {value: "text", name: gettext("手动输入")},
                ],
                default: "topo",
                validation: [
                    {
                        type: "required"
                    }
                ],
            },
            events: [
                {
                    source: "cc_set_select_method",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value)
                    }
                },
            ]
        },
        {
            tag_code: "cc_set_select_topo",
            type: "tree",
            attrs: {
                name: gettext("所属集群"),
                hookable: true,
                remote: true,
                remote_url: function () {
                    const url = $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/cc_search_topo/set/normal/' + $.context.getBkBizId() + '/';
                    return url
                },
                remote_data_init: function (resp) {
                    return resp.data;
                },
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let self = this;
                            let result = {
                                result: true,
                                error_message: ""
                            };
                            console.log(result);
                            if (!self.get_parent) {
                                return result
                            } else if (self.get_parent().get_child("cc_set_select_topo")) {

                                if (self.get_parent().get_child("cc_set_select_method").value === "topo" && !value.length) {
                                    result.result = false;
                                    result.error_message = gettext("请选择集群");
                                }
                            } else if (!value.length) {
                                result.result = false;
                                result.error_message = gettext("请选择集群");
                            }
                            return result
                        }
                    }
                ]
            },
            events: [
                {
                    source: "biz_cc_id",
                    type: "init",
                    action: function () {
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id').value;
                        this.items = [];
                        if (cc_id !== '') {
                            this.remote_url = $.context.get('site_url') + 'pipeline/cc_search_topo/set/normal/' + cc_id + '/';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "biz_cc_id",
                    type: "change",
                    action: function (value) {
                        if ($.context.canSelectBiz()) {
                            this._set_value('');
                        }
                        this.items = [];
                        if (value !== '') {
                            this.remote_url = $.context.get('site_url') + 'pipeline/cc_search_topo/set/normal/' + value + '/';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    // 监听 cc_set_select_method 单选框变化，选择topo时显示该树形组件
                    source: "cc_set_select_method",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === "topo") {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
            ],
            methods: {}
        },
        {
            tag_code: "cc_set_select_text",
            type: "textarea",
            attrs: {
                name: gettext("所属集群"),
                hookable: true,
                placeholder: gettext("请输入完整路径，从业务拓扑开始，如`业务A>网络B>集群C`，多个目标集群用换行分隔"),
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let self = this;
                            let result = {
                                result: true,
                                error_message: ""
                            };
                            if (!self.get_parent) {
                                return result
                            } else if (self.get_parent().get_child("cc_set_select_method")) {
                                if (self.get_parent().get_child("cc_set_select_method").value === "text" && !value) {
                                    result.result = false;
                                    result.error_message = gettext("集群完整路径不能为空")
                                }
                            } else if (!value) {
                                result.result = false;
                                result.error_message = gettext("集群完整路径不能为空")
                            }
                            return result
                        }
                    }
                ]
            },
            events: [
                {
                    source: "cc_set_select_method",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === "text") {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
            ]
        },
        {
            tag_code: "cc_create_method",
            type: "radio",
            attrs: {
                name: gettext("创建方式"),
                hookable: false,
                items: [
                    {value: "template", name: gettext("从模板创建")},
                    {value: "category", name: gettext("直接创建")},
                ],
                default: "category",
                validation: [
                    {
                        type: "required"
                    }
                ],
            },
            events: [
                {
                    source: "cc_create_method",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value)
                    }
                },
            ]
        },
        {
            tag_code: "cc_module_infos_category",
            type: "datatable",
            attrs: {
                name: gettext("模块信息"),
                remote_url: function () {
                    const url = $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/cc_search_create_object_attribute/set/' + $.context.getBkBizId() + '/';
                    return url
                },
                remote_data_init: function (resp) {
                    const data = resp.data;
                    data.forEach(function (column) {
                        column.type = 'input';
                        column.attrs.width = "200px";
                    });

                    data.push({
                        tag_code: "cc_service_category",
                        type: "cascader",
                        attrs: {
                            name: gettext("服务实例分类"),
                            width: "200px",
                            items: [],
                            multiple: false,
                            lazy: true,
                            lazyLoad(node, resolve) {
                                let self = this;
                                const {level, value} = node;
                                setTimeout(() => {
                                    let url = '';
                                    if (level === 0) {
                                        url = `${$.context.get('site_url')}pipeline/cc_list_service_category/${$.context.getBkBizId()}/0/`;
                                    }else {
                                        url = `${$.context.get('site_url')}pipeline/cc_list_service_category/${$.context.getBkBizId()}/${value}/`;
                                    }
                                    // 通过调用resolve将子节点数据返回，通知组件数据加载完成
                                    $.ajax({
                                        url: url,
                                        type: 'GET',
                                        dataType: 'json',
                                        success: function (resp) {
                                            let nodes = resp.data.map(item => ({
                                                value: item.value,
                                                label: item.label,
                                                leaf: level >= 1
                                            }));
                                            if (level === 0) {
                                                self.items = nodes;
                                            } else {
                                                self.items.every(element => {
                                                    if (element.value === value) {
                                                        element.children = nodes;
                                                        return false
                                                    } else return true
                                                })
                                            }
                                            resolve(nodes)
                                        },
                                        error: function (resp) {
                                            resolve([]);
                                            show_msg(resp.message, 'error');
                                        }
                                    })
                                }, 100);
                            }
                        }
                    });
                    return data;
                },
                hookable: true,
                add_btn: true,
            },
            events: [
                {
                    source: "cc_create_method",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === "category") {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
                {
                    source: "biz_cc_id",
                    type: "init",
                    action: function () {
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id').value;
                        this.columns = [];
                        if (cc_id !== '') {
                            this.remote_url = $.context.get('site_url') + 'pipeline/cc_search_create_object_attribute/module/' + cc_id + '/';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "biz_cc_id",
                    type: "change",
                    action: function (value) {
                        if ($.context.canSelectBiz()) {
                            this._set_value('');
                        }
                        this.columns = [];
                        if (value !== '') {
                            this.remote_url = $.context.get('site_url') + 'pipeline/cc_search_create_object_attribute/module/' + value + '/';
                            this.remoteMethod();
                        }
                    }
                }
            ],
        },
        {
            tag_code: "cc_module_infos_template",
            type: "datatable",
            attrs: {
                name: gettext("模块信息"),
                remote_url: function () {
                    const url = $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/cc_search_create_object_attribute/set/' + $.context.getBkBizId() + '/';
                    return url
                },
                remote_data_init: function (resp) {
                    const data = resp.data;
                    data.forEach(function (column) {
                        column.type = 'input';
                        column.attrs.width = "200px";
                    });
                    let name_index = -1;
                    data.every((column, index) => {
                        if (column.tag_code === "bk_module_name") {
                            name_index = index;
                            return false
                        } else return true
                    });
                    if (name_index !== -1) {
                        data.splice(name_index, 1);
                    }
                    data.unshift({
                        tag_code: "cc_service_template",
                        type: "select",
                        attrs: {
                            name: gettext("服务模板"),
                            width: "200px",
                            default: "Default_-1",
                            hookable: false,
                            remote_url: function () {
                                return `${$.context.get('site_url')}pipeline/cc_list_service_template/${$.context.getBkBizId()}/`;
                            },
                            remote_data_init: function (resp) {
                                let data = resp.data;
                                if (data.length !== 0) {
                                    this.value = data[0].value;
                                }
                                return resp.data;
                            },
                        }
                    });
                    return data;
                },
                hookable: true,
                add_btn: true,
            },
            events: [
                {
                    source: "cc_create_method",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === "template") {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
                {
                    source: "biz_cc_id",
                    type: "init",
                    action: function () {
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id').value;
                        this.columns = [];
                        if (cc_id !== '') {
                            this.remote_url = $.context.get('site_url') + 'pipeline/cc_search_create_object_attribute/module/' + cc_id + '/';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "biz_cc_id",
                    type: "change",
                    action: function (value) {
                        if ($.context.canSelectBiz()) {
                            this._set_value('');
                        }
                        this.columns = [];
                        if (value !== '') {
                            this.remote_url = $.context.get('site_url') + 'pipeline/cc_search_create_object_attribute/module/' + value + '/';
                            this.remoteMethod();
                        }
                    }
                }
            ],
        },
    ]
})();