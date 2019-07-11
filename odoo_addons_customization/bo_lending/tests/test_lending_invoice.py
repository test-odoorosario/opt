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
from openerp.exceptions import ValidationError
from datetime import datetime, timedelta


class TestLendingLot(TransactionCase):
    def setUp(self):
        super(TestLendingLot, self).setUp()

    def test_check_dates(self):
        invoice = self.env['lending.invoice'].new({
            'entry_date': datetime.now() + timedelta(days=1),
            'due_date': datetime.now()
        })
        with self.assertRaises(ValidationError):
            invoice.check_dates()

    def test_due_date(self):
        customer = self.env['lending.customer'].create({
            'name': 'Cliente',
            'code': '1'
        })
        lender = self.env['lending.lender'].create({
            'name': 'Prestador',
            'code': '1.1'
        })
        self.env['lending.rate'].create({
            'name': 'Tarifario',
            'customer_id': customer.id,
            'lender_id': lender.id,
            'qty_expiration_days': 10,
            'qty_liquidation_days': 10,
        })
        invoice = self.env['lending.invoice'].create({
            'name': "Factura",
            'lender_id': lender.id,
            'customer_id': customer.id,
            'entry_date': datetime.now(),
            'due_date': datetime.now(),
        })
        invoice.onchange_entry_date()
        invoice.due_date = datetime.now() + timedelta(days=10)

    def test_check_amounts_negative(self):
        invoice = self.env['lending.invoice'].new({'amount_untaxed': -1})
        with self.assertRaises(ValidationError):
            invoice.check_amounts()

    def test_check_amounts_all_zero(self):
        invoice = self.env['lending.invoice'].new({})
        with self.assertRaises(ValidationError):
            invoice.check_amounts()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
