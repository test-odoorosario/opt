# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class ResPartnerTest(TransactionCase):
    # ---
    # AUX
    # ---
    def find_retention(self):
        self.retention = self.env['retention.retention'].search(
            [('type', '=', 'gross_income'), ('type_tax_use', '=', 'purchase')], limit=1)

    def create_partner(self):
        self.partner = self.env['res.partner'].create({
            'name': "Partner",
        })

    # -----
    # SETUP
    # -----
    def setUp(self):
        super(ResPartnerTest, self).setUp()
        self.find_retention()
        self.create_partner()
        self.partner.retention_partner_rule_ids.unlink()

    # -----
    # TESTS
    # -----
    def test_delete_lines_onchange_supplier_parent_id(self):
        self.env['retention.partner.rule'].create({
            'partner_id': self.partner.id,
            'retention_id': self.retention.id,
            'percentage': 0,
        })
        self.partner.onchange_supplier_parent_id()
        assert not self.partner.retention_partner_rule_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
