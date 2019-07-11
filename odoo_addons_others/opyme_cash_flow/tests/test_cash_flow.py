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

from dateutil.relativedelta import relativedelta
from openerp.tests.common import TransactionCase
from datetime import date, timedelta
from openerp.exceptions import ValidationError


class TestCashFlow(TransactionCase):

    def prepare_date_for_invoice(self):
        # Proxies
        self.iva_ri = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari')
        self.company_fiscal_position = self.env.user.company_id.partner_id.property_account_position_id
        self.document_book_proxy = self.env['document.book']
        self.pos_proxy = self.env['pos.ar']

        # Configuracion de posicion fiscal RI en la compania
        self.env.user.company_id.partner_id.property_account_position_id = self.iva_ri

        self.pos = self.pos_proxy.create({'name': 5})
        self.document_book = self.document_book_proxy.create({
            'name': 100,
            'pos_ar_id': self.pos.id,
            'category': 'invoice',
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_invoice').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_invoice').id,
            'denomination_id': self.env.ref('l10n_ar_afip_tables.account_denomination_a').id,
        })

        self.partner = self.env['res.partner'].create({
            'name': "Customer",
            'email': "customer@example.com",
            'property_account_position_id': self.iva_ri.id
        })
        self.journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        self.account = self.env['account.account'].search([('user_type_id.type', '=', 'receivable')], limit=1)

    def create_invoices(self):
        self.prepare_date_for_invoice()
        self.invoice_1 = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'fiscal_position_id': self.partner.property_account_position_id.id,
            'journal_id': self.journal.id,
            'denomination_id': self.env.ref('l10n_ar_afip_tables.account_denomination_a').id,
            'pos_ar_id': self.pos.id,
            'date_due': date.today(),
            'type': 'out_invoice',
        })
        self.env['account.invoice.line'].create({
            'name': 'Producto',
            'account_id': self.env.ref('l10n_ar.1_bienes_de_cambio').id,
            'quantity': 1,
            'price_unit': 500,
            'invoice_id': self.invoice_1.id,
        })
        self.invoice_1.action_invoice_open()

        self.invoice_2 = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'fiscal_position_id': self.partner.property_account_position_id.id,
            'journal_id': self.journal.id,
            'denomination_id': self.env.ref('l10n_ar_afip_tables.account_denomination_a').id,
            'pos_ar_id': self.pos.id,
            'date_due': date.today() + relativedelta(days=3),
            'type': 'out_invoice',
        })
        self.env['account.invoice.line'].create({
            'name': 'Producto',
            'account_id': self.env.ref('l10n_ar.1_bienes_de_cambio').id,
            'quantity': 1,
            'price_unit': 1500,
            'invoice_id': self.invoice_2.id,
        })
        self.invoice_2.action_invoice_open()

    def create_cash_flow(self):
        config = self.create_configuration_empty()
        return self.env['account.cash.flow'].create({
            'date_start': date.today(),
            'date_stop': date.today() + relativedelta(days=1),
            'configuration_id': config.id,
        })

    def create_configuration_empty(self):
        return self.env['cash.flow.configuration'].create({
            'name': 'Configuration 1',
        })

    def create_move(self):
        # Creo el diario para usar en el asiento
        self.journal = self.env['account.journal'].create({
            'name': 'CYP',
            'code': 'CYP',
            'type': 'bank',
        })
        # Creo el asiento con los datos necesarios
        self.move = self.env['account.move'].create({
            'name': 'Test',
            'journal_id': self.journal.id,
            'ref': 'Referencia asiento contable',
            'date': date.today(),
        })

    def create_accounts(self):
        self.account_debit = self.env['account.account'].create({
            'name': 'Cuenta debito',
            'code': 100,
            'user_type_id': self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })
        self.account_credit = self.env['account.account'].create({
            'name': 'Cuenta credito',
            'code': 101,
            'user_type_id': self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })

    def create_third_checks(self):
        third_check_proxy = self.env['account.third.check']
        date_today = date.today()
        self.third_check = third_check_proxy.create({
            'name': '12345678',
            'bank_id': self.env['res.bank'].search([], limit=1).id,
            'payment_type': 'common',
            'amount': 1300,
            'currency_id': self.env.user.company_id.currency_id.id,
            'issue_date': date_today,
            'payment_date': date_today,
            'state': 'wallet'
        })
        self.third_check_2 = third_check_proxy.create({
            'name': '123456789',
            'bank_id': self.env['res.bank'].search([], limit=1).id,
            'payment_type': 'common',
            'amount': 100,
            'currency_id': self.env.user.company_id.currency_id.id,
            'issue_date': date_today,
            'payment_date': date_today,
            'state': 'draft'
        })

    def setUp(self):
        super(TestCashFlow, self).setUp()

    def test_check_date(self):
        """Chequeo que valide el rango de fechas correctamente"""
        config = self.create_configuration_empty()
        with self.assertRaises(ValidationError):
            self.env['account.cash.flow'].create({
                'date_start': date.today() + relativedelta(days=1),
                'date_stop': date.today(),
                'configuration_id': config.id,
            })

    def test_accumulated(self):
        """Calculamos el acumulado por linea"""
        cash_flow = self.create_cash_flow()
        line_1 = self.env['account.cash.flow.line'].create({
            'date': date.today() + relativedelta(days=1),
            'debit': 10,
            'cash_flow_id': cash_flow.id,
        })
        line_2 = self.env['account.cash.flow.line'].create({
            'date': date.today(),
            'credit': 200,
            'cash_flow_id': cash_flow.id,
        })
        cash_flow._set_accumulated(cash_flow.id)
        assert line_2.accumulated == -200
        assert line_1.accumulated == -190

    def test_search_move_line(self):
        """Testeo que traiga correctamente los movimientos"""
        # Creacion de cuentas
        self.create_accounts()
        config = self.create_configuration_empty()
        config.write({
            'account_ids': [(4, [self.account_credit.id, self.account_debit.id])]
        })
        self.create_move()
        # Creo las lineas de los asientos con el with context para que no valide el balanceo del asientos
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'CUENTA CREDITO',
            'account_id': self.account_credit.id,
            'credit': 10,
            'date': date.today(),
            'date_maturity': date.today(),
            'move_id': self.move.id
        })
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'CUENTA CREDITO 2',
            'account_id': self.account_credit.id,
            'credit': 10,
            'date': date.today(),
            'date_maturity': date.today(),
            'move_id': self.move.id
        })
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'MOVIMIENTO FECHA FUTURA. NO TIENE QUE TOMARSE',
            'account_id': self.account_debit.id,
            'debit': 10,
            'date': date.today() + relativedelta(days=1),
            'date_maturity': date.today() + relativedelta(days=1),
            'move_id': self.move.id
        })
        assert len(config.search_past_move_lines(self.account_debit, date.today())) == 0
        assert len(config.search_past_move_lines(self.account_credit, date.today())) == 2

    def test_search_futute_move_line(self):
        """Testeo que traiga correctamente los movimientos"""
        # Creacion de cuentas
        self.create_accounts()
        config = self.create_configuration_empty()
        config.write({
            'account_ids': [(4, [self.account_credit.id, self.account_debit.id])]
        })
        self.create_move()
        yesterday = date.today() - relativedelta(days=1)
        today = date.today()
        tomorrow = date.today() + relativedelta(days=1)
        future_date = date.today() + relativedelta(days=7)
        # Creo las lineas de los asientos con el with context para que no valide el balanceo del asientos
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'CUENTA CREDITO PASADA, NO DEBE FIGURAR',
            'account_id': self.account_credit.id,
            'credit': 10,
            'date': yesterday,
            'date_maturity': yesterday,
            'move_id': self.move.id
        })
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'CUENTA CREDITO 1',
            'account_id': self.account_credit.id,
            'credit': 10,
            'date': tomorrow,
            'date_maturity': tomorrow,
            'move_id': self.move.id
        })
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'CUENTA DEBITO 1',
            'account_id': self.account_debit.id,
            'debit': 10,
            'date': tomorrow,
            'date_maturity': tomorrow,
            'move_id': self.move.id
        })

        assert len(config.search_future_move_lines(self.account_debit, today, future_date)) == 1
        assert len(config.search_future_move_lines(self.account_credit, today, future_date)) == 1

    def test_set_account(self):
        """ Chequeo que setee correctamente los datos de cuentas configuradas"""
        cash_flow = self.create_cash_flow()
        self.create_accounts()
        config = self.create_configuration_empty()
        config.write({
            'account_ids': [(4, [self.account_credit.id, self.account_debit.id])]
        })
        self.create_move()
        # Creo las lineas de los asientos con el with context para que no valide el balanceo del asientos
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'CUENTA CREDITO',
            'account_id': self.account_credit.id,
            'credit': 10,
            'date': date.today(),
            'move_id': self.move.id
        })
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'CUENTA CREDITO 2',
            'account_id': self.account_credit.id,
            'credit': 10,
            'date': date.today(),
            'move_id': self.move.id
        })
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'FECHA FUTURA. NO TIENE QUE TOMARSE',
            'account_id': self.account_debit.id,
            'debit': 10,
            'date': date.today() + relativedelta(days=1),
            'move_id': self.move.id
        })
        assert len(config._set_account_values(cash_flow.id, date.today())) == 1
        assert config._set_account_values(cash_flow.id, date.today())[0].get('balance') == -20

    def test_calculate_balance(self):
        """Chequeo el calculo de balance de cuentas"""
        # Creacion de cuentas
        self.create_accounts()
        config = self.create_configuration_empty()
        config.write({
            'account_ids': [(4, [self.account_credit.id, self.account_debit.id])]
        })
        self.create_move()
        # Creo las lineas de los asientos con el with context para que no valide el balanceo del asientos
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'CUENTA CREDITO',
            'account_id': self.account_credit.id,
            'credit': 10,
            'date': date.today(),
            'date_maturity': date.today(),
            'move_id': self.move.id
        })
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'CUENTA CREDITO 2',
            'account_id': self.account_credit.id,
            'credit': 10,
            'date': date.today(),
            'date_maturity': date.today(),
            'move_id': self.move.id
        })
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'ESTA NO DEBERIA TOMARLA POR SER CON FECHA FUTURA',
            'account_id': self.account_credit.id,
            'credit': 100,
            'date': date.today() + relativedelta(days=3),
            'date_maturity': date.today() + relativedelta(days=3),
            'move_id': self.move.id
        })
        move_lines = config.search_past_move_lines(self.account_credit, date.today())
        assert config.calculate_balance(move_lines) == -20

    def test_get_invoices(self):
        """Chequeo que traiga correctamente las facturas"""
        self.create_invoices()
        config = self.create_configuration_empty()
        config.write({
            'account_ids': [(4, [self.account.id])]
        })
        assert len(config._get_invoice_values(date.today(), ['out_invoice'])) == 1
        self.invoice_2.write({'date_due': date.today()})
        assert len(config._get_invoice_values(date.today(), ['out_invoice'])) == 2

    def test_set_invoices(self):
        """Chequeo que setee correctamente las facturas"""
        self.create_invoices()
        cash = self.create_cash_flow()
        config = self.create_configuration_empty()
        config.write({
            'account_ids': [(4, [self.account.id])]
        })
        assert len(config._get_invoice_values(date.today(), ['out_invoice'])) == 1
        self.invoice_2.write({'date_due': date.today()})
        assert len(config._get_invoice_values(date.today(), ['out_invoice'])) == 2
        invoices = config._get_invoice_values(date.today(), ['out_invoice'])
        invoices_vals = config._set_invoice_values(date.today().strftime('%d/%m/%Y'), invoices, cash.id)
        assert len(invoices_vals) == 2
        assert invoices_vals[0].get('debit') == 1500
        assert invoices_vals[1].get('debit') == 500

    def test_set_invoices_ndd(self):
        """Chequeo que setee correctamente las facturas (Nota de debito)"""
        self.create_invoices()
        cash = self.create_cash_flow()
        config = self.create_configuration_empty()
        config.write({
            'account_ids': [(4, [self.account.id])]
        })
        self.invoice_1.write({
            'is_debit_note': True
        })
        assert len(config._get_invoice_values(date.today(), ['out_invoice'])) == 1
        invoices = config._get_invoice_values(date.today(), ['out_invoice'])
        invoices_vals = config._set_invoice_values(date.today().strftime('%d/%m/%Y'), invoices, cash.id)
        assert len(invoices_vals) == 1
        assert invoices_vals[0].get('reference') == self.invoice_1.name_get()[0][1] + ' - ' + self.invoice_1.partner_id.name
        self.invoice_2.write({'date_due': date.today()})
        invoices_2 = config._get_invoice_values(date.today(), ['out_invoice'])
        invoices_vals_2 = config._set_invoice_values(date.today().strftime('%d/%m/%Y'), invoices_2, cash.id)
        assert len(invoices_vals_2) == 2
        assert invoices_vals_2[0].get('reference') == self.invoice_2.name_get()[0][1] + ' - ' + self.invoice_2.partner_id.name
        assert invoices_vals_2[1].get('reference') == self.invoice_1.name_get()[0][1] + ' - ' + self.invoice_1.partner_id.name

    def test_set_invoices_ndc(self):
        """Chequeo que setee correctamente las facturas (Nota de credito)"""
        self.create_invoices()
        cash = self.create_cash_flow()
        config = self.create_configuration_empty()
        config.write({
            'account_ids': [(4, [self.account.id])]
        })
        self.invoice_1.write({
            'type': 'in_refund'
        })
        assert len(config._get_invoice_values(date.today(), ['out_invoice', 'in_refund'])) == 1
        invoices = config._get_invoice_values(date.today(), ['out_invoice', 'in_refund'])
        invoices_vals = config._set_invoice_values(date.today().strftime('%d/%m/%Y'), invoices, cash.id)
        assert len(invoices_vals) == 1
        assert invoices_vals[0].get('reference') == self.invoice_1.name_get()[0][1] + ' - ' + self.invoice_1.partner_id.name
        self.invoice_2.write({'date_due': date.today()})
        invoices_2 = config._get_invoice_values(date.today(), ['out_invoice', 'in_refund'])
        invoices_vals_2 = config._set_invoice_values(date.today().strftime('%d/%m/%Y'), invoices_2, cash.id)
        assert len(invoices_vals_2) == 2
        assert invoices_vals_2[0].get('reference') == self.invoice_2.name_get()[0][1] + ' - ' + self.invoice_2.partner_id.name
        assert invoices_vals_2[1].get('reference') == self.invoice_1.name_get()[0][1] + ' - ' + self.invoice_1.partner_id.name

    def test_get_check(self):
        """Chequeo que traiga correctamente los cheques de terceros"""
        cash = self.create_cash_flow()
        self.create_third_checks()
        checks = self.env['account.third.check'].search(
            [('state', '=', 'wallet')]
        )
        assert len(checks) == 1
        config = self.create_configuration_empty()
        today = date.today() + timedelta(days=-date.today().weekday(), weeks=1)
        checks_ok = config._get_check_values(today.strftime('%Y-%m-%d'), (today - relativedelta(days=1)).strftime('%Y-%m-%d'), checks, cash.id)
        assert len(checks_ok) == 0
        checks_ok = config._get_check_values(today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), checks, cash.id)
        assert len(checks_ok) == 1

    def test_set_third_check(self):
        """Chequeo que traiga correctamente los cheques de terceros"""
        self.create_third_checks()
        cash = self.create_cash_flow()
        checks = self.env['account.third.check'].search(
            [('state', '=', 'wallet')]
        )
        assert len(checks) == 1
        config = self.create_configuration_empty()
        today = date.today() + timedelta(days=-date.today().weekday(), weeks=1)
        checks_ok = config._get_check_values(today.strftime('%Y-%m-%d'), (today - relativedelta(days=1)).strftime('%Y-%m-%d'), checks, cash.id)
        assert len(checks_ok) == 0
        checks_ok = config._get_check_values(today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), checks, cash.id)
        assert len(checks_ok) == 1
        assert checks_ok[0].get('reference') == 'Cheque de tercero a depositar N° 12345678'
        assert checks_ok[0].get('balance') == 1300

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
