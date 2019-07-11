# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError
import pytest


class TestExpensePost(TransactionCase):

    def create_payment_method(self):
        self.payment_method = self.env['account.payment.method'].create({
            'name': 'Payment method',
            'code': '111',
            'payment_type': 'outbound'
        })

    def create_pos_ar(self):
        self.iva_ri = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari')
        self.company_fiscal_position = self.env.user.company_id.partner_id.property_account_position_id
        self.document_book_proxy = self.env['document.book']
        self.pos_proxy = self.env['pos.ar']
        # Configuracion de posicion fiscal RI en la compania
        self.env.user.company_id.partner_id.property_account_position_id = self.iva_ri
        self.pos_outbound = self.env['pos.ar'].create({
            'name': '10'
        })
        self.document_book_outbound = self.env['document.book'].with_context(default_payment_type='outbound').create({
            'name': '11',
            'category': 'payment',
            'pos_ar_id': self.pos_outbound.id,
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_payment').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_outbound').id
        })

    def create_partner(self):
        self.partner = self.env['res.partner'].create({
            'name': 'Partner',
            'customer': True,
            'supplier': True,
        })

    def create_journal(self):
        self.account_journal = self.env['account.account'].create({
            'name': 'Cuenta diario',
            'code': 10001,
            'user_type_id': self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })
        self.journal = self.env['account.journal'].create({
            'name': 'Diario',
            'code': 'DIA',
            'type': 'bank',
            'default_debit_account_id': self.account_journal.id,
            'default_credit_account_id': self.account_journal.id,
        })

    def setUp(self):
        super(TestExpensePost, self).setUp()
        self.create_partner()
        self.create_journal()
        self.create_payment_method()

    @pytest.mark.skip(reason="Solo ejecutar manualmente ya que se instala dependiendo de otros modulos que no son de la localizacion")
    def test_posteo_gasto_sin_talonario_para_pagos(self):
        wizard = self.env['hr.expense.register.payment.wizard'].create({
            'journal_id': self.journal.id,
            'partner_id': self.partner.id,
            'amount': 100,
            'payment_method_id': self.payment_method.id
        })
        with self.assertRaises(ValidationError):
            wizard.expense_post_payment()

    @pytest.mark.skip(reason="Solo ejecutar manualmente ya que se instala dependiendo de otros modulos que no son de la localizacion")
    def test_posteo_de_localizacion_gasto_sin_talonario_para_pagos(self):
        wizard = self.env['hr.expense.register.payment.wizard'].create({
            'journal_id': self.journal.id,
            'partner_id': self.partner.id,
            'amount': 100,
            'payment_method_id': self.payment_method.id
        })
        with self.assertRaises(ValidationError):
            wizard.expense_post_l10n_ar_payment()

    @pytest.mark.skip(reason="Solo ejecutar manualmente ya que se instala dependiendo de otros modulos que no son de la localizacion")
    def test_posteo_de_localizacion_gasto_con_talonario_para_pagos(self):
        self.create_pos_ar()
        payment_type = self.env["account.payment.type"].create({
            "name": "Transferencia",
            "account_id": self.env.ref("l10n_ar.1_banco").id,
        })
        wizard = self.env['hr.expense.register.payment.wizard'].create({
            'journal_id': self.journal.id,
            'partner_id': self.partner.id,
            'amount': 100,
            'payment_method_id': self.payment_method.id
        })
        payment_line = self.env["account.payment.type.line"].create({
            "account_payment_type_id": payment_type.id,
            "amount": 100,
        })
        wizard.payment_type_line_ids = [(6, 0, [payment_line.id])]
        wizard.expense_post_l10n_ar_payment()

    @pytest.mark.skip(reason="Solo ejecutar manualmente ya que se instala dependiendo de otros modulos que no son de la localizacion")
    def test_posteo_de_localizacion_gasto_con_talonario_para_pagos_desbalanceado(self):
        self.create_pos_ar()
        payment_type = self.env["account.payment.type"].create({
            "name": "Transferencia",
            "account_id": self.env.ref("l10n_ar.1_banco").id,
        })
        wizard = self.env['hr.expense.register.payment.wizard'].create({
            'journal_id': self.journal.id,
            'partner_id': self.partner.id,
            'amount': 100,
            'payment_method_id': self.payment_method.id
        })
        self.env["account.payment.type.line"].create({
            "account_payment_type_id": payment_type.id,
            "line_id": wizard.id,
            "amount": 1010,
        })
        with self.assertRaises(UserError):
            wizard.expense_post_l10n_ar_payment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
