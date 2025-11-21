from rest_framework import status
from rest_framework.exceptions import APIException


class SMSCodeExpireException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Срок смс кода истек. Повторите регистрацию'
    default_code = 'sms_code_expire'


class PhonePrefixErrorException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Некорректный префикс номера! Укажите другой номер!'
    default_code = 'sms_phone_invalid'


class SMSCodeInvalidException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Не верный СМС код! Повторите ввод!'
    default_code = 'sms_code_invalid'
