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

from __future__ import absolute_import, unicode_literals

from auth_backend.constants import HTTP_AUTH_FAILED_CODE


class AuthBaseException(Exception):
    pass


class AuthLookupError(AuthBaseException):
    pass


class AuthKeyError(AuthBaseException):
    pass


class AuthInvalidOperationError(AuthBaseException):
    pass


class AuthInterfaceEmptyError(AuthBaseException):
    pass


class AuthBackendError(AuthBaseException):
    pass


class AuthOperationFailedError(AuthBaseException):
    pass


class AuthFailedException(AuthBaseException):
    def __init__(self, permissions, status=HTTP_AUTH_FAILED_CODE, *args, **kwargs):
        super(AuthFailedException, self).__init__(*args, **kwargs)
        self.permissions = permissions
        self.status = status
