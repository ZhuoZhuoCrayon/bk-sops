# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from auth_backend.resources.base import Action, NeverInitiateResource
from auth_backend.resources.django import DjangoModelResource
from auth_backend.resources.inspect import FixedCreatorTypeFieldInspect
from auth_backend.backends import get_backend_from_config

from gcloud.core.models import Project

project_resource = DjangoModelResource(
    rtype='project',
    name=_("项目"),
    scope_type='system',
    scope_id=settings.BK_IAM_SYSTEM_ID,
    scope_name=_("标准运维"),
    actions=[
        Action(id='create', name=_("新建"), is_instance_related=False),
        Action(id='view', name=_("查看"), is_instance_related=True),
        Action(id='edit', name=_("编辑"), is_instance_related=True),
        Action(id='create_template', name=_("新建流程"), is_instance_related=True),
        Action(id='use_common_template', name=_("使用公共流程"), is_instance_related=True),
        Action(id='fast_create_task', name=_("快速新建一次性任务"), is_instance_related=True),
    ],
    operations=[
        {
            'operate_id': 'create',
            'actions_id': ['create']
        },
        {
            'operate_id': 'view',
            'actions_id': ['view']
        },
        {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        },
        {
            'operate_id': 'create_template',
            'actions_id': ['view', 'create_template']
        },
        {
            'operate_id': 'use_common_template',
            'actions_id': ['view', 'use_common_template']
        },
        {
            'operate_id': 'fast_create_task',
            'actions_id': ['view', 'fast_create_task']
        }
    ],
    resource_cls=Project,
    id_field='id',
    backend=get_backend_from_config(),
    inspect=FixedCreatorTypeFieldInspect(creator_type='user',
                                         creator_id_f='creator',
                                         resource_id_f='id',
                                         resource_name_f='name',
                                         parent_f=None,
                                         scope_id_f=None))

admin_operate_resource = NeverInitiateResource(
    rtype='admin_operate',
    name=_("后台管理"),
    scope_type='system',
    scope_id=settings.BK_IAM_SYSTEM_ID,
    scope_name=_("标准运维"),
    actions=[
        Action(id='view', name=_("查看"), is_instance_related=False),
        Action(id='edit', name=_("编辑"), is_instance_related=False)
    ],
    backend=get_backend_from_config())
