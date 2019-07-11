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


class RetentionRetentionRuleTest(TransactionCase):
    # ---
    # AUX
    # ---
    def find_retentions(self):
        self.profit_retention = self.env['retention.retention'].search([('type', '=', 'profit')], limit=1)
        self.non_profit_retention = self.env['retention.retention'].search([('type', '!=', 'profit')], limit=1)

    def find_activity(self):
        self.activity = self.env['retention.activity'].search([], limit=1)

    # -----
    # SETUP
    # -----
    def setUp(self):
        super(RetentionRetentionRuleTest, self).setUp()
        self.find_retentions()
        self.find_activity()
        self.profit_retention.retention_rule_ids.unlink()
        self.non_profit_retention.retention_rule_ids.unlink()

    # -----
    # TESTS
    # -----
    def test_activity_profit_retention(self):
        with self.assertRaises(ValidationError):
            self.env['retention.retention.rule'].create({
                'retention_id': self.profit_retention.id,
                'not_applicable_minimum': 0,
                'minimum_tax': 0,
                'percentage': 0,
            })

    def test_activity_non_profit_retention(self):
        with self.assertRaises(ValidationError):
            self.env['retention.retention.rule'].create({
                'retention_id': self.non_profit_retention.id,
                'activity_id': self.activity.id,
                'not_applicable_minimum': 0,
                'minimum_tax': 0,
                'percentage': 0,
            })

    def test_repeated_line(self):
        self.env['retention.retention.rule'].create({
            'retention_id': self.profit_retention.id,
            'activity_id': self.activity.id,
            'not_applicable_minimum': 0,
            'minimum_tax': 0,
            'percentage': 0,
        })
        with self.assertRaises(ValidationError):
            self.env['retention.retention.rule'].create({
                'retention_id': self.profit_retention.id,
                'activity_id': self.activity.id,
                'not_applicable_minimum': 0,
                'minimum_tax': 0,
                'percentage': 0,
            })

    def test_negative_not_applicable_minimum(self):
        with self.assertRaises(ValidationError):
            self.env['retention.retention.rule'].create({
                'retention_id': self.profit_retention.id,
                'activity_id': self.activity.id,
                'not_applicable_minimum': -1,
                'minimum_tax': 0,
                'percentage': 0,
            })

    def test_negative_minimum_tax(self):
        with self.assertRaises(ValidationError):
            self.env['retention.retention.rule'].create({
                'retention_id': self.profit_retention.id,
                'activity_id': self.activity.id,
                'not_applicable_minimum': 0,
                'minimum_tax': -1,
                'percentage': 0,
            })

    def test_negative_percentage(self):
        with self.assertRaises(ValidationError):
            self.env['retention.retention.rule'].create({
                'retention_id': self.profit_retention.id,
                'activity_id': self.activity.id,
                'not_applicable_minimum': 0,
                'minimum_tax': 0,
                'percentage': -1,
            })

    def test_greater_than_100_percentage(self):
        with self.assertRaises(ValidationError):
            self.env['retention.retention.rule'].create({
                'retention_id': self.profit_retention.id,
                'activity_id': self.activity.id,
                'not_applicable_minimum': 0,
                'minimum_tax': 0,
                'percentage': 101,
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
