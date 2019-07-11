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


class TestLendingLender(TransactionCase):
    def create_lender(self):
        self.lender = self.env['lending'].create({
            'code': "111111",
            'name': "Ejemplo",
        })

    def setUp(self):
        super(TestLendingLender, self).setUp()
        self.create_lender()

    def test_name_get(self):
        assert self.lender.name_get()[0][1] == "[111111] Ejemplo"

    def test_name_search(self):
        assert self.lender.name_search("111111")[0][0] == self.lender.id
        assert self.lender.name_search("Ejemplo")[0][0] == self.lender.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
