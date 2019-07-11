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


class LendingRegistryLending(models.Model):
    _name = 'lending.registry.lending'
    _rec_name = 'code'
    _order = 'date'
    _inherit = ['mail.thread']

    code = fields.Char(
        string='Código',
        required=True,
        track_visibility='onchange'
    )
    description = fields.Char(
        string='Descripción',
        required=True,
    )
    lending_id = fields.Many2one(
        comodel_name='lending',
        string='Código',
        copy=False,
        track_visibility='onchange',
        domain=[('medicine', '=', False)]
    )
    medicine_id = fields.Many2one(
        comodel_name='lending',
        string='Código de medicamento',
        copy=False,
        track_visibility='onchange',
        domain=[('medicine', '=', True)]
    )
    date = fields.Date(
        string='Fecha',
        track_visibility='onchange'
    )
    lot_id = fields.Many2one(
        comodel_name='lending.lot',
        string='Lote',
        copy=False,
        required=True,
        ondelete='cascade'
    )
    lender_id = fields.Many2one(
        related='lot_id.lender_id',
        comodel_name='lending.lender',
        string='Prestador',
        readonly=True,
        store=True,
    )
    affiliate_vat = fields.Char(
        string='Documento',
        related='affiliate_id.vat',
    )
    affiliate_id = fields.Many2one(
        comodel_name='lending.affiliate',
        string='Afiliado',
        copy=False,
        required=True,
        track_visibility='onchange'
    )
    informed_value = fields.Float(
        string='Valor facturado',
        track_visibility='onchange'
    )
    rate_value = fields.Float(
        string='Valor tarifario',
        track_visibility='onchange'
    )
    debit = fields.Float(
        string='Débito',
        track_visibility='onchange'
    )
    debit_motive_ids = fields.Many2many(
        comodel_name='lending.debit.motive',
        string='Motivos de débito',
        track_visibility='onchange'
    )
    no_debit = fields.Boolean(
        string='Sin débito?',
        track_visibility='onchange'
    )
    total_to_pay = fields.Float(
        string='Total a pagar'
    )

    @api.onchange('informed_value', 'debit')
    def onchange_total_to_pay(self):
        self.total_to_pay = self.informed_value - self.debit

    @api.onchange('informed_value', 'debit_motive_ids')
    def onchange_debit(self):
        if self.debit_motive_ids and self.informed_value:
            motive_sorted = self.debit_motive_ids.sorted(lambda x: x.percentage, reverse=True)
            if motive_sorted[0].percentage > 0:
                self.update({
                    'debit': motive_sorted[0].percentage * self.informed_value / 100,
                    'total_to_pay': (motive_sorted[0].percentage * self.informed_value / 100) - self.informed_value
                })

    @api.onchange('date')
    def onchange_date(self):
        self.update({
            'lending_id': None,
            'code': None,
            'description': None,
            're_invoice_id': None,
        })
        domain = [('date', '<=', self.date)]
        if self.lot_id.invoice_id:
            domain.append(('id', '!=', self.lot_id.invoice_id.id))
        return {'domain': {'re_invoice_id': domain}}

    re_invoice_id = fields.Many2one(
        comodel_name='lending.invoice',
        string='Refactura',
        track_visibility='onchange'
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
