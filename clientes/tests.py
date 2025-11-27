from django.test import TestCase
from .models import Cliente, Carro
from django.urls import reverse


class ClientesBasicTests(TestCase):
	def test_cliente_creation_and_list_view(self):
		# cria um cliente
		cliente = Cliente.objects.create(
			nome='Joao', sobrenome='Silva', email='joao@example.com', cpf='12345678901'
		)
		# cria um carro associado
		Carro.objects.create(carro='Fusca', placa='ABC1234', ano=1990, cliente=cliente)

		# verifica representação
		self.assertEqual(str(cliente), 'Joao')

		# verifica a view de listagem de clientes
		resp = self.client.get(reverse('clientes'))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Joao')

