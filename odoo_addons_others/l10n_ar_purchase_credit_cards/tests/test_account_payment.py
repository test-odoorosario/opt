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

from odoo.tests import common
from mock import mock
payment_methods = 'odoo.addons.l10n_ar_account_check.models.' \
                    'account_payment.AccountPayment'
abstract_payment_methods = 'odoo.addons.l10n_ar_account_check.models.' \
                    'account_payment.AccountAbstractPayment'
credit_cards_methods = 'odoo.addons.l10n_ar_purchase_credit_cards.models.' \
                    'purchase_credit_card_line.PurchaseCreditCard'


class TestAccountPayment(common.TransactionCase):

    def setUp(self):
        super(TestAccountPayment, self).setUp()

    def test_el_validar_del_pago_pago_crea_cuotas(self):
        credit_card = self.env['credit.card'].new({
            'name': 'Test tarjeta de credito',
            'account_id': self.env['account.account'].new({})
        })
        credit_card_line = self.env['purchase.credit.card.line'].new({
            'credit_card_id': credit_card,
            'amount': 1000,
            'fee': 1
        })
        payment = self.env['account.payment'].new({
            'purchase_credit_card_line_ids': credit_card_line,
        })

        with mock.patch(payment_methods+'.post_l10n_ar') as post_mock,\
                mock.patch(credit_cards_methods+'.create_fees') as post_credit_mock:
            post_mock.return_value = True
            payment.post_l10n_ar()
            post_credit_mock.assert_called_once()

    def test_el_cancelar_del_pago_borra_cuotas(self):
        credit_card = self.env['credit.card'].new({
            'name': 'Test tarjeta de credito',
            'account_id': self.env['account.account'].new({})
        })
        credit_card_line = self.env['purchase.credit.card.line'].new({
            'credit_card_id': credit_card,
            'amount': 1000,
            'fee': 1
        })
        payment = self.env['account.payment'].new({
            'purchase_credit_card_line_ids': credit_card_line,
        })

        with mock.patch(payment_methods+'.cancel') as post_mock, \
                mock.patch(credit_cards_methods+'.delete_fees') as post_credit_mock:
            post_mock.return_value = True
            payment.cancel()
            post_credit_mock.assert_called_once()

    def test_pago_con_una_tarjeta_carga_los_importes_para_el_asiento(self):
        account = self.env['account.account'].new({})
        credit_card = self.env['credit.card'].new({
            'name': 'Test tarjeta de credito',
            'account_id': account
        })
        credit_card_lines = self.env['purchase.credit.card.line'].new({
            'credit_card_id': credit_card,
            'amount': 1000,
            'fees': 1
        })
        payment = self.env['account.payment'].new({
            'purchase_credit_card_line_ids': credit_card_lines,
        })
        with mock.patch(abstract_payment_methods+'.set_payment_methods_vals') as vals_mock:
            vals_mock.return_value = []
            vals = payment.set_payment_methods_vals()
            assert vals[0]['amount'] == 1000
            assert vals[0]['account_id'] == account.id

    def test_pago_con_varias_tarjetas_carga_los_importes_para_el_asiento(self):
        account = self.env['account.account'].new({})
        credit_card = self.env['credit.card'].new({
            'name': 'Test tarjeta de credito',
            'account_id': account
        })
        credit_card_lines = self.env['purchase.credit.card.line'].new({
            'credit_card_id': credit_card,
            'amount': 1000,
            'fees': 1
        }) | self.env['purchase.credit.card.line'].new({
            'credit_card_id': credit_card,
            'amount': 1200,
            'fees': 2
        })
        payment = self.env['account.payment'].new({
            'purchase_credit_card_line_ids': credit_card_lines,
        })
        with mock.patch(abstract_payment_methods+'.set_payment_methods_vals') as vals_mock:
            vals_mock.return_value = []
            vals = payment.set_payment_methods_vals()
            assert vals[0]['amount'] == 1000
            assert vals[0]['account_id'] == account.id
            assert vals[1]['amount'] == 1200
            assert vals[1]['account_id'] == account.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
