import json
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.accounts.mixins import StaffOrOwnerRequiredMixin, OwnerRequiredMixin
from .models import ServiceRecord, ServiceType
from .forms import ServiceRecordForm, ServiceTypeForm, ServiceStatusForm


class ServiceListView(LoginRequiredMixin, ListView):
    model = ServiceRecord
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 20

    def get_queryset(self):
        qs = ServiceRecord.objects.select_related('service_type', 'mechanic').all()
        status = self.request.GET.get('status')
        vehicle = self.request.GET.get('vehicle')
        mechanic_id = self.request.GET.get('mechanic')
        if status:
            qs = qs.filter(status=status)
        if vehicle:
            qs = qs.filter(vehicle_number__icontains=vehicle)
        if mechanic_id:
            qs = qs.filter(mechanic_id=mechanic_id)
        # Mechanics see only their own services
        if self.request.user.is_mechanic:
            qs = qs.filter(mechanic=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = ServiceRecord.STATUS_CHOICES
        from apps.accounts.models import User
        ctx['mechanics'] = User.objects.filter(role='MECHANIC', is_active=True)
        return ctx


class ServiceCreateView(StaffOrOwnerRequiredMixin, CreateView):
    model = ServiceRecord
    form_class = ServiceRecordForm
    template_name = 'services/service_form.html'
    success_url = reverse_lazy('services:service_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['service_types'] = ServiceType.objects.filter(is_active=True)
        return ctx

    def form_valid(self, form):
        service = form.save(commit=False)
        # Copy checklist template from service type
        if service.service_type:
            service.checklist = [
                {'item': item, 'done': False}
                for item in service.service_type.get_checklist()
            ]
        service.save()
        messages.success(self.request, f'Service created for {service.vehicle_number}!')
        return super().form_valid(form)


class ServiceDetailView(LoginRequiredMixin, DetailView):
    model = ServiceRecord
    template_name = 'services/service_detail.html'
    context_object_name = 'service'


class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceRecord
    form_class = ServiceStatusForm
    template_name = 'services/service_update.html'
    success_url = reverse_lazy('services:service_list')

    def form_valid(self, form):
        service = form.save(commit=False)
        if service.status == ServiceRecord.COMPLETED and not service.completed_at:
            service.completed_at = timezone.now()
        service.save()
        messages.success(self.request, 'Service updated!')
        return super().form_valid(form)


class VehicleHistoryView(LoginRequiredMixin, ListView):
    model = ServiceRecord
    template_name = 'services/vehicle_history.html'
    context_object_name = 'services'

    def get_queryset(self):
        vehicle = self.request.GET.get('vehicle', '')
        if vehicle:
            return ServiceRecord.objects.filter(vehicle_number__iexact=vehicle).order_by('-created_at')
        return ServiceRecord.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['searched_vehicle'] = self.request.GET.get('vehicle', '')
        return ctx


class UpdateChecklistView(LoginRequiredMixin, View):
    def post(self, request, pk):
        service = get_object_or_404(ServiceRecord, pk=pk)
        data = json.loads(request.body)
        service.checklist = data.get('checklist', service.checklist)
        service.save()
        return JsonResponse({'success': True})


class ServiceTypeListView(OwnerRequiredMixin, ListView):
    model = ServiceType
    template_name = 'services/service_type_list.html'
    context_object_name = 'service_types'


class ServiceTypeCreateView(OwnerRequiredMixin, CreateView):
    model = ServiceType
    form_class = ServiceTypeForm
    template_name = 'services/service_type_form.html'
    success_url = reverse_lazy('services:service_type_list')
