from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from clubs import models


class ClubServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClubServiceImage
        fields = '__all__'


class ClubServiceSerializer(serializers.ModelSerializer):
    images = SerializerMethodField()

    class Meta:
        model = models.ClubService
        fields = ('id', 'name', 'description', 'price', 'images')

    @property
    def images(self):
        images = models.ClubServiceImage.filter(club=self.context['uuid'])
        return images
