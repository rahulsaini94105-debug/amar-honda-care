import json
from datetime import datetime, timedelta
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages

from apps.accounts.mixins import StaffOrOwnerRequiredMixin
from apps.accounts.models import User
from apps.services.models import ServiceType, ServiceRecord
from .models import Appointment
from .forms import CustomerAppointmentForm, AdminAppointmentForm
from .reminders import notify_appointment_created, notify_appointment_status_changed


class CustomerBookingView(CreateView):
    model = Appointment
    form_class = CustomerAppointmentForm
    template_name = 'appointments/book.html'
    success_url = reverse_lazy('appointments:booking_success')

    def form_valid(self, form):
        booking_date = form.cleaned_data['booking_date']
        time_slot = form.cleaned_data['time_slot']
        
        # Parse slot
        try:
            start_str, end_str = time_slot.split('-')
            tz = timezone.get_current_timezone()
            
            start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
            end_time = datetime.strptime(end_str.strip(), "%H:%M").time()
            
            scheduled_start = timezone.make_aware(datetime.combine(booking_date, start_time), tz)
            scheduled_end = timezone.make_aware(datetime.combine(booking_date, end_time), tz)
        except Exception as e:
            form.add_error('time_slot', 'Invalid time slot selection.')
            return self.form_invalid(form)

        appointment = form.save(commit=False)
        appointment.scheduled_start = scheduled_start
        appointment.scheduled_end = scheduled_end
        appointment.status = Appointment.PENDING

        # Check availability: find an active mechanic who is NOT occupied during this window
        all_mechanics = User.objects.filter(role='MECHANIC', is_active=True)
        assigned_mechanic = None

        for mech in all_mechanics:
            overlapping = Appointment.objects.filter(
                mechanic=mech,
                status__in=[Appointment.CONFIRMED, Appointment.RESCHEDULED],
                scheduled_start__lt=scheduled_end,
                scheduled_end__gt=scheduled_start
            ).exists()
            if not overlapping:
                assigned_mechanic = mech
                break

        appointment.mechanic = assigned_mechanic
        appointment.save()

        # Send notifications
        notify_appointment_created(appointment)
        
        # Save appointment in session to show details on success page
        self.request.session['last_booking_id'] = appointment.id
        return super().form_valid(form)


class BookingSuccessView(TemplateView):
    template_name = 'appointments/success.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        booking_id = self.request.session.get('last_booking_id')
        if booking_id:
            ctx['appointment'] = Appointment.objects.filter(pk=booking_id).first()
        return ctx


class MechanicAvailabilityAPIView(View):
    """
    Returns mechanic capacity and occupancy for a given date.
    Can be queried via GET /appointments/api/availability/?date=YYYY-MM-DD
    """
    def get(self, request):
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': 'Date parameter required'}, status=400)
        
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

        # Get total mechanics
        total_mechanics = User.objects.filter(role='MECHANIC', is_active=True).count()
        if total_mechanics == 0:
            return JsonResponse({'date': date_str, 'slots': []})

        # List hourly slots from 09:00 to 18:00
        slots = []
        for hour in range(9, 18):
            start_str = f"{hour:02d}:00"
            end_str = f"{(hour+1):02d}:00"
            slot_key = f"{start_str}-{end_str}"
            
            tz = timezone.get_current_timezone()
            slot_start = timezone.make_aware(datetime.combine(query_date, datetime.strptime(start_str, "%H:%M").time()), tz)
            slot_end = timezone.make_aware(datetime.combine(query_date, datetime.strptime(end_str, "%H:%M").time()), tz)

            # Count active appointments overlapping this slot
            booked_count = Appointment.objects.filter(
                status__in=[Appointment.CONFIRMED, Appointment.PENDING, Appointment.RESCHEDULED],
                scheduled_start__lt=slot_end,
                scheduled_end__gt=slot_start
            ).count()

            available_slots = max(0, total_mechanics - booked_count)
            slots.append({
                'slot': slot_key,
                'label': f"{start_str} - {end_str}",
                'total_capacity': total_mechanics,
                'booked': booked_count,
                'available': available_slots,
                'status': 'available' if available_slots > 0 else 'full'
            })

        return JsonResponse({
            'date': date_str,
            'total_mechanics': total_mechanics,
            'slots': slots
        })


