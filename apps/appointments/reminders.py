import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils.formats import date_format

logger = logging.getLogger(__name__)


def send_appointment_email(appointment, subject, template_text):
    """Utility to send emails to customers."""
    if not appointment.customer_email:
        return False
    
    try:
        send_mail(
            subject=subject,
            message=template_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.customer_email],
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {appointment.customer_email} for appointment {appointment.id}")
        print(f"\n[SMTP SUCCESS] Email sent successfully to {appointment.customer_email}!\n")
        return True
    except Exception as e:
        logger.error(f"Error sending email to {appointment.customer_email}: {e}")
        print(f"\n[SMTP ERROR] Failed to send email to {appointment.customer_email}. Error: {e}\n")
        return False


def send_appointment_sms(appointment, message_content):
    """Simulates sending an SMS reminder (logs/prints to console)."""
    # In a real environment, you would call an API like Twilio or Vonage here.
    simulated_log = (
        f"\n=== [SIMULATED SMS SENT] ===\n"
        f"To: {appointment.customer_phone}\n"
        f"Body: {message_content}\n"
        f"=============================\n"
    )
    # Log to django logs and print to standard output
    logger.info(simulated_log)
    print(simulated_log)
    return True


def get_appointment_messages(appointment):
    """Generate email subject, email body, and SMS body for a new appointment."""
    start_time_str = appointment.scheduled_start.strftime("%B %d, %Y at %I:%M %p")
    subject = "Service Booking Received - Amar Honda Care"
    
    email_body = (
        f"Hello {appointment.customer_name},\n\n"
        f"Thank you for booking a service slot with Amar Honda Care!\n\n"
        f"Booking Details:\n"
        f"- Vehicle: {appointment.vehicle_model} ({appointment.vehicle_number})\n"
        f"- Service Type: {appointment.service_type.name if appointment.service_type else 'General'}\n"
        f"- Requested Time: {start_time_str}\n"
        f"- Status: Pending Confirmation\n\n"
        f"We will review your booking and send a confirmation shortly. If you need to reschedule or have any questions, please reply to this email.\n\n"
        f"Best regards,\n"
        f"Amar Honda Care Team"
    )
    
    sms_body = (
        f"Amar Honda Care: Hello {appointment.customer_name}, we've received your service booking for {appointment.vehicle_number} "
        f"on {appointment.scheduled_start.strftime('%d-%m-%Y')} at {appointment.scheduled_start.strftime('%I:%M %p')}. "
        f"We will confirm shortly!"
    )
    return subject, email_body, sms_body


def notify_appointment_created(appointment):
    """Send notifications when an appointment is booked."""
    subject, email_body, sms_body = get_appointment_messages(appointment)
    send_appointment_email(appointment, subject, email_body)
    send_appointment_sms(appointment, sms_body)


def notify_appointment_status_changed(appointment):
    """Send notifications when status changes (CONFIRMED, RESCHEDULED, CANCELLED)."""
    start_time_str = appointment.scheduled_start.strftime("%B %d, %Y at %I:%M %p")
    status = appointment.status
    
    subject = f"Service Booking {status.title()} - Amar Honda Care"
    
    status_msg = ""
    if status == appointment.CONFIRMED:
        status_msg = f"Your appointment has been CONFIRMED. A mechanic is assigned to look after your vehicle."
    elif status == appointment.RESCHEDULED:
        status_msg = f"Your appointment has been RESCHEDULED to: {start_time_str}."
    elif status == appointment.CANCELLED:
        status_msg = f"Your appointment has been CANCELLED. If this was a mistake, please reach out to us."
    elif status == appointment.COMPLETED:
        status_msg = f"Your service has been COMPLETED! Thank you for choosing Amar Honda Care."
    else:
        return

    email_body = (
        f"Hello {appointment.customer_name},\n\n"
        f"{status_msg}\n\n"
        f"Details:\n"
        f"- Vehicle: {appointment.vehicle_model} ({appointment.vehicle_number})\n"
        f"- Time: {start_time_str}\n"
        f"- Status: {appointment.get_status_display()}\n\n"
        f"If you need any help, please contact us.\n\n"
        f"Best regards,\n"
        f"Amar Honda Care Team"
    )
    send_appointment_email(appointment, subject, email_body)

    sms_body = (
        f"Amar Honda Care: Hi {appointment.customer_name}, your booking for {appointment.vehicle_number} "
        f"is now {appointment.get_status_display()} for {appointment.scheduled_start.strftime('%d-%m-%Y %I:%M %p')}."
    )
    send_appointment_sms(appointment, sms_body)
