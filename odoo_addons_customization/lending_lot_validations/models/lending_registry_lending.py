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
from datetime import datetime
from openerp.exceptions import ValidationError


class LendingRegistryLending(models.Model):
    _inherit = 'lending.registry.lending'

    observations = fields.Text(
        string="Observaciones",
    )

    def get_rate(self):
        self.ensure_one()
        return self.env['lending.rate'].search(
            [('lender_id', '=', self.lot_id.lender_id.id), ('date', '<=', self.date), ('end_date', '=', False)],
            limit=1,
            order='date desc'
        )

    @api.model
    def create(self, vals):
        res = super(LendingRegistryLending, self).create(vals)
        res.validate()
        return res

    def write(self, vals):
        res = super(LendingRegistryLending, self).write(vals)
        if not ('debit' in vals or 'observations' in vals or 'no_debit' in vals):
            self.validate()
        return res

    def validate(self):
        for reg in self:
            errors = []
            rate = reg.get_rate()
            dict = reg.check_amount(rate)
            c_re_invoice = reg.check_re_invoice()
            c_duplicity = ''
            if not reg.re_invoice_id:
                c_duplicity = reg.check_duplicity()
            c_aff_duplicity = reg.check_affiliate_duplicity()
            c_dates = reg.check_dates(rate)
            c_lending_rate = reg.check_lending_in_rate(rate)
            if c_re_invoice:
                errors.append(c_re_invoice)
            if c_duplicity:
                errors.append(c_duplicity)
            if c_aff_duplicity:
                errors.append(c_aff_duplicity)
            if c_dates:
                errors.append(c_dates)
            if c_lending_rate:
                errors.append(c_lending_rate)
            rate_line_description = reg.get_rate_line_description(rate)
            if rate_line_description:
                dict['description'] = rate_line_description
            dict['total_to_pay'] = reg.informed_value - dict.get('debit', reg.debit)
            dict['observations'] = " - ".join(errors)
            if reg.debit_motive_ids and reg.informed_value:
                motive_sorted = reg.debit_motive_ids.sorted(lambda x: x.percentage, reverse=True)
                if motive_sorted[0].percentage > 0:
                    dict['debit'] = motive_sorted[0].percentage * reg.informed_value / 100
                    dict['total_to_pay'] = motive_sorted[0].percentage * reg.informed_value / 100 - reg.informed_value
            reg.write(dict)

    def calculate_value(self, rate_line):
        """ Devuelvo el valor final de la prestacion """
        if not rate_line:
            return 0
        nomenclator_line = self.env['lending.nomenclator.line'].search(
            [('code', '=', self.code), ('nomenclator_id', '=', rate_line.nomenclator_id.id)], limit=1
        )
        value = rate_line.value
        if nomenclator_line and rate_line.nomenclator_id:
            CALCULATION_TYPE = {
                'galeno': nomenclator_line.unit * rate_line.value,
                'expense': nomenclator_line.unit_expense * rate_line.value,
                'galeno_expense': nomenclator_line.unit * rate_line.value_galeno + nomenclator_line.unit_expense * rate_line.value,
                'final_amount': nomenclator_line.amount_total * rate_line.value
            }
            value = CALCULATION_TYPE.get(str(rate_line.calculation_type))
        return value

    def get_kairos_value(self, medicine):
        """ Obtengo, según los registros de Kairos, el valor de medicamento vigente en la fecha del registro """
        # Busco las líneas de Kairos que tengan el código, principio activo y gramaje que necesito
        kairos_lines = self.env['lending.kairos.line'].search([
            ('code', '=', medicine.code), ('description_drug', '=', medicine.description_drug),
            ('description_presentation', '=', medicine.description_presentation)
        ])
        value = 0
        # Para todas las líneas de Kairos que encontré, busco el valor más reciente para la fecha del registro y me fijo
        # si es menor al que tengo. Si es menor, lo reemplazo por ese.
        for kairos in kairos_lines:
            value_lines = kairos.value_line_ids.filtered(lambda l: l.date <= self.date)
            if value_lines:
                last_value = value_lines[0].value
                if not value or last_value < value:
                    value = last_value
        return value

    def calculate_medicine_value(self, rate_line, medicine):
        """ Calculo el valor del medicamento en base al valor del Kairos y el coeficiente de la línea de tarifario """
        self.ensure_one()
        return self.get_kairos_value(medicine) * rate_line.value

    def calculate_medicine_value_no_rate_line(self, rate, medicine):
        """ Calculo el valor del medicamento en base al valor del Kairos y el coeficiente del tarifario """
        self.ensure_one()
        return self.get_kairos_value(medicine) * rate.coefficient

    def check_amount(self, rate):
        """ Valido el importe facturado si es correcto"""
        self.ensure_one()
        medicine_id = self.medicine_id
        debit_motive = self.env.ref('bo_lending.debit_motive_amount').id
        if not medicine_id:
            rate_line = rate.mapped('line_ids').filtered(
                lambda x: x.lender_code == self.code and not x.code_range and not x.no_agreed) or rate.mapped(
                'line_ids').filtered(
                lambda x: x.lending_id.code == self.code and not x.code_range and not x.no_agreed) or rate.mapped(
                'line_ids').filtered(lambda x: x.lending_id.code <= self.code <= x.code_range and not x.no_agreed)
            if len(rate_line) > 1:
                raise ValidationError('En el tarifario esta cargada varias veces la prestacion {}'.format(self.code))
            value = self.calculate_value(rate_line)
        else:
            rate_line = rate.mapped('line_ids').filtered(
                lambda x: x.lender_code == medicine_id.code and not x.code_range and not x.no_agreed) or rate.mapped(
                'line_ids').filtered(
                lambda x: x.lending_id.code == medicine_id.code and not x.code_range and not x.no_agreed) or rate.mapped(
                'line_ids').filtered(lambda x: x.lending_id.code <= medicine_id.code <= x.code_range and not x.no_agreed)
            if len(rate_line) > 1:
                raise ValidationError('En el tarifario esta cargado varias veces el medicamento {}'.format(medicine_id.code))
            if len(rate_line) == 1:
                # Si hay una línea de tarifario con el medicamento, uso el valor de la línea para el cálculo
                value = self.calculate_medicine_value(rate_line, medicine_id)
            if not rate_line:
                # Si no hay una línea de tarifario con el medicamento, uso el coeficiente del tarifario para el cálculo
                value = self.calculate_medicine_value_no_rate_line(rate, medicine_id)
        if self.informed_value > (value * self.qty):
            return ({
                'rate_value': value,
                'debit': self.informed_value - value * self.qty,
                'debit_motive_ids': [(4, debit_motive)],
            })
        return {
            'rate_value': value,
            'debit': 0,
            'debit_motive_ids': [(3, debit_motive)],
        }

    def check_re_invoice(self):
        """ Valido que la prestacion se pueda refacturar"""
        self.ensure_one()
        invoice = self.re_invoice_id
        lot_line = invoice.mapped('line_ids.registry_lending_ids').filtered(
            lambda
                x: x.id != self.id and x.date == self.date and x.affiliate_id == self.affiliate_id and x.code == self.code and x.debit_motive_ids)
        motives = lot_line.mapped('debit_motive_ids')
        if any(not motive.is_re_invoice for motive in motives):
            return "No refacturable"
        return False

    def check_duplicity(self):
        """ Valido que la prestacion no este duplicada en cualquier lote"""
        self.ensure_one()
        duplicates = self.search([
            ('date', '=', self.date),
            ('affiliate_id', '=', self.affiliate_id.id),
            ('code', '=', self.code),
            ('lender_id', '=', self.lender_id.id),
            ('id', '!=', self.id)
        ])
        if duplicates:
            return "Prestacion duplicada"
        return False

    def check_affiliate_duplicity(self):
        self.ensure_one()
        numbers = self.env['lending.affiliate'].search([('vat', '=', self.affiliate_vat)])
        if len(numbers) > 1:
            return "Afiliado duplicado"
        return False

    def check_dates(self, rate):
        self.ensure_one()
        if self.lot_id.invoice_id:
            invoice_date = datetime.strptime(self.lot_id.invoice_id.date, '%Y-%m-%d')
            registry_date = datetime.strptime(self.date, '%Y-%m-%d')
            diff = invoice_date - registry_date
            if not self.check_lending_in_rate(rate) and abs(diff.days) > rate.qty_expiration_days:
                return "Vencido"
        return False

    def check_lending_in_rate(self, rate):
        self.ensure_one()
        rate_line_with_lending = rate.line_ids.filtered(
            lambda l: l.lending_id.code == self.code or l.lender_code == self.code or l.lending_id.code <= self.code <= l.code_range)
        if not rate_line_with_lending:
            return "Sin tarifario"
        return False

    def get_rate_line_description(self, rate):
        # Busco en el tarifario, primero por código y después por prestación
        line = rate.line_ids.filtered(lambda l: l.lender_code == self.code and not l.code_range)
        if line:
            return line.description
        line_w_lending = rate.line_ids.filtered(lambda l: l.lending_id.code == self.code and not l.code_range)
        if line_w_lending:
            return line_w_lending.description
        # Busco en las líneas de nomenclador por código
        line = self.env['lending.nomenclator.line'].search([('code', '=', self.code)], limit=1)
        if line:
            return line.description
        # Busco en las prestaciones por código
        lending = self.env['lending'].search([('code', '=', self.code)], limit=1)
        return lending.description if lending else False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
