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


class TestLendingAffiliate(TransactionCase):
    def create_affiliate(self):
        self.affiliate = self.env['lending.affiliate'].create({
            'name': "Ejemplo",
            'document_type': 'dni',
            'vat': "12345678",
        })

    def setUp(self):
        super(TestLendingAffiliate, self).setUp()
        self.create_affiliate()

    def test_name_search(self):
        assert self.affiliate.name_search("12345678")[0][0] == self.affiliate.id
        assert self.affiliate.name_search("Ejemplo")[0][0] == self.affiliate.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
