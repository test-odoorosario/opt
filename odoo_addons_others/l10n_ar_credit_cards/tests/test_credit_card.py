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
from psycopg2._psycopg import IntegrityError


class TestCreditCard(common.TransactionCase):

    def setUp(self):
        super(TestCreditCard, self).setUp()

    def test_unique_credit_card(self):
        card_proxy = self.env['credit.card']
        vals = {'name': 'Test credit card', 'account_id': self.env.ref('l10n_ar.1_caja_pesos').id}
        card_proxy.create(vals)
        with self.assertRaises(IntegrityError):
            card_proxy.create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
