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
from datetime import date
from ..models import payment


class TestAccumulated(common.TransactionCase):

    """ CREACION DE RECORDS PARA TESTS """
    def _create_pos_data(self):
        self.pos_inbound = self.env['pos.ar'].create({
            'name': '1'
        })
        self.pos_outbound = self.env['pos.ar'].create({
            'name': '10'
        })
        self.document_book_outbound = self.env['document.book'].with_context(default_payment_type='outbound').create({
            'name': '1',
            'category': 'payment',
            'pos_ar_id': self.pos_outbound.id,
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_payment').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_outbound').id
        })
        self.document_book_invoice = self.env['document.book'].create({
            'name': '1',
            'category': 'invoice',
            'pos_ar_id': self.pos_inbound.id,
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_invoice').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_invoice').id,
            'denomination_id': self.env.ref('l10n_ar_afip_tables.account_denomination_a').id
        })

    def _create_payments(self):
        payment_proxy = self.env['account.payment']
        payment_1 = payment_proxy.create({
            'payment_date': date.today(), 'partner_id': self.partner.id, 'state': 'draft',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'payment_type': 'outbound', 'amount': 500
        })
        payment_2 = payment_proxy.create({
            'payment_date': date.today()+relativedelta(months=1), 'partner_id': self.partner.id, 'state': 'posted',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'payment_type': 'outbound', 'amount': 500
        })
        payment_3 = payment_proxy.create({
            'payment_date': date.today().replace(day=1), 'partner_id': self.partner.id, 'state': 'reconciled',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'payment_type': 'outbound', 'amount': 5200
        })
        payment_4 = payment_proxy.create({
            'partner_id': self.partner.id, 'payment_date': date.today(), 'state': 'posted',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'payment_type': 'outbound', 'amount': 1500
        })
        return payment_1 | payment_2 | payment_3 | payment_4

    def _create_invoice(self, amount, tax=None, name=None):
        invoice_proxy = self.env['account.invoice']
        invoice_line_proxy = self.env['account.invoice.line']
        product_21_consu = self.env['product.product'].create({
            'name': '21 consu',
            'type': 'consu',
            'supplier_taxes_id':  [(6, 0, [tax.id])] if tax else None
        })

        invoice = invoice_proxy.create({
            'partner_id': self.partner.id,
            'type': 'in_invoice',
            'name': name or '0001-00000001'
        })
        invoice.onchange_partner_id()
        invoice_line = invoice_line_proxy.create({
            'name': 'product_21_test',
            'product_id': product_21_consu.id,
            'price_unit': 0,
            'account_id': product_21_consu.categ_id.property_account_income_categ_id.id,
            'invoice_id': invoice.id
        })
        invoice_line._onchange_product_id()
        invoice_line.price_unit = amount
        invoice._onchange_invoice_line_ids()
        return invoice

    """ HELPERS """
    def _validate_payments(self, payments):
        payments.write({
            'state': 'draft',
            'pos_ar_id': payments[0].get_pos(payments[0].payment_type),
        })
        payment_type_transfer = self.env['account.payment.type'].create({
            'name': 'Transferencia',
            'account_id': self.env.ref('l10n_ar.1_banco').id,
        })
        for paym in payments:
            self.env['account.payment.type.line'].create({
                'account_payment_type_id': payment_type_transfer.id,
                'payment_id': paym.id,
                'amount': paym.amount
            })
        payments.post_l10n_ar()

    def _associate_invoice_with_payment(self, invoice, paym, amount):
        self.env['payment.imputation.line'].create({
            'payment_id': paym.id,
            'invoice_id': invoice.id,
            'move_line_id': invoice.move_id.line_ids.filtered(lambda x: x.account_id == invoice.account_id).id,
            'amount': amount
        })

    def setUp(self):
        super(TestAccumulated, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test',
            'property_account_position_id': self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari').id
        })
        self._create_pos_data()
        self.env.user.company_id.account_position_id = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari')

    def test_get_accumulated_payments(self):
        self._create_payments()
        payments = payment.get_accumulated_payments(self.env['account.payment'], self.partner, date.today())
        assert len(payments) == 2

    def test_accumulated_no_invoices(self):
        self._create_payments()
        payments = payment.get_accumulated_payments(self.env['account.payment'], self.partner, date.today())
        self._validate_payments(payments)
        assert payments.get_accumulated_amount() == 6700

    def test_accumulated_with_invoice_with_tax(self):
        self._create_payments()
        payments = payment.get_accumulated_payments(self.env['account.payment'], self.partner, date.today())[0]
        invoice = self._create_invoice(payments[0].amount/1.21, self.env.ref('l10n_ar.1_vat_21_compras'))
        invoice.action_invoice_open()
        payments[0].invoice_ids = [(6, 0, [invoice.id])]
        self._associate_invoice_with_payment(invoice, payments[0], invoice.amount_total_signed)
        self._validate_payments(payments[0])
        assert payments[0].get_accumulated_amount() == invoice.amount_to_tax

    def test_accumulated_with_invoice_without_tax(self):
        self._create_payments()
        payments = payment.get_accumulated_payments(self.env['account.payment'], self.partner, date.today())[0]
        invoice = self._create_invoice(payments[0].amount)
        invoice.action_invoice_open()
        payments[0].invoice_ids = [(6, 0, [invoice.id])]
        self._associate_invoice_with_payment(invoice, payments[0], invoice.amount_total_signed)
        self._validate_payments(payments[0])
        assert not payments[0].get_accumulated_amount()

    def test_accumulated_with_invoice_with_and_without_tax(self):
        self._create_payments()
        payments = payment.get_accumulated_payments(self.env['account.payment'], self.partner, date.today())[0]
        invoice = self._create_invoice(10000, self.env.ref('l10n_ar.1_vat_21_compras'))
        # Agregamos una linea sin impuesto
        self.env['account.invoice.line'].create({
            'name': 'line without tax',
            'price_unit': 5000,
            'invoice_id': invoice.id,
            'account_id': self.env.ref('l10n_ar.1_ingresos_por_ventas').id
        })
        invoice._onchange_invoice_line_ids()
        invoice.action_invoice_open()
        payments[0].invoice_ids = [(6, 0, [invoice.id])]
        payments[0].amount = 17100
        self._associate_invoice_with_payment(invoice, payments[0], invoice.amount_total_signed)
        self._validate_payments(payments[0])
        assert payments[0].get_accumulated_amount() == 10000

    def test_accumulated_with_invoice_and_advance_amount(self):
        self._create_payments()
        payments = payment.get_accumulated_payments(self.env['account.payment'], self.partner, date.today())[0]
        invoice = self._create_invoice(10000, self.env.ref('l10n_ar.1_vat_21_compras'))
        invoice.action_invoice_open()
        payments[0].invoice_ids = [(6, 0, [invoice.id])]
        payments[0].amount = 15000
        payments[0].advance_amount = 2900
        self._associate_invoice_with_payment(invoice, payments[0], 12100)
        self._validate_payments(payments[0])
        assert payments[0].get_accumulated_amount() == 12900

    def test_multiple_invoices(self):
        self._create_payments()
        payments = payment.get_accumulated_payments(self.env['account.payment'], self.partner, date.today())[0]
        invoice = self._create_invoice(10000, self.env.ref('l10n_ar.1_vat_21_compras'))
        invoice.action_invoice_open()
        invoice2 = self._create_invoice(10000, name='0001-00000002')
        invoice2.action_invoice_open()
        payments[0].invoice_ids = [(6, 0, [invoice.id, invoice2.id])]
        payments[0].amount = 22100
        self._associate_invoice_with_payment(invoice, payments[0], 12100)
        self._associate_invoice_with_payment(invoice2, payments[0], 10000)
        self._validate_payments(payments[0])
        assert payments[0].get_accumulated_amount() == 10000

    def test_multiple_invoices_with_advance_amount(self):
        self._create_payments()
        payments = payment.get_accumulated_payments(self.env['account.payment'], self.partner, date.today())[0]
        invoice = self._create_invoice(10000, self.env.ref('l10n_ar.1_vat_21_compras'))
        invoice.action_invoice_open()
        invoice2 = self._create_invoice(10000, name='0001-00000002')
        invoice2.action_invoice_open()
        payments[0].invoice_ids = [(6, 0, [invoice.id, invoice2.id])]
        payments[0].amount = 30000
        payments[0].advance_amount = 7900
        self._associate_invoice_with_payment(invoice, payments[0], 12100)
        self._associate_invoice_with_payment(invoice2, payments[0], 10000)
        self._validate_payments(payments[0])
        assert payments[0].get_accumulated_amount() == 17900

    def test_multiple_payments_and_multiple_invoices_with_advance_amount(self):
        self._create_payments()
        payments = payment.get_accumulated_payments(self.env['account.payment'], self.partner, date.today())
        invoice = self._create_invoice(10000, self.env.ref('l10n_ar.1_vat_21_compras'))
        invoice.action_invoice_open()
        invoice2 = self._create_invoice(10000, name='0001-00000002')
        invoice2.action_invoice_open()
        payments[0].invoice_ids = [(6, 0, [invoice.id])]
        payments[0].amount = 12100
        payments[1].invoice_ids = [(6, 0, [invoice2.id])]
        payments[1].amount = 15000
        payments[1].advance_amount = 5000
        self._associate_invoice_with_payment(invoice, payments[0], 12100)
        self._associate_invoice_with_payment(invoice2, payments[1], 10000)
        self._validate_payments(payments)
        assert payments.get_accumulated_amount() == 15000

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
