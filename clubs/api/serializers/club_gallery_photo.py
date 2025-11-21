from rest_framework import serializers
from clubs import models


class ClubGalleryPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ClubGalleryPhoto
        fields = '__all__'
