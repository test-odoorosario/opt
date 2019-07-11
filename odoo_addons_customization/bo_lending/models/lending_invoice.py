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
from dateutil.relativedelta import relativedelta
from datetime import datetime


class LendingInvoice(models.Model):
    _name = 'lending.invoice'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Numero de factura',
        required=True,
        copy=False,
    )
    date = fields.Date(
        string='Fecha de factura',
        required=True,
        default=fields.Date.context_today,
        track_visibility='onchange'
    )
    amount_untaxed = fields.Float(
        string='No gravado',
    )
    amount_taxed = fields.Float(
        string='Gravado',
    )
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount',
    )
    amount_total_lots = fields.Float(
        string='Total de lotes',
        compute='_compute_amount',
    )
    gross_income_amount = fields.Float(
        string="IIBB",
    )
    vat_amount = fields.Float(
        string="IVA",
    )
    customer_id = fields.Many2one(
        comodel_name='lending.customer',
        string='Cliente',
        required=True,
        copy=False,
        track_visibility='onchange'
    )
    lender_id = fields.Many2one(
        comodel_name='lending.lender',
        string='Prestador',
        required=True,
        copy=False,
        track_visibility='onchange'
    )
    line_ids = fields.Many2many(
        comodel_name='lending.lot',
        relation='lending_invoice_lot_rel',
        column2='inv_id',
        column1='lot_id',
        string='Lotes',
        copy=False,
        track_visibility='onchange'
    )
    entry_date = fields.Date(
        string="Fecha de ingreso",
    )
    due_date = fields.Date(
        string="Fecha de vencimiento"
    )
    debit_motive_id = fields.Many2one(
        comodel_name='lending.debit.motive',
        string="Motivo de débito",
    )

    @api.onchange('entry_date', 'lender_id')
    def onchange_entry_date(self):
        """ Al cambiar la fecha se calcula la fecha de vencimiento en base a la configuracion del tarifario activo"""
        if self.lender_id and self.entry_date:
            rate = self.search_active_rate(self.lender_id)
            if not rate:
                raise ValidationError("No hay ningun tarifario activo para el prestador seleccionado.")
            qty = rate.qty_liquidation_days
            self.due_date = (datetime.strptime(self.entry_date, '%Y-%m-%d') + relativedelta(days=qty))

    def search_active_rate(self, lender):
        rate = self.env['lending.rate'].search([
            ('lender_id', '=', lender.id),
            ('end_date', '=', False)
        ], limit=1, order='date desc')
        return rate

    def _domain_lender(self):
        """ Busco los prestadores segun el cliente y devuelvo el dominio para el campo"""
        ids = self.customer_id.lender_ids.ids + self.customer_id.mapped('lender_ids.child_ids').ids
        return {'domain': {'lender_id': [('id', 'in', ids)]}}

    @api.onchange('customer_id')
    def onchange_customer(self):
        self.lender_id = False
        return self._domain_lender()

    @api.constrains('entry_date', 'due_date')
    def check_dates(self):
        if any(r.entry_date > r.due_date for r in self):
            raise ValidationError("La fecha de ingreso no puede ser mayor a la de vencimiento")

    def _get_amount_total(self):
        self.ensure_one()
        return sum([self.amount_untaxed, self.amount_taxed, self.gross_income_amount, self.vat_amount])

    @api.depends('amount_untaxed', 'amount_taxed', 'gross_income_amount', 'vat_amount', 'line_ids')
    def _compute_amount(self):
        for invoice in self:
            invoice.amount_total = invoice._get_amount_total()
            invoice.amount_total_lots = sum(line.amount_total for line in invoice.line_ids)

    @api.constrains('amount_untaxed', 'amount_taxed', 'gross_income_amount', 'vat_amount')
    def check_amounts(self):
        for r in self:
            if any(v < 0 for v in [r.amount_untaxed, r.amount_taxed, r.gross_income_amount, r.vat_amount]):
                raise ValidationError("Los importes no pueden ser negativos")
            if not r._get_amount_total():
                raise ValidationError("El importe total no puede ser 0")

    _sql_constraints = [
        ('name_lender_unique', 'unique(name, lender_id)', 'Ya existe una factura con ese número y prestador')
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
