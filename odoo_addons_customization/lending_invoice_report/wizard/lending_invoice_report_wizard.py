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


class LendingInvoiceReportWizard(models.TransientModel):
    _name = 'lending.invoice.report.wizard'

    lender_id = fields.Many2one(
        comodel_name='lending.lender',
        string='Prestador',
        ondelete='cascade',
        required=True
    )
    customer_id = fields.Many2one(
        comodel_name='lending.customer',
        string='Cliente',
        ondelete='cascade',
        required=True
    )
    date_from = fields.Date(
        string='Fecha inicio',
        required=True
    )
    date_to = fields.Date(
        string='Fecha fin',
        required=True
    )
    date_today = fields.Date(
        string='Fecha actual',
        default=fields.Date.context_today,
    )
    invoice_ids = fields.Many2many(
        comodel_name='lending.invoice',
        string='Facturas'
    )

    @api.onchange('date_from', 'date_to', 'lender_id', 'customer_id')
    def onchange_dates(self):
        self.invoice_ids = False
        if self.date_from and self.date_to and self.lender_id and self.customer_id:
            invoices = self.env['lending.invoice'].search([
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('lender_id', '=', self.lender_id.id),
                ('customer_id', '=', self.customer_id.id)
            ])
            return {'domain': {'invoice_ids': [('id', 'in', invoices.ids)]}}
        return {'domain': {'invoice_ids': []}}

    @api.constrains('date_from', 'date_to')
    def check_date(self):
        if self.date_from > self.date_to:
            raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin.")

    def get_invoices(self):
        """ Busco las facturas para el prestador y el rango """
        if not self.invoice_ids:
            raise ValidationError('No hay facturas del prestador {} y cliente {} para el rango de fechas seleccionado.'
                                  .format(self.lender_id.name, self.customer_id.name))
        return self.invoice_ids

    @api.multi
    def generate_report_pdf(self):
        """ Genero reporte de facturas para un prestador y un rango de fechas """
        self.get_invoices()
        res = self.env['report'].get_action(self, 'lending_invoice_report.lending_invoice_report')
        return res

    def get_total(self):
        """ Sumo el total de todas las facturas """
        invoices = self.get_invoices()
        return sum(invoice.amount_total for invoice in invoices)

    def get_period(self):
        """ Devuelvo el periodo (mes y anio) correspondiente a la fecha de inicio seleccionada en el wizard """
        date_from = fields.Date.from_string(self.date_from)
        return datetime.strftime(date_from, "%B %Y")

    def get_types_lots(self):
        """ Busco los tipos de todos los lotes de las facturas en el rango de fecha"""
        types_lots = self.get_invoices().mapped('line_ids.lending_lot_type_id')
        return "/".join(type.name.upper() for type in types_lots) if types_lots else False

    def get_debit_motive(self):
        """ Busco todos los motivos que existen en las facturas """
        debit_motives = self.get_invoices().mapped('line_ids.registry_lending_ids.debit_motive_ids')
        debit_motives |= self.env.ref('lending_invoice_report.debit_motive_invoice_difference')
        return debit_motives

    def get_debit_motive_total(self, motive):
        """ Calculo el total de debito de un motivo en todos los registros de prestaciones """
        total = 0
        if motive == self.env.ref('lending_invoice_report.debit_motive_invoice_difference'):
            invoices = self.get_invoices()
            total = sum(invoices.mapped('difference'))
        percentage = motive.percentage
        # Filtro los registros con motivos que contengan el motivo buscado
        # y que no haya un motivo con porcentaje mayor que el del motivo buscado
        registries_filtered = self.get_invoices().mapped('line_ids.registry_lending_ids').filtered(lambda x: motive in x.debit_motive_ids and not any(
            mot.percentage > percentage for mot in x.debit_motive_ids))
        for registry in registries_filtered:
            # Si existe dos motivos con el mismo porcentaje, verifico si el primero es el motivo buscado
            if registry.debit_motive_ids[0] == motive:
                total += registry.debit
        return total or False

    @staticmethod
    def _build_num_to_string(amount):
        """ Devuelvo el monto convertido a string """
        try:
            from num2words import num2words
        except Exception:
            raise ValidationError("Por favor, descargar la libreria num2words (sudo pip install num2words)")
        # Divido el monto separando los decimales para que realice correctamente la conversion
        amount_tuple = (int(str(amount).split('.')[0]),
                        int(str(amount).split('.')[1].ljust(2, '0')))
        return num2words(amount_tuple, lang='es_CO', to='currency').upper()  # Usamos es_CO porque no existe es_AR

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
