from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from accounts.models import User, Profile


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get('email')
        password = data.get('password')

        if not phone or not password:
            msg = "Телефон и пароль объязательные поля"
            raise serializers.ValidationError(msg, code='authentication')

        return data


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'avatar', 'email', 'phone']


class UserCreateSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['phone', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password2": "Пароли не совпадают"})

        return attrs


class UserVerifySerializer(serializers.Serializer):
    user_session_id = serializers.UUIDField()
    email_code = serializers.CharField()
    
    def validate(self, data):
        user_session_id = data.get('user_session_id')
        email_code = data.get('email_code')

        if not user_session_id or not email_code:
            msg = "user_session_id и email_code объязательные поля"
            raise serializers.ValidationError(msg, code='authentication')

        return data


class ProfileUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        exclude = ('user',)
