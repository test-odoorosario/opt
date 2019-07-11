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
from openerp.exceptions import ValidationError


class TestLendingLot(TransactionCase):
    def create_lender(self):
        self.lender = self.env['lending.lender'].create({
            'code': "Prestador",
            'name': "Prestador",
        })

    def create_affiliate(self):
        self.affiliate = self.env['lending.affiliate'].create({
            'name': "Afiliado",
            'document_type': 'dni',
            'vat': "1234",
        })

    def create_lot_type(self):
        self.type = self.env['lending.lot.type'].create({
            'name': "Tipo de lote",
        })

    def create_lot(self):
        self.lot = self.env['lending.lot'].create({
            'name': "Lote",
            'lender_id': self.lender.id,
            'lending_lot_type_id': self.type.id,
        })

    def create_registry_lending(self):
        self.registry = self.env['lending.registry.lending'].create({
            'code': "Registro",
            'description': "Registro",
            'lot_id': self.lot.id,
            'affiliate_id': self.affiliate.id,
        })

    def setUp(self):
        super(TestLendingLot, self).setUp()
        self.create_lender()
        self.create_affiliate()
        self.create_lot_type()
        self.create_lot()
        self.create_registry_lending()

    def test_error_if_no_debit(self):
        with self.assertRaises(ValidationError):
            self.lot.debit_report()

    def test_file_generated_if_debit(self):
        self.registry.debit = 1
        self.lot.debit_report()
        assert self.lot.file

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
