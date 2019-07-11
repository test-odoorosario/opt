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
from openerp import fields
from dateutil.relativedelta import relativedelta
from datetime import datetime


class TestLendingLotValidations(TransactionCase):
    def create_lot_type(self):
        self.lot_type = self.env['lending.lot.type'].create({
            'name': "Tipo de lote",
        })

    def create_lender(self):
        self.lender = self.env['lending.lender'].create({
            'name': 'Prestador',
            'code': '1.1'
        })

    def create_lot(self):
        self.lot = self.env['lending.lot'].create({
            'lender_id': self.lender.id,
            'name': 'Lote',
            'lending_lot_type_id': self.lot_type.id,
        })

    def create_customer(self):
        self.customer = self.env['lending.customer'].create({
            'name': 'Cliente',
            'code': '1'
        })

    def create_affiliate(self):
        self.affiliate = self.env['lending.affiliate'].create({
            'name': 'Afiliado',
            'code': '01',
            'document_type': 'dni',
            'vat': '31323323',
        })

    def create_lending(self):
        self.lending = self.env['lending'].create({
            'code': '010101',
            'name': 'Prestacion 1',
        })
        self.lending_2 = self.env['lending'].create({
            'code': '020101',
            'name': 'Prestacion 2',
        })

    def create_nomenclator(self):
        self.nomenclator_nn = self.env['lending.nomenclator'].create({
            'name': 'NN'
        })
        self.nomenclator_nbu = self.env['lending.nomenclator'].create({
            'name': 'NBU'
        })
        self.env['lending.nomenclator.line'].create({
            'lending_id': self.lending.id,
            'code': '010101',
            'description': 'PRESTACION NUMERO NN 1',
            'nomenclator_id': self.nomenclator_nn.id,
            'unit': 10,
            'unit_expense': 2,
            'value': 5,
        })
        self.env['lending.nomenclator.line'].create({
            'lending_id': self.lending.id,
            'code': '010101',
            'description': 'PRESTACION NUMERO NBU 1',
            'nomenclator_id': self.nomenclator_nbu.id,
            'value': 5,
        })

    def create_rate(self):
        self.rate = self.env['lending.rate'].create({
            'name': 'Tarifario',
            'customer_id': self.customer.id,
            'lender_id': self.lender.id,
            'qty_expiration_days': 10,
        })
        self.rate_line = self.env['lending.rate.line'].create({
            'lending_id': self.lending.id,
            'nomenclator_id': self.nomenclator_nbu.id,
            'calculation_type': 'expense',
            'value': 10,
            'rate_id': self.rate.id,
            'description': 'PRESTACION 1'
        })
        self.env['lending.rate.line'].create({
            'lending_id': self.lending_2.id,
            'code_range': '030100',
            'value': 1000,
            'rate_id': self.rate.id,
            'description': 'PRESTACION 2'

        })

    def _create_registry(self, value, code, description):
        return self.env['lending.registry.lending'].with_context(mail_create_nosubscribe=True).create({
            'date': fields.Date.today(),
            'affiliate_id': self.affiliate.id,
            'informed_value': value,
            'lot_id': self.lot.id,
            'code': code,
            'description': description,
        })

    def setUp(self):
        super(TestLendingLotValidations, self).setUp()
        self.env['lending.rate'].search([]).unlink()
        self.create_lot_type()
        self.create_lender()
        self.create_lot()
        self.create_customer()
        self.create_affiliate()
        self.create_lending()
        self.create_nomenclator()
        self.create_rate()

    def test_calculation_amount(self):
        line_lending_1 = self._create_registry(150, "010101", "Ejemplo")
        line_lending_2 = self._create_registry(2000, "020200", "Ejemplo 2")
        assert line_lending_1.debit == 130
        assert line_lending_1.total_to_pay == 20
        assert line_lending_1.rate_value == 20
        assert line_lending_1.debit_motive_ids

        assert line_lending_2.debit == 1000
        assert line_lending_2.rate_value == 1000
        assert line_lending_2.debit_motive_ids

    def test_sum_total_to_pay(self):
        self._create_registry(150, "010101", "Ejemplo")
        self._create_registry(2000, "020200", "Ejemplo 2")
        assert self.lot.total_to_pay == 1020

    def test_validate_without_rate(self):
        self.rate.end_date = self.rate.date
        registry = self._create_registry(150, "123456", "Ejemplo")
        assert registry.observations == "Sin tarifario"

    def test_validate_registry_duplicity(self):
        self._create_registry(150, "010101", "Ejemplo")
        registry = self._create_registry(150, "010101", "Ejemplo")
        assert registry.observations == "Prestacion duplicada"

    def test_validate_affiliate_duplicity(self):
        self.affiliate.document_type = 'cuit'
        self.create_affiliate()
        registry = self._create_registry(150, "010101", "Ejemplo")
        assert registry.observations == "Afiliado duplicado"

    def test_validate_expiry(self):
        self.rate.qty_expiration_days = -1
        invoice = self.env['lending.invoice'].create({
            'name': "Factura",
            'lender_id': self.lender.id,
            'customer_id': self.customer.id,
        })
        self.lot.invoice_id = invoice
        registry = self._create_registry(150, "010101", "Ejemplo")
        assert registry.observations == "Vencido"

    def test_re_invoice(self):
        invoice = self.env['lending.invoice'].create({
            'name': "Factura 1",
            'lender_id': self.lender.id,
            'date': fields.Date.today(),
            'customer_id': self.customer.id,
        })
        self.lot.invoice_ids = [(4, invoice.id)]
        registry = self._create_registry(150, "010101", "Ejemplo1")
        registry.write({
            'debit_motive_ids': [(4, self.env.ref('bo_lending.debit_motive_agreement_affiliate').id)]
        })

        lot_2 = self.env['lending.lot'].create({
            'lender_id': self.lender.id,
            'name': 'Lote',
            'lending_lot_type_id': self.lot_type.id,
        })
        registry_2 = self.env['lending.registry.lending'].with_context(mail_create_nosubscribe=True).create({
            'date': fields.Date.today(),
            'affiliate_id': self.affiliate.id,
            're_invoice_id': invoice.id,
            'informed_value': 10,
            'lot_id': lot_2.id,
            'code': '010101',
            'description': 'Ejemplo',
        })
        assert registry_2.observations == "No refacturable"

    def test_medicine_validation(self):
        self.env['lending.kairos.line'].create({
            'lending_id': self.lending.id,
            'value_line_ids': [(0, 0, {
                'value': 200,
                'date': fields.Date.today()
            })]
        })
        registry = self._create_registry(150, "010101", "Ejemplo1")
        registry.write({'medicine_id': self.lending.id})
        assert registry.calculate_medicine_value(self.rate_line, self.lending) == 2000
        assert registry.rate_value == 2000

    def test_get_kairos_value_by_date(self):
        self.env['lending.kairos.line'].create({
            'lending_id': self.lending.id,
            'value_line_ids': [(0, 0, {'value': 100, 'date': datetime.today() - relativedelta(days=1)}),
                               (0, 0, {'value': 200, 'date': datetime.today()})
        ]})
        registry = self._create_registry(150, "010101", "Ejemplo1")
        registry.write({'date': datetime.today(), 'medicine_id': self.lending.id})
        assert registry.get_kairos_value(self.lending) == 200
        registry.write({'date': datetime.today() - relativedelta(days=1)})
        assert registry.get_kairos_value(self.lending) == 100
        registry.write({'date': datetime.today() - relativedelta(days=2)})
        assert not registry.get_kairos_value(self.lending)

    def test_get_kairos_value_rate_coefficient(self):
        lending_3 = self.env['lending'].create({
            'code': '020102',
            'name': 'Prestacion 3',
        })
        self.env['lending.kairos.line'].create({
            'lending_id': lending_3.id,
            'value_line_ids': [(0, 0, {'value': 400, 'date': datetime.today()})]
        })
        registry = self._create_registry(150, "010101", "Ejemplo1")
        registry.write({'date': datetime.today(), 'medicine_id': lending_3.id})
        self.rate.coefficient = 0.5
        assert registry.calculate_medicine_value_no_rate_line(self.rate, lending_3) == 200

    def test_registry_get_rate_line_description_line_with_lender_code(self):
        self.env['lending.rate.line'].create({
            'lending_id': self.lending_2.id,
            'lender_code': '900000',
            'value': 1000,
            'rate_id': self.rate.id,
            'description': 'PRESTACION'
        })
        registry = self._create_registry(150, "900000", "Ejemplo1")
        assert registry.get_rate_line_description(self.rate) == "PRESTACION"

    def test_registry_get_rate_line_description_line_with_code(self):
        self.lending_2.code = '900000'
        self.env['lending.rate.line'].create({
            'lending_id': self.lending_2.id,
            'value': 1000,
            'rate_id': self.rate.id,
            'description': 'PRESTACION'
        })
        registry = self._create_registry(150, "900000", "Ejemplo1")
        assert registry.get_rate_line_description(self.rate) == "PRESTACION"

    def test_registry_get_rate_line_description_lines_with_lender_code_and_code(self):
        self.lending_2.code = '900000'
        self.env['lending.rate.line'].create({
            'lending_id': self.lending_2.id,
            'value': 1000,
            'rate_id': self.rate.id,
            'description': 'PRESTACION'
        })
        self.env['lending.rate.line'].create({
            'lending_id': self.lending.id,
            'lender_code': '900000',
            'value': 1000,
            'rate_id': self.rate.id,
            'description': 'PRESTACIONN'
        })
        registry = self._create_registry(150, "900000", "Ejemplo1")
        assert registry.get_rate_line_description(self.rate) == "PRESTACIONN"

    def test_registry_get_rate_line_description_line_with_range(self):
        self.lending_2.code = '900000'
        self.env['lending.rate.line'].create({
            'lending_id': self.lending_2.id,
            'code_range': '990000',
            'value': 1000,
            'rate_id': self.rate.id,
            'description': 'PRESTACION'
        })
        registry = self._create_registry(150, "900000", "Ejemplo1")
        assert not registry.get_rate_line_description(self.rate)

    def test_registry_get_rate_line_description_line_from_nomenclator(self):
        self.rate.line_ids.unlink()
        self.env['lending.nomenclator.line'].create({
            'lending_id': self.lending.id,
            'code': '900000',
            'description': 'EJEMPLO',
            'nomenclator_id': self.nomenclator_nn.id,
            'unit': 10,
            'unit_expense': 2,
            'value': 5,
        })
        registry = self._create_registry(150, "900000", "Ejemplo1")
        assert registry.get_rate_line_description(self.rate) == "EJEMPLO"

    def test_registry_get_rate_line_description_line_from_rate_line_ignore_nomenclator(self):
        self.env['lending.rate.line'].create({
            'lending_id': self.lending_2.id,
            'lender_code': '900000',
            'value': 1000,
            'rate_id': self.rate.id,
            'description': 'PRESTACION'
        })
        self.lending.code = '900000'
        self.env['lending.nomenclator.line'].create({
            'lending_id': self.lending.id,
            'description': 'EJEMPLO',
            'nomenclator_id': self.nomenclator_nn.id,
            'unit': 10,
            'unit_expense': 2,
            'value': 5,
        })
        registry = self._create_registry(150, "900000", "Ejemplo1")
        assert registry.get_rate_line_description(self.rate) == "PRESTACION"

    def test_registry_get_rate_line_description_line_from_lending(self):
        self.rate.line_ids.unlink()
        self.nomenclator_nn.line_ids.unlink()
        self.nomenclator_nbu.line_ids.unlink()
        self.lending.code = '900000'
        self.lending.description = "Un ejemplo"
        registry = self._create_registry(150, "900000", "Ejemplo1")
        assert registry.get_rate_line_description(self.rate) == "Un ejemplo"

    def test_registry_get_rate_line_description_false(self):
        registry = self._create_registry(150, "999999", "Ejemplo1")
        assert not registry.get_rate_line_description(self.rate)

    def test_registry_update_description_on_validate_if_rate_line_found(self):
        self.lending_2.code = '900000'
        self.env['lending.rate.line'].create({
            'lending_id': self.lending_2.id,
            'value': 1000,
            'rate_id': self.rate.id,
            'description': 'PRESTACION'
        })
        registry = self._create_registry(150, "900000", "Ejemplo1")
        registry.validate()
        assert registry.description == "PRESTACION"

    def test_registry_dont_update_description_on_validate_if_no_rate_line_found(self):
        registry = self._create_registry(150, "999999", "Ejemplo1")
        registry.validate()
        assert registry.description == "Ejemplo1"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
