# -*- coding: utf-8 -*-
from rest_framework import serializers

from ensembl_production.models import *


class WebDataElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebDataElement
        fields = '__all__'


class WebDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebData
        fields = '__all__'

    elements = WebDataElementSerializer(many=True)
