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
from datetime import date
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import pytest


@pytest.mark.skip(reason="Depende de enterprise")
class TestProjectReport(TransactionCase):
    def create_wizard(self):
        """Creacion de wizard de reporte"""
        return self.env['project.report.wizard'].create({
            'date_from': date.today(),
            'date_to': date.today() + relativedelta(months=4)
        })

    def create_product(self):
        self.product_1 = self.env['product.product'].create({
            'name': 'Product1'
        })

    def create_partner(self):
        self.partner = self.env['res.partner'].create({
            'name': 'partner'
        })

    def create_pricelist(self):
        self.pricelist = self.env['product.pricelist'].create({
            'name': 'Lista de precios',
            'currency_id': self.env.ref('base.ARS').id,
        })

    def create_sale_order(self):
        self.create_partner()
        self.create_pricelist()
        return self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'pricelist_id': self.pricelist.id,
        })

    def create_sale_line(self, sale):
        self.create_product()
        return self.env['sale.order.line'].create({
            'product_id': self.product_1.id,
            'name': 'PRODUCTO1',
            'product_uom_qty': 2,
            'product_uom': self.product_1.uom_id.id,
            'price_unit': 100,
            'order_id': sale.id,
            'admission_date': date.today() + relativedelta(months=10)
        })

    def create_subscription(self):
        self.create_partner()
        self.create_pricelist()
        return self.env['sale.subscription'].create({
            'partner_id': self.partner.id,
            'pricelist_id': self.pricelist.id,
            'template_id': self.env['sale.subscription.template'].create({'name': 'Plantilla'}).id
        })

    def create_subscription_line(self, subscription):
        self.create_product()
        return self.env['sale.subscription.line'].create({
            'product_id': self.product_1.id,
            'name': self.product_1.name,
            'price_unit': 1200,
            'actual_quantity': 2,
            'sold_quantity': 2,
            'uom_id': self.product_1.uom_id.id,
            'analytic_account_id': subscription.id
        })

    def setUp(self):
        super(TestProjectReport, self).setUp()

    def test_check_date(self):
        """Validamos el rango de fechas"""
        with self.assertRaises(ValidationError):
            self.env['project.report.wizard'].create({
                'date_from': date.today(),
                'date_to': date.today() - relativedelta(months=1)
            })
        self.create_wizard()

    def test_search_periods(self):
        """Chequeo que traiga correctamente la cantidad de periodos entre las fechas"""
        wizard = self.create_wizard()
        periods = wizard.search_periods()
        assert len(periods) == 5
        assert periods[0][0].strftime('%d/%m/%Y') == \
            date.today().strftime('%d/%m/%Y')
        assert periods[0][1].strftime('%d/%m/%Y') == \
            (date.today() + relativedelta(day=1) + relativedelta(months=1) - relativedelta(days=1)).strftime(
                   '%d/%m/%Y')

    def test_search_sale_lines(self):
        """Chequeo la busqueda de lineas de OV"""
        sale = self.create_sale_order()
        self.create_sale_line(sale)
        sale.action_confirm()
        wizard = self.create_wizard()
        periods = wizard.search_periods()
        assert not wizard.search_sale_lines(periods[0])
        line_2 = self.create_sale_line(sale)
        line_2.update({'admission_date': date.today() + relativedelta(months=1)})
        assert len(wizard.search_sale_lines(periods[1])) == 1

    def test_search_contract(self):
        """Chequeo la busqueda de subscripciones"""
        wizard = self.create_wizard()
        periods = wizard.search_periods()
        subscription = self.create_subscription()
        self.create_subscription_line(subscription)
        assert not wizard.search_contracts(periods[0])
        subscription.set_open()
        assert len(wizard.search_contracts(periods[0])) == 1

    def test_get_report_items(self):
        """Verifico que se creem los items correspondientes"""
        wizard = self.create_wizard()
        periods = wizard.search_periods()

        sale = self.create_sale_order()
        self.create_sale_line(sale)
        sale.action_confirm()
        assert not wizard.search_sale_lines(periods[0])
        line_2 = self.create_sale_line(sale)
        line_2.update({'admission_date': date.today() + relativedelta(months=1)})
        assert len(wizard.search_sale_lines(periods[1])) == 1

        subscription = self.create_subscription()
        self.create_subscription_line(subscription)
        assert not wizard.search_contracts(periods[0])
        subscription.set_open()
        assert len(wizard.search_contracts(periods[0])) == 1

        assert len(wizard._get_report_items(periods[0], 1)) == 1
        assert len(wizard._get_report_items(periods[1], 2)) == 2

        subscription2 = self.create_subscription()
        self.create_subscription_line(subscription2)
        subscription2.set_open()

        assert len(wizard._get_report_items(periods[1], 1)) == 3

    def test_generate_report_xls(self):
        """Verifico que se generere el reporte"""
        wizard = self.create_wizard()

        sale = self.create_sale_order()
        self.create_sale_line(sale)
        line_2 = self.create_sale_line(sale)
        line_2.update({'admission_date': date.today() + relativedelta(months=1)})
        sale.action_confirm()

        wizard.generate_report_xls()

        subscription = self.create_subscription()
        self.create_subscription_line(subscription)
        subscription.set_open()

        subscription2 = self.create_subscription()
        self.create_subscription_line(subscription2)
        subscription2.set_open()

        wizard.generate_report_xls()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
