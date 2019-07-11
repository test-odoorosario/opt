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

import test_retention_retention
from openerp.exceptions import ValidationError


class TestGrossIncomeRetentionCalc(test_retention_retention.TestRetentionRetention):

    def setUp(self):
        super(TestGrossIncomeRetentionCalc, self).setUp()
        self.partner_rule = self.env['retention.partner.rule'].create({
            'retention_id': self.env.ref('l10n_ar_retentions.retention_retention_iibb_pba_efectuada').id,
            'percentage': 5,
            'partner_id': self.partner.id
        })

    def test_retention_without_gross_income_in_partner(self):
        retention = self.env.ref('l10n_ar_retentions.retention_retention_iibb_pba_efectuada')
        self.partner_rule.unlink()
        assert retention.calculate_gross_income_retention(self.partner, 10000)[0] == 10000
        assert not retention.calculate_gross_income_retention(self.partner, 10000)[1]

    def test_retention_with_gross_income_in_partner(self):
        retention = self.env.ref('l10n_ar_retentions.retention_retention_iibb_pba_efectuada')
        assert retention.calculate_gross_income_retention(self.partner, 10000)[0] == 10000
        assert retention.calculate_gross_income_retention(self.partner, 10000)[1] == 500

    def test_retention_without_configuration(self):
        retention = self.env.ref('l10n_ar_retentions.retention_retention_iibb_pba_efectuada')
        self.partner_rule.unlink()
        self.env['retention.retention.rule'].search([('retention_id', '=', retention.id)]).unlink()
        with self.assertRaises(ValidationError):
            retention.calculate_gross_income_retention(self.partner, 1000)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
