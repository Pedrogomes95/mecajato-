from django.templatetags.static import static
from django.conf import settings


def site_metadata(request):
    """Provide site-wide metadata for templates (SEO/OpenGraph defaults).

    Returns SITE_NAME, SITE_DESCRIPTION, SITE_KEYWORDS, SITE_TWITTER,
    SITE_OG_IMAGE (absolute URL) and SITE_URL.
    """
    site_name = getattr(settings, 'SITE_NAME', 'Mecajato')
    description = getattr(settings, 'SITE_DESCRIPTION', 'Sistema de gestão de oficina: clientes, serviços e agenda.')
    keywords = getattr(settings, 'SITE_KEYWORDS', 'oficina, mecânica, serviços, clientes, agendamento')
    twitter = getattr(settings, 'SITE_TWITTER', '')
    # SITE_OG_IMAGE in settings should be a static-relative path (e.g. 'general/img/og.png')
    og_image_setting = getattr(settings, 'SITE_OG_IMAGE', 'general/img/logo.png')
    try:
        og_image_static = static(og_image_setting)
    except Exception:
        og_image_static = og_image_setting
    try:
        og_image = request.build_absolute_uri(og_image_static)
        site_url = request.build_absolute_uri('/')
    except Exception:
        og_image = og_image_static
        site_url = '/'

    return {
        'SITE_NAME': site_name,
        'SITE_DESCRIPTION': description,
        'SITE_KEYWORDS': keywords,
        'SITE_TWITTER': twitter,
        'SITE_OG_IMAGE': og_image,
        'SITE_URL': site_url,
    }
