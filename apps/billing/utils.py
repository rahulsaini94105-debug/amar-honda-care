import os
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa


def link_callback(uri, rel):
    """
    Convert HTML static/media URLs to local absolute paths so xhtml2pdf can access them.
    """
    # If the URI starts with STATIC_URL, convert it to the static path
    if uri.startswith(settings.STATIC_URL):
        # Remove STATIC_URL from the beginning of the URI
        relative_path = uri[len(settings.STATIC_URL):]
        # Try STATICFILES_DIRS first, then STATIC_ROOT
        found_path = None
        if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
            for directory in settings.STATICFILES_DIRS:
                full_path = os.path.join(directory, relative_path)
                if os.path.exists(full_path):
                    found_path = full_path
                    break
        if not found_path:
            # Fall back to BASE_DIR/static or STATIC_ROOT
            full_path = os.path.join(settings.BASE_DIR, 'static', relative_path)
            if os.path.exists(full_path):
                found_path = full_path
            elif settings.STATIC_ROOT:
                full_path = os.path.join(settings.STATIC_ROOT, relative_path)
                if os.path.exists(full_path):
                    found_path = full_path
        if found_path:
            return found_path
            
    elif uri.startswith(settings.MEDIA_URL):
        relative_path = uri[len(settings.MEDIA_URL):]
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        if os.path.exists(full_path):
            return full_path
            
    return uri


def render_to_pdf(template_src, context={}):
    template = get_template(template_src)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(
        BytesIO(html.encode('UTF-8')),
        result,
        link_callback=link_callback
    )
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def generate_invoice_pdf(invoice):
    context = {'invoice': invoice, 'items': invoice.items.select_related('product').all()}
    return render_to_pdf('billing/invoice_pdf.html', context)
