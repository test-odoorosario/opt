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

from openerp.exceptions import ValidationError
from datetime import date
from odoo.tests import common


class TestRetentionRetention(common.TransactionCase):

    def _create_payment(self):
        return self.env['account.payment'].create({
            'partner_id': self.partner.id, 'payment_date': date.today(), 'state': 'posted',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'payment_type': 'outbound', 'amount': 1500
        })

    def setUp(self):
        super(TestRetentionRetention, self).setUp()
        activity = self.env['retention.activity'].create({'name': 'test', 'code': 1})
        retention_partner_rule = self.env['retention.partner.rule'].create({
            'retention_id': self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada').id,
            'activity_id': activity.id,
            'percentage': 0
        })
        self.env['retention.retention.rule'].create({
            'retention_id': self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada').id,
            'activity_id': activity.id,
            'percentage': 2,
            'minimum_tax': 90,
            'exclude_minimum': True,
            'not_applicable_minimum': 100000
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test',
            'property_account_position_id': self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari').id,
            'retention_partner_rule_ids': [(6, 0, [retention_partner_rule.id])],
        })

    def test_valid_retention_configuration(self):
        retention = self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada')
        retention.get_profit_retention_rule(self.partner)

    def test_partner_no_retention(self):
        retention = self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada')
        self.partner.retention_partner_rule_ids = None
        with self.assertRaises(ValidationError):
            retention.calculate_profit_retention(self.partner, 10)

    def test_no_retention_rule(self):
        retention = self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada')
        retention.retention_rule_ids = None
        with self.assertRaises(ValidationError):
            retention.calculate_profit_retention(self.partner, 10)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
