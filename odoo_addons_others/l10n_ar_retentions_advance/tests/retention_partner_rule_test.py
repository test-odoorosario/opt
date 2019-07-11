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

from odoo.exceptions import ValidationError


class RetentionPartnerRuleTest(TransactionCase):
    # ---
    # AUX
    # ---
    def find_retentions(self):
        self.profit_retention = self.env['retention.retention'].search([('type', '=', 'profit')], limit=1)
        self.non_profit_retention = self.env['retention.retention'].search([('type', '!=', 'profit')], limit=1)

    def find_activity(self):
        self.activity = self.env['retention.activity'].search([], limit=1)

    def create_partner(self):
        self.partner = self.env['res.partner'].create({
            'name': "Partner",
        })

    # -----
    # SETUP
    # -----
    def setUp(self):
        super(RetentionPartnerRuleTest, self).setUp()
        self.find_retentions()
        self.find_activity()
        self.create_partner()
        self.partner.retention_partner_rule_ids.unlink()

    # -----
    # TESTS
    # -----

    def test_percentage_profit_retention(self):
        with self.assertRaises(ValidationError):
            self.env['retention.partner.rule'].create({
                'partner_id': self.partner.id,
                'retention_id': self.profit_retention.id,
                'activity_id': self.activity.id,
                'percentage': 10,
            })

    def test_repeated_rule(self):
        self.env['retention.partner.rule'].create({
            'partner_id': self.partner.id,
            'retention_id': self.profit_retention.id,
            'activity_id': self.activity.id,
            'percentage': 0,
        })
        with self.assertRaises(ValidationError):
            self.env['retention.partner.rule'].create({
                'partner_id': self.partner.id,
                'retention_id': self.profit_retention.id,
                'activity_id': self.activity.id,
                'percentage': 10,
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
