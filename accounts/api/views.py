import uuid
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework import status, permissions as drf_permissions, generics
from rest_framework.views import APIView

from accounts.models import User, Profile
from accounts import utils
from accounts import constants
from . import serializers
from . import exceptions
from . import permissions


class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (drf_permissions.AllowAny,)
    serializer_class = serializers.UserCreateSerializer
    #
    # def validate_phone(self, phone):
    #     """
    #     Проверяет, начинается ли номер телефона с допустимого префикса.
    #
    #     Параметры:
    #         phone (str): Номер телефона.
    #
    #     Возвращает:
    #         bool: True, если номер валиден.
    #
    #     Исключения:
    #         ValidationError: Если номер телефона невалиден.
    #     """
    #     valid_prefixes = (
    #         '+770', '+7747', '+7771', '+7775', '+7776', '+7777', '+7778'
    #     )
    #
    #     if not any(phone.startswith(prefix) for prefix in valid_prefixes):
    #         raise exceptions.PhonePrefixErrorException

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_id = uuid.uuid4()
        session_key = constants.USER_SESSION_KEY.format(session_id)
        
        phone = serializer.validated_data['phone']
        email = serializer.validated_data['email']

        # # Валидация номера телефона перед созданием пользователя
        # if phone:
        #     self.validate_phone(phone)

        user_data = {
            'phone': phone,
            'email': email,
            'first_name': serializer.validated_data['first_name'],
            'last_name': serializer.validated_data['last_name'],
            'password': make_password(serializer.validated_data['password2']),
        }
        
        email_code = utils.generate_email_code(email)
        data = {
            'user_data': user_data,
            'email_code': email_code,
        }
        
        cache.set(session_key, data, constants.USER_SESSION_KEY_TTL)
        return Response(
            {'session_id': session_id, 'phone': phone, 'email': email},
            status=status.HTTP_202_ACCEPTED
        )


class UserVerifyAPIView(generics.GenericAPIView):
    serializer_class = serializers.UserVerifySerializer

    # def validate_phone(self, phone):
    #     """
    #     Проверяет, начинается ли номер телефона с допустимого префикса.
    #
    #     Параметры:
    #         phone (str): Номер телефона.
    #
    #     Возвращает:
    #         bool: True, если номер валиден.
    #
    #     Исключения:
    #         ValidationError: Если номер телефона невалиден.
    #     """
    #     valid_prefixes = (
    #         '+770', '+7747', '+7771', '+7775', '+7776', '+7777', '+7778'
    #     )
    #
    #     if not any(phone.startswith(prefix) for prefix in valid_prefixes):
    #         raise exceptions.PhonePrefixErrorException

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_key = constants.USER_SESSION_KEY.format(serializer.validated_data['user_session_id'])
        session = cache.get(session_key)

        if session is None:
            raise exceptions.SMSCodeExpireException

        if session['email_code'] != serializer.validated_data['email_code']:
            raise exceptions.SMSCodeInvalidException

        # # Валидация номера телефона перед созданием пользователя
        # phone = session['user_data'].get('phone')
        # if phone:
        #     self.validate_phone(phone)

        user = User.objects.create(**session['user_data'], is_displayed_in_allies=True)
        login(request, user)
        user.save()
        token = utils.generate_token(user)

        return Response(token, status=status.HTTP_201_CREATED)


class ProfileUpdateAPIView(APIView):
    permission_classes = (drf_permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = serializers.ProfileUpdateSerializer(instance=profile, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('avatar'):
            profile.avatar = serializer.validated_data['avatar']
        for key, value in serializer.validated_data.items():
            setattr(profile, key, value)
        profile.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserToSearchingInAlliesList(APIView):
    permission_classes = (drf_permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.user.is_displayed_in_allies = 1 - request.user.is_displayed_in_allies
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
