# -*- coding: utf-8 -*-
"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest
from rest_framework import serializers
from rest_framework import status

from rest_framework.exceptions import APIException
from ensembl_dbcopy.models import *

User = get_user_model()


class BaseUserTimestampSerializer(serializers.ModelSerializer):
    user = serializers.CharField(required=False)

    def create(self, validated_data):
        if 'user' in validated_data:
            validated_data['user'] = validated_data.pop('user')
            validated_data['email_list'] = validated_data.pop('email')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'user' in validated_data:
            validated_data['user'] = validated_data.pop('user')
            validated_data['email_list'] = validated_data.pop('email')
        return super().update(instance, validated_data)

    def validate(self, data):
        if "user" in data:
            try:
                data['user'] = User.objects.get(username=data.pop('user', ''), is_staff=True)
            except ObjectDoesNotExist:
                exc = APIException(code='error', detail="User not found")
                # hack to update status code. :-(
                exc.status_code = status.HTTP_400_BAD_REQUEST
                raise exc
            user_info = User.objects.filter(username=data.get('user')).first()
            data['email'] = user_info.email
        data = super().validate(data)
        return data


class TransferLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferLog
        fields = (
            'job_id',
            'tgt_host',
            'table_schema',
            'table_name',
            'renamed_table_schema',
            'target_directory',
            'start_date',
            'end_date',
            'size')


class RequestJobListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RequestJob
        fields = '__all__'
        extra_kwargs = {
            'url': {'view_name': 'requestjob-detail', 'lookup_field': 'job_id'},
        }


class RequestJobDetailSerializer(BaseUserTimestampSerializer):
    class Meta:
        model = RequestJob
        fields = '__all__'

    transfer_log = TransferLogSerializer(many=True, source='transfer_logs', read_only=True)
