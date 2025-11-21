from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image

from clubs import forms, models


class ClubServiceListView(generic.ListView):
    model = models.ClubService
    context_object_name = 'services'
    template_name = 'clubs/club_services.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Услуги клубов'
        return ctx


class CreateServiceView(generic.CreateView):
    model = models.ClubService
    form_class = forms.ClubServiceCreateForm
    template_name = 'clubs/create_service.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Создать услугу'
        return ctx

    def form_valid(self, form):
        if form.is_valid():
            service = form.save(commit=False)
            club_id = self.kwargs.get('pk')
            club = models.Club.objects.get(id=club_id)
            service.club = club
            service.save()
            # Получаем изображение из формы
            photo = form.cleaned_data.get('photo')

            # Если изображение существует, сжимаем его
            if photo:
                # Открываем изображение с помощью PIL
                img = Image.open(photo)

                # Преобразуем изображение в формат RGB, если это необходимо
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Сжимаем изображение до максимального размера
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

                # Создаем новый файл сжатого изображения
                image_io = BytesIO()
                img.save(image_io, format='JPEG', quality=70)
                image_io.seek(0)

                # Сохраняем сжатое изображение как ContentFile
                compressed_photo = ContentFile(image_io.read(), name=photo.name)

                # Создаем объект изображения с сжатыми данными
                models.ClubServiceImage.objects.create(
                    service=service,
                    image=compressed_photo
                )

            return HttpResponseRedirect(reverse('service_detail', kwargs={'pk': service.pk}))
        else:
            return super().form_invalid(form)


class UpdateServiceView(PermissionRequiredMixin, generic.UpdateView):
    model = models.ClubService
    form_class = forms.ClubServiceCreateForm
    template_name = 'clubs/update_service.html'

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь разрешение на редактирование услуги сообщества.

        Параметры:
            None

        Возвращает:
            bool: True, если пользователь является менеджером клуба, иначе False.
        """
        return self.request.user in self.get_object().club.managers.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Редактировать услугу'
        ctx['service'] = self.object
        return ctx

    def form_valid(self, form):
        if form.is_valid():
            service = form.save(commit=False)
            service.save()
            # Получаем изображение из формы
            photo = form.cleaned_data.get('photo')
            if photo:

                # Открываем изображение с помощью PIL
                img = Image.open(photo)

                # Преобразуем изображение в формат RGB, если это необходимо
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Сжимаем изображение до максимального размера
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

                # Создаем новый файл сжатого изображения
                image_io = BytesIO()
                img.save(image_io, format='JPEG', quality=70)
                image_io.seek(0)

                # Создаем новое изображение
                compressed_photo = ContentFile(image_io.read(), name=photo.name)

                # Создаем или обновляем объект изображения для услуги
                photo_obj, created = models.ClubServiceImage.objects.get_or_create(
                    service=service
                )
                photo_obj.image = compressed_photo
                photo_obj.save()
            return HttpResponseRedirect(reverse('service_detail', kwargs={'pk': self.get_object().pk}))
        else:
            return super().form_invalid(form)


class ClubServiceDetailView(generic.DetailView):
    model = models.ClubService
    template_name = 'clubs/detail_service.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.object.name
        return context
