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

from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class TestPaymentImputationWizard(TransactionCase):

    def _create_invoice(self):
        invoice_proxy = self.env['account.invoice']
        invoice_line_proxy = self.env['account.invoice.line']
        product_21_consu = self.env['product.product'].create({
            'name': '21 consu',
            'type': 'consu',
            'taxes_id': [(6, 0, [self.env.ref('l10n_ar.1_vat_21_compras').id])]
        })
        self.invoice = invoice_proxy.create({
            'partner_id': self.partner.id,
            'type': 'in_invoice',
            'name': '0001-00000001'
        })
        self.invoice.onchange_partner_id()
        invoice_line = invoice_line_proxy.create({
            'name': 'product_21_test',
            'product_id': product_21_consu.id,
            'price_unit': 0,
            'account_id': product_21_consu.categ_id.property_account_income_categ_id.id,
            'invoice_id': self.invoice.id
        })
        invoice_line._onchange_product_id()
        invoice_line.price_unit = 1000
        self.invoice._onchange_invoice_line_ids()
        self.invoice.action_invoice_open()
        # Nota de credito
        self.refund_invoice = invoice_proxy.create({
            'partner_id': self.partner.id,
            'type': 'in_refund',
            'name': '0001-00000001'
        })
        self.refund_invoice.onchange_partner_id()
        refund_invoice_line = invoice_line_proxy.create({
            'name': 'product_21_test',
            'product_id': product_21_consu.id,
            'price_unit': 0,
            'account_id': product_21_consu.categ_id.property_account_income_categ_id.id,
            'invoice_id': self.refund_invoice.id
        })
        refund_invoice_line._onchange_product_id()
        refund_invoice_line.price_unit = 1000
        self.refund_invoice._onchange_invoice_line_ids()
        self.refund_invoice.action_invoice_open()

    def setUp(self):
        super(TestPaymentImputationWizard, self).setUp()

        self.iva_ri = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari')
        self.env.user.company_id.partner_id.property_account_position_id = self.iva_ri

        self.partner = self.env['res.partner'].create({
            'name': 'Partner',
            'supplier': True,
            'customer': True,
            'property_account_position_id': self.iva_ri.id,

        })
        self.payment_imputation_wizard = self.env['payment.imputation.wizard'].create({
            'partner_id': self.partner.id,
            'payment_type': 'outbound'
        })

    def test_create_payment_imputation_credits(self):
        self._create_invoice()
        self.payment_imputation_wizard.onchange_partner_id()
        self.payment_imputation_wizard.debit_imputation_line_ids.write({
            'amount': 500
        })
        self.payment_imputation_wizard.credit_imputation_line_ids.write({
            'amount': 400
        })
        res = self.payment_imputation_wizard.create_payment()
        payment = self.env['account.payment'].browse(res.get('res_id'))
        assert payment.partner_type == 'supplier'
        assert payment.payment_type == 'outbound'
        assert payment.partner_id == self.partner
        assert payment.amount == 100
        assert payment.imputation_credit_ids
        assert payment.imputation_credit_ids[0].amount == 400
        assert payment.imputation_debit_ids[0].amount == 500



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
