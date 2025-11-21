from rest_framework import serializers

from clubs import models


class ClubEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ClubEvent
        exclude = ('old_datetime', )
