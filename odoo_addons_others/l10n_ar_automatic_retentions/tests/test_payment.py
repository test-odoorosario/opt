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


class TestPayment(common.TransactionCase):

    def setUp(self):
        super(TestPayment, self).setUp()
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
        self.payment = self.env['account.payment'].new({'amount': 500, 'partner_id': self.partner.id})

    def test_amount_to_tax_only_advance(self):
        self.payment.advance_amount = 500
        assert self.payment.get_amount_to_tax() == 500

    def test_amount_all_taxed(self):
        invoice = self.env['account.invoice'].new({
            'amount_total_signed': 500,
            'amount_to_tax': 413.22
        })
        self.payment.payment_imputation_ids = self.env['payment.imputation.line'].new({
            'payment_id': self.payment.id,
            'invoice_id': invoice,
            'amount': 500
        })
        assert self.payment.get_amount_to_tax() == 413.22

    def test_amount_untaxed(self):
        invoice = self.env['account.invoice'].new({
            'amount_total_signed': 500,
            'amount_to_tax': 0
        })
        self.payment.payment_imputation_ids = self.env['payment.imputation.line'].new({
            'payment_id': self.payment.id,
            'invoice_id': invoice,
            'amount': 500
        })
        assert not self.payment.get_amount_to_tax()

    def test_mixed_amount_with_advance(self):
        invoice = self.env['account.invoice'].new({
            'amount_total_signed': 1000,
            'amount_to_tax': 413.22
        })
        self.payment.payment_imputation_ids = self.env['payment.imputation.line'].new({
            'payment_id': self.payment.id,
            'invoice_id': invoice,
            'amount': 1000
        })
        self.payment.advance_amount = 100
        assert self.payment.get_amount_to_tax() == 513.22

    def test_retention_vals(self):
        profit_ret = self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada')
        self.payment._create_retention(10000, 200, profit_ret)
        retention_ids = self.payment.retention_ids
        assert retention_ids[0].base == 10000
        assert retention_ids[0].amount == 200
        assert retention_ids[0].retention_id == profit_ret
        assert retention_ids[0].name == profit_ret.name
        assert retention_ids[0].jurisdiction == profit_ret.jurisdiction
        activity = profit_ret.get_profit_retention_rule(self.partner).activity_id
        assert retention_ids[0].activity_id == activity

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
