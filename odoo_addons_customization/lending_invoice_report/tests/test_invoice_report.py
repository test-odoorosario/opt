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
from dateutil.relativedelta import relativedelta
from datetime import datetime


class TestInvoiceReport(TransactionCase):

    def create_customer(self):
        self.customer = self.env['lending.customer'].create({
            'code': '0001/C',
            'name': 'CLIENTE'
        })

    def create_lender(self):
        self.lender = self.env['lending.lender'].create({
            'code': '0001/P',
            'name': 'PRESTADOR'
        })

    def create_wizard(self):
        self.wizard = self.env['lending.invoice.report.wizard'].create({
            'lender_id': self.lender.id,
            'customer_id': self.customer.id,
            'date_from': datetime.now(),
            'date_to': datetime.now()
        })

    def setUp(self):
        super(TestInvoiceReport, self).setUp()
        self.create_customer()
        self.create_lender()
        self.create_wizard()

    def test_domain_invoices(self):
        self.env['lending.invoice'].create({
            'name': "Factura",
            'customer_id': self.customer.id,
            'lender_id': self.lender.id,
            'date': datetime.now() + relativedelta(days=30),
            'entry_date': datetime.now(),
            'due_date': datetime.now(),
        })
        self.env['lending.invoice'].create({
            'name': "Factura 2",
            'customer_id': self.customer.id,
            'lender_id': self.lender.id,
            'date': datetime.now(),
            'entry_date': datetime.now(),
            'due_date': datetime.now(),
        })
        domain = self.wizard.onchange_dates()
        assert len(domain.get('domain').get('invoice_ids')[0][2]) == 1
        self.wizard.update({'date_to': datetime.now() + relativedelta(days=30)})
        domain = self.wizard.onchange_dates()
        assert len(domain.get('domain').get('invoice_ids')[0][2]) == 2

    def test_check_date(self):
        """Validamos el rango de fechas"""
        with self.assertRaises(ValidationError):
            self.wizard.date_to = datetime.now() - relativedelta(months=1)

    def test_build_num_to_string(self):
        num_string = self.wizard._build_num_to_string(10.5)
        assert num_string == "DIEZ PESOS Y CINCUENTA CENTAVOS"

    def test_get_invoices(self):
        with self.assertRaises(ValidationError):
            self.wizard.get_invoices()
        self.env['lending.invoice'].create({
            'name': '001',
            'customer_id': self.customer.id,
            'lender_id': self.lender.id,
            'date': datetime.now()
        })
        self.wizard.get_invoices()

    def test_get_name_invoices(self):
        self.wizard.date_from = datetime(2018, 1, 15, 0, 0, 0)
        assert self.wizard.get_period() == "enero 2018"

    def test_get_types_lots(self):
        invoice = self.env['lending.invoice'].create({
            'name': '001',
            'customer_id': self.customer.id,
            'lender_id': self.lender.id,
            'date': datetime.now(),
        })
        invoice2 = self.env['lending.invoice'].create({
            'name': '002',
            'customer_id': self.customer.id,
            'lender_id': self.lender.id,
            'date': datetime.now(),
        })
        lot = self.env['lending.lot'].create({
            'name': 'L0001',
            'lender_id': self.lender.id,
            'lending_lot_type_id': self.env['lending.lot.type'].create({
                'name': 'ambULATORIO'
            }).id
        })
        lot2 = self.env['lending.lot'].create({
            'name': 'L0002',
            'lender_id': self.lender.id,
            'lending_lot_type_id': self.env['lending.lot.type'].create({
                'name': 'TRASLado'
            }).id
        })
        invoice.line_ids = [(4, lot.id)]
        invoice2.line_ids = [(4, lot2.id)]
        assert self.wizard.get_types_lots() == "AMBULATORIO/TRASLADO"
        invoice2.date = datetime.now() + relativedelta(days=2)
        assert self.wizard.get_types_lots() == "AMBULATORIO"

    def test_get_total(self):
        invoice = self.env['lending.invoice'].create({
            'name': '001',
            'customer_id': self.customer.id,
            'lender_id': self.lender.id,
            'date': datetime.now(),
            'amount_untaxed': 170,
        })
        lot = self.env['lending.lot'].create({
            'name': 'L0001',
            'lender_id': self.lender.id,
            'lending_lot_type_id': self.env['lending.lot.type'].create({
                'name': 'ambULATORIO'
            }).id
        })
        self.env['lending.registry.lending'].create({
            'code': 170101,
            'description': 'TEST',
            'informed_value': 170,
            'date': datetime.now(),
            'affiliate_id': self.env['lending.affiliate'].create({
                'name': 'Afiliado',
                'code': '01',
                'document_type': 'dni',
                'vat': '3000',
            }).id,
            'lot_id': lot.id,
        })
        invoice.line_ids = [(4, lot.id)]
        assert self.wizard.get_total() == 170

    def test_get_debit_motive(self):
        invoice = self.env['lending.invoice'].create({
            'name': '001',
            'customer_id': self.customer.id,
            'lender_id': self.lender.id,
            'date': datetime.now(),
        })
        lot = self.env['lending.lot'].create({
            'name': 'L0001',
            'lender_id': self.lender.id,
            'lending_lot_type_id': self.env['lending.lot.type'].create({
                'name': 'ambULATORIO'
            }).id
        })
        motive = self.env.ref('bo_lending.debit_motive_without_term')
        self.env['lending.registry.lending'].create({
            'code': 170101,
            'description': 'TEST',
            'informed_value': 170,
            'date': datetime.now(),
            'affiliate_id': self.env['lending.affiliate'].create({
                'name': 'Afiliado',
                'code': '001',
                'document_type': 'dni',
                'vat': '30000',
            }).id,
            'lot_id': lot.id,
            'debit_motive_ids': [(4, motive.id)]
        })
        invoice.line_ids = [(4, lot.id)]
        assert self.wizard.get_debit_motive()[0].name == 'Prestacion fuera de termino'

    def test_get_debit_motive_total(self):
        invoice = self.env['lending.invoice'].create({
            'name': '001',
            'customer_id': self.customer.id,
            'lender_id': self.lender.id,
            'date': datetime.now(),
        })
        lot = self.env['lending.lot'].create({
            'name': 'L0001',
            'lender_id': self.lender.id,
            'lending_lot_type_id': self.env['lending.lot.type'].create({
                'name': 'ambULATORIO'
            }).id
        })
        motive = self.env.ref('bo_lending.debit_motive_without_term')
        registry = self.env['lending.registry.lending'].create({
            'code': 170101,
            'description': 'TEST',
            'informed_value': 170,
            'date': datetime.now(),
            'affiliate_id': self.env['lending.affiliate'].create({
                'name': 'Afiliado',
                'code': '01',
                'document_type': 'dni',
                'vat': '3000',
            }).id,
            'lot_id': lot.id,
            'debit_motive_ids': [(4, motive.id)]
        })
        registry2 = self.env['lending.registry.lending'].create({
            'code': 170102,
            'description': 'TEST',
            'informed_value': 100,
            'date': datetime.now(),
            'affiliate_id': self.env['lending.affiliate'].create({
                'name': 'Afiliado',
                'code': '010',
                'document_type': 'dni',
                'vat': '30000',
            }).id,
            'lot_id': lot.id,
            'debit_motive_ids': [(4, motive.id)]
        })
        registry.debit = 50
        registry2.debit = 50
        invoice.line_ids = [(4, lot.id)]
        assert self.wizard.get_debit_motive_total(motive) == 100

    def test_get_debit_motive_total_difference_motive(self):
        invoice = self.env['lending.invoice'].create({
            'name': '001',
            'customer_id': self.customer.id,
            'lender_id': self.lender.id,
            'date': datetime.now(),
            'amount_untaxed': 150,
        })
        lot = self.env['lending.lot'].create({
            'name': 'L0001',
            'lender_id': self.lender.id,
            'lending_lot_type_id': self.env['lending.lot.type'].create({
                'name': 'Ambulatorio'
            }).id
        })
        self.env['lending.registry.lending'].create({
            'code': 170101,
            'description': 'TEST',
            'informed_value': 200,
            'date': datetime.now(),
            'affiliate_id': self.env['lending.affiliate'].create({
                'name': 'Afiliado',
                'code': '01',
                'document_type': 'dni',
                'vat': '3000',
            }).id,
            'lot_id': lot.id,
        })
        invoice.line_ids = [(4, lot.id)]
        motive = self.env.ref('lending_invoice_report.debit_motive_invoice_difference')
        assert self.wizard.get_debit_motive_total(motive) == 50

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
