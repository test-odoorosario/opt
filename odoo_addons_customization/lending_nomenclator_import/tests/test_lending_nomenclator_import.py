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


class TestLendingNomenclatorImport(TransactionCase):


    def create_wizard(self):
        self.wizard = self.env['import.nomenclator.line.wizard'].create({
        })

    def create_array(self):
        self.array = [
            ['14', 'Categoria 1', '1', 'OG', '2', ''],
            ['01.23.05', 'Prestacion 1', '100000', 'OG', '201', '100'],
            ['02', 'Prestacion 2', '0', '', '0', '10']]

    def setUp(self):
        super(TestLendingNomenclatorImport, self).setUp()
        self.create_array()
        self.create_wizard()

    def test_first_row_without_code_or_description(self):
        array = [['', 'linea 1', 100000, 200, 100]]
        with self.assertRaises(ValidationError):
            self.wizard.create_lines(array)
        self.wizard.create_lines(self.array)

    def test_qty_lines(self):
        ids = self.wizard.create_lines(self.array)
        assert len(ids) == 3
        assert self.env['lending.nomenclator.line'].search([('id', '=', ids[2])]).lending_id.name == 'Prestacion 2'
        assert self.env['lending.nomenclator.line'].search([('id', '=', ids[2])]).amount_total == 10

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
