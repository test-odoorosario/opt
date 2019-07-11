# coding: utf-8
##############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from odoo.tests import common
from datetime import date


class SetUp(common.TransactionCase):
    def setUp(self):
        super(SetUp, self).setUp()
        # traemos el diario
        journal = self.env.ref("l10n_ar_account_payment.journal_cobros_y_pagos")
        journal.update_posted = True
        # configuramos la posicion en la compania
        iva_ri = self.env.ref("l10n_ar_afip_tables.account_fiscal_position_ivari")
        self.env.user.company_id.partner_id.property_account_position_id = iva_ri
        # creamos el partner
        partner = self.env["res.partner"].create({
            "name": "Test Partner",
            "supplier": True,
            "customer": True,
            "property_account_position_id": self.env.ref("l10n_ar_afip_tables.account_fiscal_position_ivari").id,
        })
        # creamos el punto de venta
        pos = self.env["pos.ar"].create({
            "name": "9"
        })
        # creamos el talonario para la factura
        invoice_book = self.env["document.book"].create({
            "name": "1",
            "category": "invoice",
            "pos_ar_id": pos.id,
            "book_type_id": self.env.ref("l10n_ar_point_of_sale.document_book_type_preprint_invoice").id,
            "document_type_id": self.env.ref("l10n_ar_point_of_sale.document_type_invoice").id,
            "denomination_id": self.env.ref("l10n_ar_afip_tables.account_denomination_a").id
        })
        # creamos el talonario para el pago
        payment_book = self.env["document.book"].with_context(default_payment_type="inbound").create({
            "name": "1",
            "category": "payment",
            "pos_ar_id": pos.id,
            "book_type_id": self.env.ref("l10n_ar_point_of_sale.document_book_type_preprint_payment").id,
            "document_type_id": self.env.ref("l10n_ar_point_of_sale.document_type_inbound").id
        })
        # cremos el metodo de pago
        payment_type = self.env["account.payment.type"].create({
            "name": "Transferencia",
            "account_id": self.env.ref("l10n_ar.1_banco").id,
        })
        # creamos el producto
        product = self.env["product.product"].create({
            "name": "Test Product",
            "type": "consu",
            "taxes_id": [(6, 0, [self.env.ref("l10n_ar.1_vat_21_ventas").id])]
        })
        # creamos la factura
        invoice = self.env["account.invoice"].create({
            "partner_id": partner.id,
            "type": "out_invoice"
        })
        # hacemos el onchange del partner
        invoice.onchange_partner_id()
        # cremamos la linea de la factura
        invoice_line = self.env["account.invoice.line"].create({
            "name": "Test Product 1",
            "product_id": product.id,
            "price_unit": 0,
            "account_id": product.categ_id.property_account_income_categ_id.id,
            "invoice_id": invoice.id
        })
        # llamamos al onchange de product id
        invoice_line._onchange_product_id()
        # cambiamos el precio unitario del producto para la linea
        invoice_line.price_unit = 1000
        # llamamos al onchange de invoice line ids
        invoice._onchange_invoice_line_ids()
        # validamos la factura
        invoice.action_invoice_open()
        # creamos el pago
        payment = self.env["account.payment"].create({
            "invoice_ids": [(6, 0, [invoice.id])],
            "partner_id": partner.id,
            "payment_type": "inbound",
            "partner_type": "customer",
            "payment_method_id": self.env.ref("account.account_payment_method_manual_in").id,
            "amount": 1210,
            "pos_ar_id": pos.id,
        })
        # creamos la linea del pago
        payment_line = self.env["account.payment.type.line"].create({
            "account_payment_type_id": payment_type.id,
            "payment_id": payment.id,
            "amount": 1120,
        })
        bank_card = self.env["bank.card"].create({
            "name": "Mostercard",
            "bank_account_id": journal.id,
            "account_id": product.categ_id.property_account_income_categ_id.id
        })
        bank_card_fee = self.env["bank.card.fee"].create({
            "name": "Mostercard 6 Cuotas",
            "bank_card_id": bank_card.id,
            "fee_quantity": "6",
        })
        bank_card_coupon = self.env["bank.card.coupon"].create({
            "number": "999",
            "bank_card_id": bank_card.id,
            "bank_card_fee_id": bank_card_fee.id,
            "amount": 90,
            "date": date.today(),
            "account_payment_id": payment.id
        })
        self._coupon = bank_card_coupon
        self._invoice = invoice
        self._payment = payment

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
