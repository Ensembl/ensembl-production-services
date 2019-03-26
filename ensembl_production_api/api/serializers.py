# -*- coding: utf-8 -*-

import json

from rest_framework import serializers

from ensembl_production_api.models import *


def escape_perl_string(v):
    """Escape characters with special meaning in perl"""
    return str(v).replace("$", "\\$").replace("\"", "\\\"").replace("@", "\\@")


def perl_string_to_python(s):
    """Parse a Perl hash string into a Python dict"""
    s = s.replace("=>", ":").replace("\\$", "$").replace("\\@", "@").replace('\'', '"')
    return json.loads(s)


class PerlFieldElementSerializer(serializers.CharField):

    def list_to_perl_string(self, input_list):
        """Transform the supplied array into a string representation of a Perl array"""
        elems = []
        for v in input_list:
            t = type(v).__name__
            if t == 'str':
                elems.append("\"%s\"" % escape_perl_string(v))
            elif t == 'unicode':
                elems.append("\"%s\"" % escape_perl_string(str(v)))
            elif t in ('int', 'long'):
                elems.append("%d" % v)
            elif t == 'float':
                elems.append("%f" % v)
            elif t == 'list':
                elems.append("%s" % self.list_to_perl_string(v))
            elif t == 'dict':
                elems.append("%s" % self.to_internal_value(v))
            else:
                raise Exception("Unsupported type " + str(t))
        return "[%s]" % ", ".join(elems)

    def to_internal_value(self, data):
        """Transform the supplied dict into a string representation of a Perl hash"""
        pairs = []
        for k, v in sorted([(k, v) for k, v in data.items() if v is not None], key=lambda x: x[0]):
            # for k, v in sorted(filter((k, v) for k, v in data.items())):
            k = str(k)
            t = type(v).__name__
            if t == 'str':
                pairs.append("\"%s\" => \"%s\"" % (k, escape_perl_string(v)))
            elif t == 'unicode':
                pairs.append("\"%s\" => \"%s\"" % (k, escape_perl_string(str(v))))
            elif t in ('int', 'long'):
                pairs.append("\"%s\" => %d" % (k, v))
            elif t == 'float':
                pairs.append("\"%s\" => %f" % (k, v))
            elif t == 'list':
                pairs.append("\"%s\" => %s" % (k, self.list_to_perl_string(v)))
            elif t == 'dict':
                pairs.append("\"%s\" => %s" % (k, self.to_internal_value(v)))
            elif t == 'bool':
                if str(v) == "True":
                    pairs.append("\"%s\" => %d" % (k, 1))
            else:
                raise Exception("Unsupported type " + str(t))
        return "{%s}" % ", ".join(pairs)

    def to_representation(self, instance):
        return perl_string_to_python(instance)


class WebDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebData
        fields = '__all__'

    data = PerlFieldElementSerializer()


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


class AttribSerializer(serializers.ModelSerializer):
    is_current = serializers.BooleanField(default=True, initial=True)
    class Meta:
        model = MasterAttrib
        exclude = ('created_at', 'created_by','modified_by')
    attrib_type = AttribTypeSerializer(many=False, required=True)

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
            elem = WebData.objects.filter(data=web_data.get('data', '')).first()
            if not elem:
                elem = WebData.objects.create(**web_data)
        else:
            elem = None
        web_data = AnalysisDescription.objects.create(web_data=elem, **validated_data)
        return web_data

    def update(self, instance, validated_data):
        if 'web_data' in validated_data:
            web_data = validated_data.pop('web_data')
            elem = WebData.objects.filter(data=web_data.get('data', '')).first()
            if not elem:
                elem = WebData.objects.create(**web_data)
                instance.web_data=elem
                instance.save()
        return super(AnalysisDescriptionSerializer, self).update(instance, validated_data)