class AdminCalendarView(StaffOrOwnerRequiredMixin, TemplateView):
    template_name = 'appointments/calendar.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['mechanics'] = User.objects.filter(role='MECHANIC', is_active=True)
        ctx['service_types'] = ServiceType.objects.filter(is_active=True)
        ctx['status_choices'] = Appointment.STATUS_CHOICES
        return ctx


class AppointmentEventListView(LoginRequiredMixin, View):
    """
    Returns appointments formatted as FullCalendar events.
    Queried via GET /appointments/api/events/?start=...&end=...
    """
    def get(self, request):
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')
        
        qs = Appointment.objects.all().select_related('mechanic', 'service_type')
        
        # Parse ISO date strings from FullCalendar (usually YYYY-MM-DD or datetime format)
        if start_str:
            qs = qs.filter(scheduled_start__gte=start_str)
        if end_str:
            qs = qs.filter(scheduled_end__lte=end_str)

        # Filters
        status = request.GET.get('status')
        mechanic_id = request.GET.get('mechanic')
        
        if status:
            qs = qs.filter(status=status)
        if mechanic_id:
            qs = qs.filter(mechanic_id=mechanic_id)

        events = []
        for app in qs:
            # Pick a color based on status
            color = '#64748b'  # default grey (Pending)
            if app.status == Appointment.CONFIRMED:
                color = '#4f46e5'  # indigo
            elif app.status == Appointment.RESCHEDULED:
                color = '#f59e0b'  # amber
            elif app.status == Appointment.COMPLETED:
                color = '#10b981'  # emerald
            elif app.status == Appointment.CANCELLED:
                color = '#ef4444'  # red

            events.append({
                'id': app.id,
                'title': f"{app.customer_name} ({app.vehicle_number})",
                'start': app.scheduled_start.isoformat(),
                'end': app.scheduled_end.isoformat(),
                'color': color,
                'extendedProps': {
                    'customer_name': app.customer_name,
                    'customer_email': app.customer_email,
                    'customer_phone': app.customer_phone,
                    'vehicle_number': app.vehicle_number,
                    'vehicle_model': app.vehicle_model,
                    'service_type': app.service_type.name if app.service_type else 'General',
                    'service_type_id': app.service_type.id if app.service_type else '',
                    'mechanic': app.mechanic.get_full_name() if app.mechanic else 'Not Assigned',
                    'mechanic_id': app.mechanic.id if app.mechanic else '',
                    'status': app.status,
                    'notes': app.notes
                }
            })
        return JsonResponse(events, safe=False)


class AppointmentUpdateAPIView(StaffOrOwnerRequiredMixin, View):
    """
    Handles inline drag/drop updates and detail edits. Handles creation when pk is 0.
    """
    def post(self, request, pk):
        if pk == 0:
            appointment = Appointment()
        else:
            appointment = get_object_or_404(Appointment, pk=pk)
        
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'success': False, 'error': 'Invalid JSON body'}, status=400)

        # Drag/drop parameters
        start_str = data.get('start')
        end_str = data.get('end')
        
        if start_str and end_str:
            old_start = appointment.scheduled_start
            appointment.scheduled_start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            appointment.scheduled_end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            
            if appointment.scheduled_start != old_start:
                appointment.status = Appointment.RESCHEDULED
                notify_appointment_status_changed(appointment)

        # Form fields update
        if 'customer_name' in data:
            appointment.customer_name = data.get('customer_name')
        if 'customer_email' in data:
            appointment.customer_email = data.get('customer_email')
        if 'customer_phone' in data:
            appointment.customer_phone = data.get('customer_phone')
        if 'vehicle_number' in data:
            appointment.vehicle_number = data.get('vehicle_number')
        if 'vehicle_model' in data:
            appointment.vehicle_model = data.get('vehicle_model')
        if 'notes' in data:
            appointment.notes = data.get('notes')

        if 'service_type' in data:
            st_id = data.get('service_type')
            appointment.service_type = ServiceType.objects.filter(pk=st_id).first() if st_id else None

        if 'mechanic' in data:
            m_id = data.get('mechanic')
            appointment.mechanic = User.objects.filter(pk=m_id, role='MECHANIC').first() if m_id else None

        if 'status' in data:
            old_status = appointment.status
            new_status = data.get('status')
            if new_status in dict(Appointment.STATUS_CHOICES) and new_status != old_status:
                appointment.status = new_status
                notify_appointment_status_changed(appointment)

        appointment.save()
        return JsonResponse({'success': True})


