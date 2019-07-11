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

from mock import mock
from . import test_retention_retention

accumulated_amount = 'odoo.addons.l10n_ar_automatic_retentions.models.payment.AccountPayment.get_accumulated_amount'


class TestProfitRetentionCalc(test_retention_retention.TestRetentionRetention):

    def test_accumulated_equal_than_minimum(self):
        retention = self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada')
        with mock.patch(accumulated_amount) as accumulated_amount_patch:
            accumulated_amount_patch.return_value = 100000
            assert retention.calculate_profit_retention(self.partner, 5000)[1] == 100

    def test_accumulated_lower_than_minimum(self):
        retention = self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada')
        with mock.patch(accumulated_amount) as accumulated_amount_patch:
            accumulated_amount_patch.return_value = 50000
            assert retention.calculate_profit_retention(self.partner, 100000)[1] == 1000

    def test_accumulated_first_retention_with_surpassed_minimum(self):
        retention = self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada')
        with mock.patch(accumulated_amount) as accumulated_amount_patch:
            accumulated_amount_patch.return_value = 101000
            assert retention.calculate_profit_retention(self.partner, 9000)[1] == 200

    def test_no_activity_percentage(self):
        retention = self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada')
        retention_rule = retention.get_profit_retention_rule(self.partner)
        retention_rule.percentage = 0
        with mock.patch(accumulated_amount) as accumulated_amount_patch:
            accumulated_amount_patch.return_value = 100000
            assert not retention.calculate_profit_retention(self.partner, 100000)[1]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
