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

import logging
import traceback

import ujson as json
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, NotFound
from tastypie.authorization import ReadOnlyAuthorization
from djcelery.models import PeriodicTask as CeleryTask

from auth_backend.plugins.tastypie.authorization import BkSaaSLooseAuthorization
from auth_backend.plugins.tastypie.shortcuts import (
    verify_or_raise_immediate_response,
    batch_verify_or_raise_immediate_response,
)
from gcloud.commons.template.permissions import common_template_resource
from gcloud.constants import PROJECT, COMMON
from gcloud.core.permissions import project_resource

from pipeline.exceptions import PipelineException
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from pipeline_web.parser.validator import validate_web_pipeline_tree

from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.permissions import task_template_resource
from gcloud.periodictask.models import PeriodicTask
from gcloud.periodictask.permissions import periodic_task_resource
from gcloud.core.utils import name_handler
from gcloud.core.constant import PERIOD_TASK_NAME_MAX_LENGTH
from gcloud.webservice3.resources import (
    ProjectResource,
    GCloudModelResource,
)
from gcloud.commons.template.models import CommonTemplate
from gcloud.commons.template.utils import replace_template_id

logger = logging.getLogger("root")


class CeleryTaskResource(GCloudModelResource):
    enabled = fields.BooleanField(attribute="enabled", readonly=True)

    class Meta(GCloudModelResource.Meta):
        queryset = CeleryTask.objects.all()
        authorization = ReadOnlyAuthorization()
        resource_name = "celery_task"
        filtering = {
            "enabled": ALL,
        }


class PipelinePeriodicTaskResource(GCloudModelResource):
    celery_task = fields.ForeignKey(CeleryTaskResource, "celery_task", full=True)
    name = fields.CharField(attribute="name", readonly=True)
    creator = fields.CharField(attribute="creator", readonly=True)

    class Meta(GCloudModelResource.Meta):
        queryset = PipelinePeriodicTask.objects.all()
        authorization = ReadOnlyAuthorization()
        resource_name = "pipeline_periodic_task"
        filtering = {
            "name": ALL,
            "creator": ALL,
            "celery_task": ALL_WITH_RELATIONS,
        }


class CustomCreateDetailAuthorization(BkSaaSLooseAuthorization):
    def create_detail(self, object_list, bundle):
        return True


class PeriodicTaskResource(GCloudModelResource):
    project = fields.ForeignKey(ProjectResource, "project", full=True)
    task_template_name = fields.CharField(attribute="task_template_name", readonly=True)
    template_id = fields.CharField(attribute="template_id", readonly=True)
    enabled = fields.BooleanField(attribute="enabled", readonly=True)
    name = fields.CharField(attribute="name", readonly=True)
    cron = fields.CharField(attribute="cron", readonly=True)
    total_run_count = fields.IntegerField(attribute="total_run_count", readonly=True)
    last_run_at = fields.DateTimeField(attribute="last_run_at", readonly=True, null=True)
    creator = fields.CharField(attribute="creator", readonly=True)
    pipeline_tree = fields.DictField(attribute="pipeline_tree", readonly=True, use_in="detail")
    form = fields.DictField(attribute="form", readonly=True, use_in="detail")
    task = fields.ForeignKey(PipelinePeriodicTaskResource, "task", full=True)

    class Meta(GCloudModelResource.Meta):
        queryset = PeriodicTask.objects.all()
        resource_name = "periodic_task"
        auth_resource = periodic_task_resource
        authorization = CustomCreateDetailAuthorization(
            auth_resource=auth_resource, read_action_id="view", update_action_id="edit"
        )
        filtering = {
            "id": ALL,
            "template_id": ALL,
            "template_source": ALL,
            "project": ALL_WITH_RELATIONS,
            "name": ALL,
            "enabled": ALL,
            "creator": ALL,
            "task": ALL_WITH_RELATIONS,
        }

    def obj_create(self, bundle, **kwargs):
        try:
            template_id = bundle.data.pop("template_id")
            template_source = bundle.data.get("template_source", PROJECT)
            name = bundle.data.pop("name")
            cron = json.loads(bundle.data.pop("cron"))
            pipeline_tree = json.loads(bundle.data.pop("pipeline_tree"))
        except (KeyError, ValueError) as e:
            message = "create periodic_task params error: %s" % e.message
            logger.error(message)
            raise BadRequest(message)

        if not isinstance(cron, dict):
            raise BadRequest("cron must be a object json string")

        # XSS handle
        name = name_handler(name, PERIOD_TASK_NAME_MAX_LENGTH)
        creator = bundle.request.user.username

        # validate pipeline tree
        try:
            validate_web_pipeline_tree(pipeline_tree)
        except PipelineException as e:
            raise BadRequest(str(e))

        try:
            project = ProjectResource().get_via_uri(bundle.data.get("project"), request=bundle.request)
        except NotFound:
            raise BadRequest("project [uri=%s] does not exist" % bundle.data.get("project"))

        if template_source == PROJECT:
            try:
                template = TaskTemplate.objects.get(id=template_id, project=project, is_deleted=False)
            except TaskTemplate.DoesNotExist:
                raise BadRequest(
                    "template[id={template_id}] of project[{project_id}] does not exist".format(
                        template_id=template_id, project_id=project.id
                    )
                )

            verify_or_raise_immediate_response(
                principal_type="user",
                principal_id=creator,
                resource=task_template_resource,
                action_ids=[task_template_resource.actions.create_periodic_task.id],
                instance=template,
            )

            try:
                replace_template_id(TaskTemplate, pipeline_tree)
            except TaskTemplate.DoesNotExist:
                raise BadRequest("invalid subprocess, check subprocess node please")

        elif template_source == COMMON:
            try:
                template = CommonTemplate.objects.get(id=template_id, is_deleted=False)
            except CommonTemplate.DoesNotExist:
                raise BadRequest("common template[id=%s] does not exist" % template_id)
            perms_tuples = [
                (project_resource, [project_resource.actions.use_common_template.id], project),
                (common_template_resource, [common_template_resource.actions.create_periodic_task.id], template),
            ]
            batch_verify_or_raise_immediate_response(
                principal_type="user", principal_id=creator, perms_tuples=perms_tuples
            )

            try:
                replace_template_id(CommonTemplate, pipeline_tree)
            except TaskTemplate.DoesNotExist:
                raise BadRequest("invalid subprocess, check subprocess node please")

        else:
            raise BadRequest("invalid template_source[%s]" % template_source)

        kwargs["template_id"] = template_id
        kwargs["template_source"] = template_source
        try:
            kwargs["task"] = PeriodicTask.objects.create_pipeline_task(
                project=project,
                template=template,
                name=name,
                cron=cron,
                pipeline_tree=pipeline_tree,
                creator=creator,
                template_source=template_source,
            )
        except Exception as e:
            logger.warning(traceback.format_exc())
            raise BadRequest(str(e))

        response = super(PeriodicTaskResource, self).obj_create(bundle, **kwargs)
        response.obj.set_enabled(True)

        return response
