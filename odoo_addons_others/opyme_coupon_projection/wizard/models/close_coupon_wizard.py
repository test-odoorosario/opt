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

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class CloseCouponWizard(models.TransientModel):
    _name = 'close.coupon.wizard'

    date = fields.Date(
        string='Fecha de cierre',
        default=fields.Date.today(),
        required=True,
    )

    configuration_hour_projection = fields.Char(
        string='Horario',
        default=lambda self: self.env.user.company_id.configuration_hour_projection
    )

    @api.multi
    def close_coupon(self):
        coupons_ids = self.env.context.get('active_ids')
        coupons = self.env['bank.card.coupon'].browse(coupons_ids)
        errors = []
        for coupon in coupons:
            # Si la cuota del cupon no tiene el estimado de dias se agrega a la lista de errores
            if coupon.bank_card_fee_id.estimated_days_accreditation < 0:
                errors.append('Por favor complete la cantidad de dias de acreditacion '
                              'estimados de la cuota: "{0}" del cupon: "{1}".'.format(coupon.bank_card_fee_id.name,
                                                                                      coupon.number))
            # Si la cuota del cupon no tiene el porcentaje estimado se agrega a la lista de errores
            if not coupon.bank_card_fee_id.percentage_of_accreditation:
                errors.append('Por favor complete el porcentaje de acreditacion '
                              ' de la cuota: "{0}" del cupon: "{1}".'.format(coupon.bank_card_fee_id.name,
                                                                             coupon.number))
        # Si hay errores muestro los errores
        if errors:
            raise ValidationError(
                "No se ha podido realizar la operacion por los siguientes errores:\n" +
                "\n".join(errors))
        # Si no hay errores calculo la fecha de cierre de los cupones
        # el monto estimado y la fecha estimada.
        date = self.date
        holidays = self.env['card.holidays'].search([
            ('date', '>=', date)
        ]).mapped('date')
        for coupon in coupons:
            total_days = coupon.bank_card_fee_id.estimated_days_accreditation
            percentage = coupon.bank_card_fee_id.percentage_of_accreditation
            estimated_amount = coupon.amount * percentage / 100
            stop_date = self.check_holidays(date, total_days, holidays)
            coupon.write({
                'date_closed': date,
                'estimated_amount': estimated_amount,
                'estimated_date': stop_date,
            })

    def check_holidays(self, date, qty_days, holidays):
        day = 0
        date = datetime.strptime(date, '%Y-%m-%d')
        while day < qty_days:
            # Chequeo si es sabado, si es asi sumo dos dias
            day += 1
            date = date + relativedelta(days=1)
            if date.weekday() == 5:
                date = date + relativedelta(days=2)
            if date.weekday() == 6:
                date = date + relativedelta(days=1)
            # Chequeo si un dia de semana hay un feriado, si es asi sumo un dia
            else:
                if date.strftime("%Y-%m-%d") in holidays:
                    date = date + relativedelta(days=1)
                    date = self.check_holidays(
                        (date - relativedelta(days=1)).strftime("%Y-%m-%d"), 1, holidays
                    )
        return date

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
