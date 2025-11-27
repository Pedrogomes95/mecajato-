from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.urls import reverse
from clientes import views as clientes_views
from servicos.models import Servico


def sitemap_xml(request):
    domain = request.scheme + '://' + request.get_host()
    # base URLs
    urls = [
        domain + reverse('clientes'),
        domain + reverse('listar_servico'),
        domain + reverse('login'),
    ]
    xml_items = []
    for u in urls:
        xml_items.append(f"  <url>\n    <loc>{u}</loc>\n  </url>")

    # include dynamic service pages
    try:
        # include only finalized services
        for serv in Servico.objects.filter(finalizado=True):
            if serv.identificador:
                loc = domain + reverse('servico', args=[serv.identificador])
                lastmod = ''
                if serv.data_inicio:
                    lastmod = f"\n    <lastmod>{serv.data_inicio.isoformat()}</lastmod>"
                xml_items.append(f"  <url>\n    <loc>{loc}</loc>{lastmod}\n  </url>")
    except Exception:
        # If models not available during migrations/import-time, skip dynamic entries
        pass
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '\n'.join(xml_items)
    xml += '\n</urlset>'
    return HttpResponse(xml, content_type='application/xml')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('clientes/', include('clientes.urls')),
    path('servicos/', include('servicos.urls')),
    path('login/', clientes_views.login_view, name='login'),
    path('logout/', clientes_views.logout_view, name='logout'),
    path('register/', clientes_views.register, name='register'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
    path('sitemap.xml', sitemap_xml, name='sitemap'),
]
