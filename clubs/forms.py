from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.validators import MinValueValidator
from accounts.models import User
from . import models
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class ClubForm(forms.ModelForm):
    class Meta:
        model = models.Club
        fields = (
            'name',
            'category',
            'logo',
            'whatsapp_group_link',
            'description',
            'email',
            'phone',
            'city',
            'address',
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'category': forms.Select(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'logo': forms.FileInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'whatsapp_group_link': forms.URLInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'description': forms.Textarea(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'email': forms.EmailInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'phone': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'city': forms.Select(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'address': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
        }

    def save(self, commit=True):
        """
        Переопределяем метод save для сжатия изображения перед сохранением.
        """
        # Получаем объект модели, но пока не сохраняем его в базе данных
        instance = super().save(commit=False)

        # Получаем изображение из поля "logo"
        logo = instance.logo
        if logo:
            img = Image.open(logo)

            # Сжимаем изображение до нужного размера (например, 1024x1024)
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)  # Используем LANCZOS для уменьшения

            # Сохраняем сжатое изображение в памяти
            image_io = BytesIO()
            img_format = 'JPEG' if img.format == 'JPEG' else 'PNG'  # Поддержка форматов JPEG и PNG
            img.save(image_io, format=img_format, quality=70)  # Сжимаем с качеством 70%

            # Заменяем оригинальное изображение на сжатое
            instance.logo = ContentFile(image_io.getvalue(), name=logo.name)

        # Сохраняем объект в базе данных
        if commit:
            instance.save()
        return instance


class ClubUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Club
        exclude = (
            'creater',
            'members',
            'members_count',
            'managers',
            'likes_count',
            'is_private',
            'is_active',
            'likes',
            'partners',
            'partners_count'
        )

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'category': forms.Select(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'logo': forms.FileInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'whatsapp_group_link': forms.URLInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'description': forms.Textarea(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'email': forms.EmailInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'phone': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'city': forms.Select(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'address': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
        }

    def save(self, commit=True):
        """
        Переопределяем метод save для сжатия изображения перед сохранением.
        """
        # Получаем объект модели, но пока не сохраняем его в базе данных
        instance = super().save(commit=False)

        # Получаем изображение из поля "logo"
        logo = self.cleaned_data.get('logo')
        if logo and isinstance(logo, TemporaryUploadedFile):
            img = Image.open(logo)

            # Сжимаем изображение до нужного размера (например, 1024x1024)
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)  # Используем LANCZOS для уменьшения

            # Сохраняем сжатое изображение в памяти
            image_io = BytesIO()
            img_format = 'JPEG' if img.format == 'JPEG' else 'PNG'  # Поддержка форматов JPEG и PNG
            img.save(image_io, format=img_format, quality=70)  # Сжимаем с качеством 70%

            file_name = logo.name.split('/')[-1]

            # Заменяем оригинальное изображение на сжатое
            instance.logo = ContentFile(image_io.getvalue(), name=file_name)

        # Сохраняем объект в базе данных
        if commit:
            instance.save()
        return instance


class SelectClubManagersForm(forms.ModelForm):
    managers = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=FilteredSelectMultiple(
            attrs={'class': 'form-control'},
            is_stacked=False,
            verbose_name='',
        ),
        required=False,
        label='Управляющие клуба'
    )

    class Meta:
        model = models.Club
        fields = ['managers', ]

    class Media:
        css = {
            'all': ('/static/admin/css/widgets.css',),
        }
        js = ('/admin/jsi18n',)

    def clean_choised_users(self):
        choiced_users = self.cleaned_data['managers']
        return choiced_users

    @staticmethod
    def required_at_least_one_manager(users_after, form):
        if len(users_after) == 0:
            form.add_error('managers', 'У клуба должен быть хотя бы один менеджер')
            return False
        return True


class ClubServiceCreateForm(forms.ModelForm):
    class Meta:
        model = models.ClubService
        fields = (
            'name',
            'description',
            'price',
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'description': forms.Textarea(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'price': forms.NumberInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
        }

    photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control text-center w-100 mx-auto'}))


class CreateClubEventForm(forms.ModelForm):
    class Meta:
        model = models.ClubEvent
        exclude = (
            'old_datetime',
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'description': forms.Textarea(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'banner': forms.FileInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'location': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'start_datetime': forms.DateInput(
                attrs={'class': 'form-control text-center w-100 mx-auto', 'type': 'date'}),
            'end_datetime': forms.DateInput(attrs={'class': 'form-control text-center w-100 mx-auto', 'type': 'date'}),
            'entry_requirements': forms.Textarea(attrs={'class': 'form-control text-center w-100 mx-auto'}),
        }

    min_age = forms.IntegerField(
        widget=forms.NumberInput(attrs={'min': '1', 'class': 'form-control text-center w-100 mx-auto'}),
        min_value=1,
        validators=[MinValueValidator(1)],
        label='Минимальный допустимый возраст'
    )
    max_age = forms.IntegerField(
        widget=forms.NumberInput(attrs={'min': '1', 'class': 'form-control text-center w-100 mx-auto'}),
        min_value=1,
        validators=[MinValueValidator(1)],
        label='Максимальный допустимый возраст'
    )
    club = forms.ModelChoiceField(widget=forms.HiddenInput(), required=True, queryset=models.Club.objects.all())

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Получаем загруженное изображение
        banner = self.cleaned_data.get('banner')
        if banner and isinstance(banner, TemporaryUploadedFile):
            # Открываем изображение с помощью PIL
            image = Image.open(banner)

            # Сжимаем изображение
            image.thumbnail((1024, 1024))  # Устанавливаем максимальные размеры

            # Сохраняем сжато
            image_io = BytesIO()
            image.save(image_io, format='JPEG')  # Сохраняем в формат JPEG
            image_io.seek(0)

            # Создаем новое изображение с сжатием
            compressed_banner = ContentFile(image_io.read(), name=banner.name)

            # Устанавливаем сжатое изображение в экземпляр модели
            instance.banner = compressed_banner

        if commit:
            instance.save()

        return instance


class AddGalleryPhotoForm(forms.ModelForm):
    class Meta:
        model = models.ClubGalleryPhoto
        fields = ('club', 'image')
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
        }

    club = forms.ModelChoiceField(
        widget=forms.HiddenInput(),
        required=True,
        queryset=models.Club.objects.all()
    )

    def save(self, commit=True):
        """
        Переопределяем метод save для сжатия изображения перед сохранением.
        """
        # Получаем объект модели, но пока не сохраняем его в базе данных
        instance = super().save(commit=False)

        # Получаем изображение из формы
        image = instance.image
        if image:
            img = Image.open(image)

            # Сжимаем изображение до нужного размера (например, 1024x1024)
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)  # Используем LANCZOS вместо ANTIALIAS

            # Сохраняем сжатое изображение в памяти
            image_io = BytesIO()
            img_format = 'JPEG' if img.format == 'JPEG' else 'PNG'  # Поддержка форматов JPEG и PNG
            img.save(image_io, format=img_format, quality=70)  # Сохраняем с качеством 70%

            # Заменяем оригинальное изображение на сжатое
            instance.image = ContentFile(image_io.getvalue(), name=image.name)

        # Сохраняем объект в базе данных
        if commit:
            instance.save()
        return instance


class FestivalForm(forms.ModelForm):
    class Meta:
        model = models.Festival
        fields = ('name', 'description', 'image', 'start_datetime', 'location')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control text-center w-100 mx-auto',
                'placeholder': 'Напишите название'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control text-center w-100 mx-auto',
                'placeholder': 'Напишите важные данные'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'start_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control text-center w-100 mx-auto',
                'type': 'datetime-local', 'placeholder': 'Пример заполнения: "01.01.2024 10:00"'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control text-center w-100 mx-auto',
                'placeholder': 'Напишите место проведения'
            }),
        }

    def save(self, commit=True):
        """
        Переопределяем метод save для сжатия изображения перед сохранением.
        """
        # Получаем объект модели, но пока не сохраняем его в базе данных
        instance = super().save(commit=False)

        # Получаем загруженное изображение
        image = self.cleaned_data.get('image')

        if image and isinstance(image, TemporaryUploadedFile):
            img = Image.open(image)

            # Сжимаем изображение до нужного размера (например, 1024x1024)
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)  # Используем LANCZOS для уменьшения

            # Сохраняем сжатое изображение в памяти
            image_io = BytesIO()
            img_format = 'JPEG' if img.format == 'JPEG' else 'PNG'  # Поддержка форматов JPEG и PNG
            img.save(image_io, format=img_format, quality=70)  # Сжимаем с качеством 70%

            # Заменяем оригинальное изображение на сжатое
            instance.image = ContentFile(image_io.getvalue(), name=image.name)

        # Сохраняем объект в базе данных
        if commit:
            instance.save()
        return instance


