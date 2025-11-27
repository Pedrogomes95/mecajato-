import os
import sys
import json

# Ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mecajato.settings')
import django
django.setup()

from servicos.models import Servico

def serialize_servico(s):
    return {
        'id': s.id,
        'identificador': s.identificador,
        'titulo': s.titulo,
        'finalizado': bool(s.finalizado),
        'data_inicio': s.data_inicio.isoformat() if s.data_inicio else None,
        'preco_total': float(s.preco_total()) if hasattr(s, 'preco_total') else None,
    }

servicos = list(Servico.objects.all())
out = [serialize_servico(s) for s in servicos]
print(json.dumps({'count': len(out), 'servicos': out}, ensure_ascii=False, indent=2))
