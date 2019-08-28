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
from rest_framework import serializers

from ensembl_production_db.models import *


class WebDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebData
        exclude = ('web_data',)

    data = serializers.CharField(source="web_data")


class BiotypeSerializer(serializers.ModelSerializer):
    is_current = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = MasterBiotype
        exclude = ('created_at', 'created_by')


class AttribTypeSerializer(serializers.ModelSerializer):
    is_current = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = MasterAttribType
        exclude = ('created_at', 'created_by')


class AttribTypeSerializerNoValidator(serializers.ModelSerializer):
    is_current = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = MasterAttribType
        exclude = ('created_at', 'created_by')
        extra_kwargs = {
            'code': {
                'validators': [],
            }
        }


class AttribSerializer(serializers.ModelSerializer):
    is_current = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = MasterAttrib
        exclude = ('created_at', 'created_by', 'modified_by')

    attrib_type = AttribTypeSerializerNoValidator(many=False, required=True)

    def create(self, validated_data):
        attrib_type = validated_data.pop('attrib_type')
        elem = MasterAttribType.objects.filter(code=attrib_type.get('code')).first()
        if not elem:
            elem = MasterAttribType.objects.create(**attrib_type)
        attrib = MasterAttrib.objects.create(attrib_type=elem, **validated_data)
        return attrib


class AnalysisDescriptionSerializer(serializers.ModelSerializer):
    is_current = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = AnalysisDescription
        exclude = ('created_at', 'created_by')

    web_data = WebDataSerializer(many=False, required=False)

    def create(self, validated_data):
        if 'web_data' in validated_data:
            web_data = validated_data.pop('web_data')
            elem = WebData.objects.filter(web_data=web_data.get('web_data', '')).first()
            if not elem:
                elem = WebData.objects.create(**web_data)
        else:
            elem = None
        web_data = AnalysisDescription.objects.create(web_data=elem, **validated_data)
        return web_data

    def update(self, instance, validated_data):
        if 'web_data' in validated_data:
            web_data = validated_data.pop('web_data')
            elem = WebData.objects.filter(web_data=web_data.get('web_data', '')).first()
            if not elem:
                elem = WebData.objects.create(**web_data)
                instance.web_data = elem
                instance.save()
        return super(AnalysisDescriptionSerializer, self).update(instance, validated_data)
