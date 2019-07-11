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
from datetime import date


class TestAccountOwnCheck(TransactionCase):
    def create_move(self):
        self.move = self.env['account.move'].create({
            'journal_id': self.env.ref('l10n_ar_account_payment.journal_cobros_y_pagos').id,
            'state': 'draft',
            'ref': 'Asiento',
        })

    def create_check(self):
        bank = self.env['res.bank'].create({
            'name': "Banco ejemplo",
        })
        journal = self.env.ref('l10n_ar_account_payment.journal_cobros_y_pagos')
        journal.bank_id = bank.id

        checkbook = self.env['account.checkbook'].create({
            'name': 'Chequera',
            'payment_type': 'postdated',
            'journal_id': journal.id,
            'number_from': '1',
            'number_to': '10',
        })
        self.check = self.env['account.own.check'].create({
            'bank_id': bank.id,
            'checkbook_id': checkbook.id,
            'name': "123456",
            'payment_type': 'common',
            'collect_move_id': self.move.id,
            'collect_date': date.today(),
            'state': 'collect',
        })

    def setUp(self):
        super(TestAccountOwnCheck, self).setUp()
        self.create_move()
        self.create_check()

    def test_reconcile(self):
        self.check.reconcile_check({})
        assert self.check.state == 'reconciled'

    def test_reconcile_invalid_state(self):
        self.check.state = 'draft'
        with self.assertRaises(ValidationError):
            self.check.reconcile_check({})

    def test_cancel_reconcile(self):
        self.check.reconcile_check({})
        self.check.cancel_reconcile()
        assert self.check.state == 'collect'

    def test_cancel_reconcile_error(self):
        self.check.reconcile_check({})
        self.check.collect_move_id = None
        with self.assertRaises(ValidationError):
            self.check.cancel_reconcile()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
