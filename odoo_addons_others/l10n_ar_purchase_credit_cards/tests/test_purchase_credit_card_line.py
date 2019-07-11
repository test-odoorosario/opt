# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from dateutil.relativedelta import relativedelta
from odoo.tests import common
from odoo import fields
from odoo.exceptions import ValidationError


class TestPurchaseCreditCardLine(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseCreditCardLine, self).setUp()

    def test_pago_sin_cuotas_lanza_excepcion(self):
        line = self.env['purchase.credit.card.line'].new({'fees': 0})
        with self.assertRaises(ValidationError):
            line.constraint_values()

    def test_pago_de_una_cuota_crea_una_cuota(self):
        account = self.env['account.account'].new({})
        credit_card = self.env['credit.card'].new({
            'name': 'Test tarjeta de credito',
            'account_id': account
        })
        credit_card_line = self.env['purchase.credit.card.line'].new({
            'credit_card_id': credit_card,
            'amount': 1000,
            'fees': 1,
            'description': 'Test tarjeta',
            'payment_id': self.env['account.payment'].new({
                'payment_date': fields.Date.from_string(fields.Date.today())
            })
        })
        values = credit_card_line.get_card_fee_values()[0]

        assert_values = {
            'name': credit_card_line.description,
            'credit_card_line_id': credit_card_line.id,
            'total_fees': 1,
            'fee': 1,
            'due_date': fields.Date.from_string(fields.Date.today()),
            'amount': 1000
        }
        assert values == assert_values

    def test_pago_de_varias_cuotas_crea_varias_cuotas(self):
        account = self.env['account.account'].new({})
        credit_card = self.env['credit.card'].new({
            'name': 'Test tarjeta de credito',
            'account_id': account
        })
        credit_card_line = self.env['purchase.credit.card.line'].new({
            'credit_card_id': credit_card,
            'amount': 1000,
            'fees': 3,
            'description': 'Test tarjeta',
            'payment_id': self.env['account.payment'].new({
                'payment_date': fields.Date.from_string(fields.Date.today())
            })
        })

        values = credit_card_line.get_card_fee_values()
        assert_values_1 = {
            'name': credit_card_line.description,
            'credit_card_line_id': credit_card_line.id,
            'total_fees': 3,
            'fee': 1,
            'due_date': fields.Date.from_string(fields.Date.today()),
            'amount': 333.33
        }
        assert_values_2 = assert_values_1.copy()
        assert_values_2['fee'] = 2
        assert_values_2['due_date'] = fields.Date.from_string(fields.Date.today()) + relativedelta(months=1)

        assert_values_3 = assert_values_1.copy()
        assert_values_3['fee'] = 3
        assert_values_3['due_date'] = fields.Date.from_string(fields.Date.today()) + relativedelta(months=2)
        assert_values_3['amount'] = 333.34

        assert values == [assert_values_1, assert_values_2, assert_values_3]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
