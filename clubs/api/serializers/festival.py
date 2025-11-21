from enum import Enum

from rest_framework import serializers
from clubs import models


class FestivalActionEnum(Enum):
    JOIN = 'join'
    LEAVE = 'leave'


class FestivalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Festival
        fields = ('id', 'name', 'description', 'image')


class FestivalRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Festival
        fields = '__all__'


class FestivalCreateOrUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Festival
        fields = ('name', 'description', 'image', 'location', 'start_datetime')


class FestivalActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=FestivalActionEnum)
    club = serializers.PrimaryKeyRelatedField(queryset=models.Club.objects.filter(is_active=True))


class FestivalSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Festival
        fields = ('id', 'name')
