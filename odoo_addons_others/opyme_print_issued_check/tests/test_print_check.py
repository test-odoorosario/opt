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

from odoo.tests import common
from num2words import num2words


class TestPrintCheck(common.TransactionCase):

    def setUp(self):
        super(TestPrintCheck, self).setUp()

    def _create_check(self):
        return self.env['account.own.check'].new({
            'issue_date': '2000-01-01',
            'amount': 1000.50,
            'payment_type': 'postdated',
            'payment_date': '2000-02-01',
            'destination_payment_id': self.env['account.payment'].new({
                'partner_id': self.env['res.partner'].new({'name': 'Test'})
            })
        })

    def test_build_check_dic(self):

        check = self._create_check()
        dic = self.env['print.check.configuration']._build_check_dic(check)
        assert dic['issue_date'] == check.issue_date
        assert dic['payment_date'] == check.payment_date
        assert dic['amount'] == check.amount
        assert dic['amount_text'] == "mil pesos con cincuenta centavos"
        assert dic['partner'] == 'Test'
        assert dic['postdated']

    def test_split_text(self):

        assert self.env['print.check.configuration'].split_text('TEXTO CORTO', 60) == ('TEXTO CORTO', '')
        assert self.env['print.check.configuration'].split_text(
            'TEXTO QUE SE CORTA PORQUE ES MUY LARGO', 25
        ) == ('TEXTO QUE SE CORTA', 'PORQUE ES MUY LARGO')

    def test_generate_raw_html(self):
        check = self._create_check()
        print_check = self.env['print.check.configuration'].new({
            'partner_characters': 60,
            'amount_characters': 60
        })
        print_check.get_raw_html(check)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

