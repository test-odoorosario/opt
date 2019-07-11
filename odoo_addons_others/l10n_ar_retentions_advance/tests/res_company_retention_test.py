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


class ResCompanyRetentionTest(TransactionCase):
    # ---
    # AUX
    # ---
    def find_retention(self):
        self.retention = self.env['retention.retention'].search([], limit=1)

    def find_company(self):
        self.company = self.env['res.company'].search([], limit=1)

    # -----
    # SETUP
    # -----
    def setUp(self):
        super(ResCompanyRetentionTest, self).setUp()
        self.find_retention()
        self.find_company()
        self.company.retention_ids.unlink()

    # -----
    # TESTS
    # -----
    def test_repeated_line(self):
        self.env['res.company.retention'].create({
            'company_id': self.company.id,
            'retention_id': self.retention.id,
        })
        with self.assertRaises(ValidationError):
            self.env['res.company.retention'].create({
                'company_id': self.company.id,
                'retention_id': self.retention.id,
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