class AppointmentActionView(StaffOrOwnerRequiredMixin, View):
    """
    Trigger actions: APPROVE, CANCEL, or CONVERT to Service Record.
    """
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        action = request.POST.get('action') or json.loads(request.body).get('action')
        
        if action == 'confirm':
            appointment.status = Appointment.CONFIRMED
            appointment.save()
            notify_appointment_status_changed(appointment)
            return JsonResponse({'success': True, 'message': 'Appointment confirmed successfully.'})
            
        elif action == 'cancel':
            appointment.status = Appointment.CANCELLED
            appointment.save()
            notify_appointment_status_changed(appointment)
            return JsonResponse({'success': True, 'message': 'Appointment cancelled successfully.'})

        elif action == 'convert':
            # Create a ServiceRecord from this appointment details
            if not appointment.mechanic:
                return JsonResponse({'success': False, 'error': 'Please assign a mechanic before converting to Service Record.'}, status=400)
            
            record = ServiceRecord.objects.create(
                vehicle_number=appointment.vehicle_number,
                vehicle_model=appointment.vehicle_model,
                customer_name=appointment.customer_name,
                customer_phone=appointment.customer_phone,
                service_type=appointment.service_type,
                mechanic=appointment.mechanic,
                status=ServiceRecord.PENDING,
                notes=appointment.notes,
                estimated_amount=appointment.service_type.base_charge if appointment.service_type else 0
            )

            # Copy checklist from service type
            if record.service_type:
                record.checklist = [
                    {'item': item, 'done': False}
                    for item in record.service_type.get_checklist()
                ]
                record.save()

            # Mark appointment as completed
            appointment.status = Appointment.COMPLETED
            appointment.save()
            notify_appointment_status_changed(appointment)

            return JsonResponse({
                'success': True, 
                'message': 'Converted to Service Record successfully.',
                'service_record_id': record.id
            })

        return JsonResponse({'success': False, 'error': 'Unknown action'}, status=400)


class AppointmentAnalyticsView(StaffOrOwnerRequiredMixin, TemplateView):
    template_name = 'appointments/analytics.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # Basic Stats
        total = Appointment.objects.count()
        pending = Appointment.objects.filter(status=Appointment.PENDING).count()
        confirmed = Appointment.objects.filter(status=Appointment.CONFIRMED).count()
        rescheduled = Appointment.objects.filter(status=Appointment.RESCHEDULED).count()
        completed = Appointment.objects.filter(status=Appointment.COMPLETED).count()
        cancelled = Appointment.objects.filter(status=Appointment.CANCELLED).count()

        ctx['stats'] = {
            'total': total,
            'pending': pending,
            'confirmed': confirmed,
            'rescheduled': rescheduled,
            'completed': completed,
            'cancelled': cancelled,
            'conversion_rate': round((completed / total * 100), 1) if total > 0 else 0
        }

        # Booking trends by date (last 7 days)
        today = timezone.localdate()
        date_range = [today - timedelta(days=i) for i in range(6, -1, -1)]
        
        trends = []
        for d in date_range:
            count = Appointment.objects.filter(scheduled_start__date=d).count()
            trends.append({
                'date': d.strftime('%Y-%m-%d'),
                'label': d.strftime('%b %d'),
                'count': count
            })
        ctx['trends_json'] = json.dumps(trends)

        # Status breakdown JSON
        status_data = [
            {'label': 'Pending', 'value': pending, 'color': '#64748b'},
            {'label': 'Confirmed', 'value': confirmed, 'color': '#4f46e5'},
            {'label': 'Rescheduled', 'value': rescheduled, 'color': '#f59e0b'},
            {'label': 'Completed', 'value': completed, 'color': '#10b981'},
            {'label': 'Cancelled', 'value': cancelled, 'color': '#ef4444'}
        ]
        ctx['status_json'] = json.dumps(status_data)

        # Mechanic occupancy (appointments per active mechanic)
        mechanics = User.objects.filter(role='MECHANIC', is_active=True)
        mech_data = []
        for mech in mechanics:
            count = Appointment.objects.filter(
                mechanic=mech,
                status__in=[Appointment.CONFIRMED, Appointment.RESCHEDULED]
            ).count()
            mech_data.append({
                'name': mech.get_full_name() or mech.username,
                'count': count
            })
        ctx['mechanic_json'] = json.dumps(mech_data)

        return ctx
