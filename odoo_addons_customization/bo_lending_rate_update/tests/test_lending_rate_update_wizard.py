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
from datetime import datetime, timedelta


class TestLendingRateUpdateWizard(TransactionCase):
    def create_lender(self):
        self.lender = self.env['lending.lender'].create({
            'code': "TES",
            'name': "Test",
        })

    def create_customer(self):
        self.customer = self.env['lending.customer'].create({
            'code': "TES",
            'name': "Test",
        })

    def create_lendings(self):
        self.lending_one = self._create_lending("100000", "Ejemplo 1")
        self.lending_two = self._create_lending("120000", "Ejemplo 2")
        self.lending_three = self._create_lending("140000", "Ejemplo 3")

    def create_rate(self):
        self.rate = self.env['lending.rate'].create({
            'name': "Test",
            'date': datetime.now() - timedelta(days=7),
            'qty_expiration_days': 10,
            'lender_id': self.lender.id,
            'customer_id': self.customer.id,
        })

    def create_rate_lines(self):
        self._create_rate_line(self.lending_one, 150)
        self._create_rate_line(self.lending_two, 200)
        self._create_rate_line(self.lending_three, 400)

    def create_wizard(self):
        self.wizard = self.env['lending.rate.update.wizard'].with_context({'active_id': self.rate.id}).create({
            'name': "Nuevo tarifario",
            'global_percentage': 50,
        })

    def create_wizard_lines(self):
        self._create_wizard_line(self.lending_one, 10)
        self._create_wizard_line(self.lending_two, -5)

    def _create_lending(self, code, name):
        return self.env['lending'].create({
            'code': code,
            'name': name,
            'description': name,
        })

    def _create_rate_line(self, lending, value):
        self.env['lending.rate.line'].create({
            'lending_id': lending.id,
            'description': "Test",
            'rate_id': self.rate.id,
            'value': value,
        })

    def _create_wizard_line(self, lending, percentage):
        self.env['lending.rate.update.line.wizard'].create({
            'lending_id': lending.id,
            'variation_percentage': percentage,
            'wizard_id': self.wizard.id,
        })

    def setUp(self):
        super(TestLendingRateUpdateWizard, self).setUp()
        self.create_lender()
        self.create_customer()
        self.create_lendings()
        self.create_rate()
        self.create_rate_lines()
        self.create_wizard()
        self.create_wizard_lines()

    def test_create_new_rate(self):
        rate_id = self.wizard.create_rate().get('res_id')
        rate = self.env['lending.rate'].browse(rate_id)
        assert len(rate.line_ids) == 3
        assert rate.name == "Nuevo tarifario"
        assert rate.line_ids.filtered(lambda l: l.lending_id == self.lending_one).value == 165
        assert rate.line_ids.filtered(lambda l: l.lending_id == self.lending_two).value == 190
        assert rate.line_ids.filtered(lambda l: l.lending_id == self.lending_three).value == 600

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
