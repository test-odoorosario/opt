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


class TestImportKairos(TransactionCase):
    
    def setUp(self):
        super(TestImportKairos, self).setUp()

    def test_onchange_medicine(self):
        lending = self.env['lending'].create({
            'code': '1231231',
            'name': 'Test',
            'medicine': True,
            'description_drug': 'Droga'
        })
        lending.medicine = False
        lending.onchange_medicine()
        assert not lending.description_drug

    def test_search_medicine(self):
        wizard = self.env['lending.import.kairos.wizard'].create({
            'file': '..'
        })
        self.env['lending'].create({
            'code': 'M12312',
            'name': 'Test',
            'description_product': "MEDICAMENTO",
            'description_presentation': "PRESENTACION",
            'description_laboratory': "LABORATORIO",
            'description_drug': "DROGA",
        })
        line = ('MEDICAMENTO', 'PRESENTACION', '123.2', 1231, 2, '2013-11-28 00:00:00', 'LABORATORIO', 'DROGA')
        assert wizard.search_medicine(line)

    def test_create_medicine(self):
        wizard = self.env['lending.import.kairos.wizard'].create({
            'file': '..'
        })
        line = ('MEDICAMENTO', 'PRESENTACION', '123.2', 1231, 2, '2013-11-28 00:00:00', 'LABORATORIO', 'DROGA')
        wizard.create_medicine(line)
        assert len(wizard.search_medicine(line)) == 1

    def test_create_and_search_kairos_line(self):
        wizard = self.env['lending.import.kairos.wizard'].create({
            'file': '..'
        })
        line = ('MEDICAMENTO', 'PRESENTACION', '123.2', 1231, 2, '2013-11-28 00:00:00', 'LABORATORIO', 'DROGA')
        wizard.create_medicine(line)
        lending = wizard.search_medicine(line)
        wizard.create_kairos_line(line, lending)
        assert len(wizard.search_kairos_line(lending)) == 1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
