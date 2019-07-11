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
from datetime import datetime


class TestImportLotLinesWizard(TransactionCase):

    def get_excel_date(self):
        temp = datetime(1899, 12, 30)
        delta = datetime.now() - temp
        self.date = float(delta.days) + (float(delta.seconds) / 86400)

    def create_array(self):
        self.array = [
            ["DNI", "00000000", "Juan Perez", 999999.0, "1", "Consulta", self.date, 250, 0, 250],
            ["CUIT", "20000000011", "Juan Perez", 999998.0, "1", "Consulta 2", self.date, 400, 0, 400],
        ]

    def create_lender(self):
        self.lender = self.env['lending.lender'].create({
            'code': "000",
            'name': "Prestador",
        })

    def create_lot_type(self):
        self.type = self.env['lending.lot.type'].create({
            'name': "Tipo",
        })

    def create_lot(self):
        self.lot = self.env['lending.lot'].create({
            'name': "Lote",
            'lender_id': self.lender.id,
            'lending_lot_type_id': self.type.id,
        })

    def create_wizard(self):
        self.wizard = self.env['import.lot.lines.wizard'].with_context({'active_id': self.lot.id}).create({})

    def setUp(self):
        super(TestImportLotLinesWizard, self).setUp()
        self.get_excel_date()
        self.create_array()
        self.create_lender()
        self.create_lot_type()
        self.create_lot()
        self.create_wizard()

    def test_no_practice(self):
        self.array[0][self.wizard.COLS['practice']] = False
        with self.assertRaises(ValidationError):
            self.wizard.create_lines(self.array, 0)

    def test_no_document_type(self):
        self.array[0][self.wizard.COLS['affiliate_doc_type']] = False
        with self.assertRaises(ValidationError):
            self.wizard.create_lines(self.array, 0)

    def test_invalid_document_type(self):
        self.array[0][self.wizard.COLS['affiliate_doc_type']] = "AAA"
        with self.assertRaises(ValidationError):
            self.wizard.create_lines(self.array, 0)

    def test_no_vat(self):
        self.array[0][self.wizard.COLS['affiliate_vat']] = False
        with self.assertRaises(ValidationError):
            self.wizard.create_lines(self.array, 0)

    def test_affiliates_created(self):
        assert not self.env['lending.affiliate'].search([('vat', 'in', ['00000000', '20000000011'])])
        self.wizard.create_lines(self.array, 0)
        assert len(self.env['lending.affiliate'].search([('vat', 'in', ['00000000', '20000000011'])])) == 2

    def test_qty_lines(self):
        ids = self.wizard.create_lines(self.array, 0)
        assert len(ids) == 2

    def test_total_amount(self):
        self.wizard.create_lines(self.array, 0)
        assert self.lot.amount_total == 650

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
