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


class TestLendingLot(TransactionCase):
    def create_affiliates(self):
        self.affiliate_taxed = self.env['lending.affiliate'].new({'taxed': True})
        self.affiliate_untaxed = self.env['lending.affiliate'].new({'taxed': False})

    def setUp(self):
        super(TestLendingLot, self).setUp()
        self.create_affiliates()

    def test_amounts(self):
        lot = self.env['lending.lot'].new({
            'registry_lending_ids': [
            (0, 0, {'affiliate_id': self.affiliate_taxed, 'informed_value': 500}),
            (0, 0, {'affiliate_id': self.affiliate_untaxed, 'informed_value': 400})
        ]})
        lot.compute_amount()
        assert lot.amount_untaxed == 400
        assert lot.amount_taxed == 500
        assert lot.amount_total == 900

    def test_pasar_a_estado_finalizado(self):
        lot = self.env['lending.lot'].new({
            'registry_lending_ids': [
                (0, 0, {'affiliate_id': self.affiliate_taxed, 'informed_value': 500}),
                (0, 0, {'affiliate_id': self.affiliate_untaxed, 'informed_value': 400})
            ],
            'revision_done': True,
        })
        lot.finish_lot()
        assert lot.state == 'done'

    def test_error_pasar_a_estado_finalizado(self):
        lot = self.env['lending.lot'].new({
            'registry_lending_ids': [
                (0, 0, {'affiliate_id': self.affiliate_taxed, 'informed_value': 500}),
                (0, 0, {'affiliate_id': self.affiliate_untaxed, 'informed_value': 400})
            ],
        })
        with self.assertRaises(ValidationError):
            lot.finish_lot()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
