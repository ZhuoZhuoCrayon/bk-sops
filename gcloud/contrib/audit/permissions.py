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

from auth_backend.backends import get_backend_from_config
from auth_backend.resources.base import Action, NeverInitiateResource

audit_center_resource = NeverInitiateResource(
    rtype='audit_center',
    name=_("审计中心"),
    scope_type='system',
    scope_id=settings.BK_IAM_SYSTEM_ID,
    scope_name=_("标准运维"),
    actions=[Action(id='view', name=_("查看"), is_instance_related=False)],
    backend=get_backend_from_config())
