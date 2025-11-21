from rest_framework import serializers

from clubs import models


class ClubAdsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ClubAds
        fields = '__all__'
