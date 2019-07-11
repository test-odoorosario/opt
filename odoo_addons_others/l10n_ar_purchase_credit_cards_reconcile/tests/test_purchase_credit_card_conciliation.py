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

from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tests import common
from odoo import fields
from odoo.exceptions import ValidationError


class TestPurchaseCreditCardConciliation(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseCreditCardConciliation, self).setUp()
        self.credit_card = self.env['credit.card'].create({
            'name': 'Test',
            'account_id': self.env.ref('l10n_ar.1_caja_pesos').id
        })
        self.conciliation = self.env['purchase.credit.card.conciliation'].create({
            'name': 'Test',
            'date': fields.Date.today(),
            'date_from': fields.Date.today(),
            'date_to': fields.Date.today(),
            'journal_id': self.env.ref('l10n_ar_account_payment.journal_cobros_y_pagos').id,
            'credit_card_id': self.credit_card.id,

        })

    def test_dates_constraint(self):
        with self.assertRaises(ValidationError):
            self.conciliation.date_to = date.today() - relativedelta(days=1)

    def test_post_without_fees(self):
        with self.assertRaises(ValidationError):
            self.conciliation.post()

    def test_post(self):
        self.conciliation.fee_ids = [(6, 0, [self.env['purchase.credit.card.fee'].create({
            'credit_card_id': self.credit_card.id
        }).id])]
        self.conciliation.post()
        assert self.conciliation.state == 'reconciled'
        assert self.conciliation.move_id

    def test_cancel(self):
        self.conciliation.cancel()
        assert self.conciliation.state == 'canceled'

    def test_cancel_to_draft(self):
        self.conciliation.cancel()
        self.conciliation.cancel_to_draft()
        assert self.conciliation.state == 'draft'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
