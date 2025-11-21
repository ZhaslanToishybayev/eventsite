from rest_framework import serializers

from accounts.api.serializers import UserReadSerializer
from clubs import models
from clubs.api.serializers import ClubSimpleSerializer
from clubs.static import RequestActionEnum


class ClubJoinRequestSerializer(serializers.ModelSerializer):
    user = UserReadSerializer()
    club = ClubSimpleSerializer()

    class Meta:
        model = models.ClubJoinRequest
        fields = ('id', 'user', 'club', 'approved')


class ClubJoinRequestActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=RequestActionEnum)


class ClubPartnershipRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ClubPartnerShipRequest
        fields = '__all__'


class ClubPartnershipRequestActionSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=RequestActionEnum)
