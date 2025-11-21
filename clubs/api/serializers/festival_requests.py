from rest_framework import serializers
from .club import ClubSimpleSerializer
from .festival import FestivalSimpleSerializer
from clubs import models
from clubs.static import RequestActionEnum


class FestivalRequestSerializer(serializers.ModelSerializer):
    club = ClubSimpleSerializer()
    festival = FestivalSimpleSerializer()

    class Meta:
        model = models.FestivalParticipationRequest
        fields = ('id', 'club', 'festival')


class FestivalRequestActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=RequestActionEnum)
