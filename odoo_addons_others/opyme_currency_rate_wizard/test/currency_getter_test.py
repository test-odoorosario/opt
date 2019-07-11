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

from odoo.tests.common import TransactionCase
from ..rate_getters import rate_getter_yahoo


class CurrencyGetterTest(TransactionCase):
    def create_currency(self):
        return self.env['res.currency'].create({
            'name':'TEST',
            'symbol':'TEST'
        })

    def create_currency_rate(self, currency):
        return self.env['res.currency.rate'].create({
            'name': '2017-10-19 00:00:00',
            'rate': 0.6541,
            'inverse_rate': 17.564,
            'currency_id': currency.id
        })

    def create_wizard(self, local, dest):
        return self.env['currency.rate.wizard'].create({
            'local_currency': local.id,
            'currency': dest.id,
            'service': 'yahoo',
        })

    def setUp(self):
        super(CurrencyGetterTest, self).setUp()
        self.rate_getter = rate_getter_yahoo.RateGetterYahoo()
        self.USD = self.env.ref('base.USD')
        self.ARS = self.env.ref('base.ARS')

    def test_get_inverse_rate(self):
        "Testeamos que el compute traiga bien la currency"
        currency = self.create_currency()
        assert currency.inverse_rate == 0

        rate = self.create_currency_rate(currency)
        currency._get_inverse_rate()
        assert currency.inverse_rate == rate.inverse_rate

    # TODO: Cuando se solucione el problema de yahoo hay que descomentar estos tests
    # def test_get_rate_getter(self):
    #     "Testeamos que el rate getter trae las currencys"
    #     assert self.rate_getter.get_rate('ARS', 'USD')
    #     assert self.rate_getter.get_rate('ARS', 'EUR')
    #     assert self.rate_getter.get_rate('USD', 'ARS')
    #     assert self.rate_getter.get_rate('EUR', 'ARS')
    #     assert not self.rate_getter.get_rate('EUR', 'PES')
    #     assert not self.rate_getter.get_rate('ARS', 'afsdf')
    #
    # def test_get_rate(self):
    #     "Testeamos que se crea el rate nuevo con la currency obtenida del servidor"
    #     assert not self.env['res.currency.rate'].search([('currency_id', '=', self.USD.id)])
    #
    #     wizard = self.create_wizard(self.ARS, self.USD)
    #     wizard.get_rate()
    #
    #     assert self.env['res.currency.rate'].search([('currency_id', '=', self.USD.id)])

    def test_instantiate_get_rate(self):
        "Testeamos que instancia el rate getter"
        wizard = self.create_wizard(self.ARS, self.USD)
        assert wizard.instantiate_rate_getter().__class__.__name__ == 'RateGetterYahoo'

    def test_get_local_currency(self):
        "Testeamos que trae la currency local"
        wizard = self.create_wizard(self.ARS, self.USD)
        assert wizard._get_local_currency() == self.env.user.company_id.currency_id.id


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