class ServiceForClubCreateForm(forms.ModelForm):
    class Meta:
        model = models.ServiceForClubs
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'description': forms.Textarea(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'min_price': forms.NumberInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'max_price': forms.NumberInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
            'phone': forms.TextInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
        }

    image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control text-center w-100 mx-auto'}),
        label='Фото услуги'
    )

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Получаем загруженное изображение
        image = self.cleaned_data.get('image')
        if image and isinstance(image, TemporaryUploadedFile):
            # Открываем изображение с помощью PIL
            img = Image.open(image)

            # Сжимаем изображение
            img.thumbnail((1024, 1024))  # Устанавливаем максимальные размеры

            # Сохраняем сжато
            image_io = BytesIO()
            img.save(image_io, format='JPEG')  # Сохраняем в формат JPEG
            image_io.seek(0)

            # Создаем новое изображение с сжатием
            compressed_image = ContentFile(image_io.read(), name=image.name)

            # Устанавливаем сжатое изображение в экземпляр модели
            instance.image = compressed_image

        if commit:
            instance.save()

        return instance


class PublicationForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget(), label='Контент')

    class Meta:
        model = models.Publication
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control text-center mx-auto'}),
            'annotation': forms.Textarea(attrs={'class': 'form-control text-center mx-auto'}),
        }
