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
from openerp.exceptions import UserError


class TestThirdCheckImportWizard(TransactionCase):

    def find_bank_bic(self):
        self.bank_bic = self.env['res.bank'].search([('bic', '!=', False)], limit=1).bic

    def create_array(self):
        self.array = [
            ['015', 15000, 15000, 'Comun', self.bank_bic, '15000.50'],
            ['018', 15000, 16000, 'Diferido', self.bank_bic, '25000'],
        ]

    def create_wizard(self):
        self.wizard = self.env['third.check.import.wizard'].new()

    def setUp(self):
        super(TestThirdCheckImportWizard, self).setUp()
        self.datemode = 0
        self.find_bank_bic()
        self.create_array()
        self.create_wizard()

    def test_correct_import(self):
        assert len(self.wizard.create_checks(self.array, self.datemode)) == len(self.array)

    def test_empty_name(self):
        self.array[0][0] = False
        with self.assertRaises(UserError):
            self.wizard.create_checks(self.array, self.datemode)

    def test_empty_issue_date(self):
        self.array[0][1] = False
        with self.assertRaises(UserError):
            self.wizard.create_checks(self.array, self.datemode)

    def test_invalid_issue_date(self):
        self.array[0][1] = 'Sarasa'
        with self.assertRaises(UserError):
            self.wizard.create_checks(self.array, self.datemode)

    def test_empty_payment_date(self):
        self.array[0][2] = False
        with self.assertRaises(UserError):
            self.wizard.create_checks(self.array, self.datemode)

    def test_invalid_payment_date(self):
        self.array[0][2] = 'Sarasa'
        with self.assertRaises(UserError):
            self.wizard.create_checks(self.array, self.datemode)

    def test_empty_payment_type(self):
        self.array[0][3] = False
        with self.assertRaises(UserError):
            self.wizard.create_checks(self.array, self.datemode)

    def test_invalid_payment_type(self):
        self.array[0][3] = 'Sarasa'
        with self.assertRaises(UserError):
            self.wizard.create_checks(self.array, self.datemode)

    def test_empty_bank(self):
        self.array[0][4] = False
        with self.assertRaises(UserError):
            self.wizard.create_checks(self.array, self.datemode)

    def test_invalid_bank(self):
        self.array[0][4] = 'Sarasa'
        with self.assertRaises(UserError):
            self.wizard.create_checks(self.array, self.datemode)

    def test_invalid_amount(self):
        self.array[0][5] = 'Sarasa'
        with self.assertRaises(UserError):
            self.wizard.create_checks(self.array, self.datemode)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
