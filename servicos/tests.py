from django.test import TestCase
from clientes.models import Cliente
from .models import Servico, CategoriaManutencao
from django.urls import reverse
from datetime import date


class ServicosBasicTests(TestCase):
	def setUp(self):
		self.cliente = Cliente.objects.create(nome='Ana', sobrenome='Lima', email='ana@example.com', cpf='98765432100')
		self.categoria = CategoriaManutencao.objects.create(titulo='TO', preco=100.00)

	def test_create_servico_and_list_view(self):
		servico = Servico.objects.create(titulo='Troca de óleo', cliente=self.cliente, data_inicio=date.today(), data_entrega=date.today())
		servico.categoria_manutencao.add(self.categoria)

		self.assertEqual(str(servico), 'Troca de óleo')

		resp = self.client.get(reverse('listar_servico'))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Troca de óleo')

