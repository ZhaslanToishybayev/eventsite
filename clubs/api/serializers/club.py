from enum import Enum

from rest_framework import serializers

from accounts.api.serializers import UserReadSerializer
from clubs import models


class ClubActionEnum(Enum):
    UNLIKE = 'unlike'
    LIKE = 'like'
    JOIN = 'join'
    LEAVE = 'leave'


class ClubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ClubCategory
        fields = ('id', 'name')


class ClubCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.City
        fields = ('id', 'name')


class ClubCreateSerializer(serializers.ModelSerializer):
    creater = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.Club
        fields = ('name', 'category', 'logo', 'creater', 'email', 'phone', 'description', 'is_private')

    def create(self, validated_data):
        club = models.Club(**validated_data)
        club.save()
        club.managers.add(validated_data['creater'])
        return club


class ClubUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Club
        fields = '__all__'


class ClubActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=ClubActionEnum)


class ClubListSerializer(serializers.ModelSerializer):
    category = ClubCategorySerializer()

    class Meta:
        model = models.Club
        fields = (
            'id',
            'name',
            'category',
            'logo',
            'description',
            'members_count',
            'likes_count',
            'is_private',
            'created_at',
        )


class ClubDetailSerializer(serializers.ModelSerializer):
    category = ClubCategorySerializer()
    city = ClubCitySerializer()
    members = UserReadSerializer(many=True)
    likes = UserReadSerializer(many=True)
    partners = ClubListSerializer(many=True)
    creater = UserReadSerializer()
    managers = UserReadSerializer(many=True)

    class Meta:
        model = models.Club
        fields = '__all__'


class ClubSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Club
        fields = ('id', 'name')
