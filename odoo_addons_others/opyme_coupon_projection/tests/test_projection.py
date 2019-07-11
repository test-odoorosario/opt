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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase, HttpCase
import assert_values_xls


class TestProjection(TransactionCase):

    def create_account_type(self):
        self.account_type_bank = self.env['account.account.type'].create({
            'name': 'Banco',
            'report_type': 'asset',
            'code': 'bank',
            'close_method': 'balance'
        })

    def create_account(self):
        self.account_other = self.env['account.account'].create({
            'code': '1111',
            'name': 'cuenta contable',
            'type': 'other',
            'user_type_id': self.account_type_bank.id,
        })

    def create_journal(self):
        self.journal = self.env.ref('l10n_ar_account_payment.journal_cobros_y_pagos')
        self.journal.write({
            'type': 'bank',
            'bank_id': self.ref('base.res_bank_1'),
            'bank_acc_number': 'Banco 1231'
        })

    def create_card(self):
        card_proxy = self.env['bank.card']
        self.card = card_proxy.create({
            'name': 'Tarjeta 1',
            'bank_account_id': self.journal.id,
            'account_id': self.account_other.id,
        })
        self.card_2 = card_proxy.create({
            'name': 'Tarjeta 2',
            'bank_account_id':self.journal.id,
            'account_id': self.account_other.id,
        })

    def create_fee(self):
        fee_proxy = self.env['bank.card.fee']
        self.fee_1_card_1 = fee_proxy.create({
            'name': 'Cuota 1 para tarjeta 1',
            'bank_card_id': self.card.id,
            'fee_quantity': 6,
        })
        self.fee_2_card_1 = fee_proxy.create({
            'name': 'Cuota 2 para tarjeta 1',
            'bank_card_id': self.card.id,
            'fee_quantity': 18,
        })
        self.fee_1_card_2 = fee_proxy.create({
            'name': 'Cuota 1 para tarjeta 2',
            'bank_card_id': self.card_2.id,
            'fee_quantity': 12,
        })

    def create_coupon(self):
        coupon_proxy = self.env['bank.card.coupon']
        self.coupon_1_card_1 = coupon_proxy.create({
            'number': '100',
            'bank_card_id': self.card.id,
            'bank_card_fee_id': self.fee_1_card_1.id,
            'amount': 200,
            'date': datetime.today(),
            'state': 'posted'
        })
        self.coupon_1_card_2 = coupon_proxy.create({
            'number': '100',
            'bank_card_id': self.card_2.id,
            'bank_card_fee_id': self.fee_2_card_1.id,
            'amount': 100,
            'date': datetime.today(),
            'state': 'draft'
        })
        self.coupon_2_card_2 = coupon_proxy.create({
            'number': '100',
            'bank_card_id': self.card_2.id,
            'bank_card_fee_id': self.fee_2_card_1.id,
            'amount': 500,
            'date': datetime.today(),
            'state': 'posted'
        })

    def setUp(self):
        super(TestProjection, self).setUp()
        self.create_account_type()
        self.create_account()
        self.create_journal()
        self.create_card()
        self.create_fee()
        self.create_coupon()

    def test_check_coupons(self):
        """
        Se testean los cupones
        """
        wizard = self.env['coupon.projection.report'].create({})
        coupons = wizard.search_coupons()
        assert_values_xls._assert_coupons(coupons)

    def test_report_generation_xls(self):
        """
        Se testea que salga el reporte
        """
        wizard = self.env['coupon.projection.report'].create({})
        wizard.generate_report_xls()

    def test_percentage_fee(self):
        with self.assertRaises(ValidationError):
            self.fee_1_card_1.percentage_of_accreditation = -1
        with self.assertRaises(ValidationError):
            self.fee_1_card_1.percentage_of_accreditation = 101
        self.fee_1_card_1.percentage_of_accreditation = 80

    def test_hour_in_configuration(self):
        wizard = self.env['base.config.settings'].create({
            'configuration_hour_projection': '20:10'
        })
        with self.assertRaises(ValidationError):
            wizard.write({'configuration_hour_projection': '24:10'})
        wizard.write({'configuration_hour_projection': '10:59'})

    def test_1_failed_fields_close_coupon(self):
        wizard = self.env['close.coupon.wizard'].with_context(
            active_ids=self.coupon_1_card_1.id
        ).create({
            'date': datetime.today(),
        })
        with self.assertRaises(ValidationError):
            wizard.close_coupon()

    def test_2_fields_close_coupon(self):
        active_ids = self.env.context.get(self.coupon_1_card_1.id)
        wizard = self.env['close.coupon.wizard'].with_context(
            active_ids=active_ids
        ).create({
            'date': datetime.today(),
        })
        self.fee_1_card_1.write({
            'percentage_of_accreditation': 10,
            'estimated_days_accreditation': 1,
        })
        wizard.close_coupon()

    def test_3_close_coupon(self):
        wizard = self.env['close.coupon.wizard'].with_context(
            active_ids=self.coupon_1_card_1.id
        ).create({
            'date': datetime.today(),
        })
        self.fee_1_card_1.write({
            'percentage_of_accreditation': 10,
            'estimated_days_accreditation': 0,
        })

        wizard.close_coupon()
        assert self.coupon_1_card_1.date_closed == wizard.date
        assert self.coupon_1_card_1.estimated_amount == 20
        assert self.coupon_1_card_1.estimated_date == (datetime.strptime(
            wizard.date, '%Y-%m-%d')).strftime("%Y-%m-%d")

    def test_check_weekday(self):
        today = datetime.today()
        wizard = self.env['close.coupon.wizard'].create({
            'date': today - timedelta(days=today.weekday()),  # Para probar un lunes
        })
        assert wizard.check_holidays(wizard.date, 5, []) == (datetime.strptime(
            wizard.date, '%Y-%m-%d') + relativedelta(days=7))

    def test_check_holidays(self):
        today = datetime.today()
        wizard_date = today - timedelta(days=today.weekday())
        wizard = self.env['close.coupon.wizard'].create({
            'date': wizard_date,  # Para probar un lunes
        })
        holidays = self.env['card.holidays'].create({
            'name': 'Feriado',
            'date': wizard_date + timedelta(days=1)
        }).mapped('date')
        assert wizard.check_holidays(wizard.date, 5, holidays) == datetime.strptime(
            wizard.date, '%Y-%m-%d') + relativedelta(days=8)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
