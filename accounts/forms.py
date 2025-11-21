from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm as _PasswordResetForm, \
    _unicode_ci_compare
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
import resend
import os
from django.utils.encoding import force_bytes
from django.template import loader
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

UserModel = get_user_model()


class PasswordResetForm(_PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email", 'class': 'form-control text-center'}),
    )

    def send_mail(
            self,
            subject_template_name,
            email_template_name,
            context,
            from_email,
            to_email,
            html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        resend.api_key = os.getenv("RESEND_API_KEY")

        params: resend.Emails.SendParams = {
            "from": "Центр событий <info@fan-club.kz>",
            "to": [to_email],
            "subject": subject,
            "html": f"""
                <div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
                    <div style="margin:50px auto;width:70%;padding:20px 0">
                        <div style="border-bottom:1px solid #eee">
                            <a href="https://fan-club.kz" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">Центр событий</a>
                        </div>
                        {body}
                        <p style="font-size:0.9em;">Regards,<br />Центр событий</p>
                        <hr style="border:none;border-top:1px solid #eee" />
                        <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
                            <p>Алматы, Казахстан</p>
                            <p>Instagram: @fan_club.kz</p>
                        </div>
                    </div>
                </div>""",
        }

        resend.Emails.send(params)
        return

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
               and _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def save(
            self,
            domain_override=None,
            subject_template_name="registration/password_reset_subject.txt",
            email_template_name="registration/password_reset_email.html",
            use_https=False,
            token_generator=default_token_generator,
            from_email=None,
            request=None,
            html_email_template_name=None,
            extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                user_email,
                html_email_template_name=html_email_template_name,
            )


class RegisterUserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['phone', 'email', 'first_name', 'last_name', ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control text-center'}),
            'email': forms.EmailInput(attrs={'class': 'form-control text-center'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control text-center'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control text-center'}),
        }

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'class': 'form-control text-center'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'class': 'form-control text-center'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"autofocus": True, 'class': "form-control"}),
        label="Номер телефона",
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            'class': "form-control",
            'id': "id_password2",

        }),
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'avatar', 'first_name', 'last_name')
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Получаем загруженное изображение
        avatar = self.cleaned_data.get('avatar')

        if avatar and isinstance(avatar, TemporaryUploadedFile):
            # Открываем изображение с помощью PIL
            img = Image.open(avatar)

            # Сжимаем изображение
            img.thumbnail((1024, 1024))  # Устанавливаем максимальные размеры

            # Сохраняем сжато
            image_io = BytesIO()
            img.save(image_io, format='JPEG')  # Сохраняем в формат JPEG
            image_io.seek(0)

            # Создаем новое изображение с сжатием
            compressed_avatar = ContentFile(image_io.read(), name=avatar.name)

            # Устанавливаем сжатое изображение в экземпляр модели
            instance.avatar = compressed_avatar

        if commit:
            instance.save()

        return instance


class VerifyUserForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control text-center'}),
        label="Код подтверждения"
    )
