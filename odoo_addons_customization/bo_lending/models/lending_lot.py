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


class LendingLot(models.Model):
    _name = 'lending.lot'
    _order = 'name'
    _inherit = ['mail.thread']
    _description = 'Lote'

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    lender_id = fields.Many2one(
        comodel_name='lending.lender',
        string='Prestador',
        copy=False,
        required=True,
        track_visibility='onchange'
    )
    registry_lending_ids = fields.One2many(
        comodel_name='lending.registry.lending',
        inverse_name='lot_id',
        string='Registros de prestaciones',
        copy=False,
        track_visibility='onchange'
    )
    lending_lot_type_id = fields.Many2one(
        comodel_name='lending.lot.type',
        string='Tipo de lote',
        required=True,
        track_visibility='onchange'
    )
    amount_untaxed = fields.Float(
        string='Importe no gravado',
        compute='compute_amount',
    )
    amount_taxed = fields.Float(
        string='Importe gravado',
        compute='compute_amount',
    )
    amount_total = fields.Float(
        string='Importe total',
        compute='compute_amount',
    )
    invoice_ids = fields.Many2many(
        comodel_name='lending.invoice',
        relation='lending_invoice_lot_rel',
        column1='inv_id',
        column2='lot_id',
        string='Factura',
        track_visibility='onchange'
    )
    invoice_id = fields.Many2one(
        comodel_name='lending.invoice',
        string='Factura',
        compute='set_invoice_id',
        store=True,
        track_visibility='onchange'
    )
    revision_done = fields.Boolean(
        string="Revisión finalizada",
    )

    @api.depends('invoice_ids')
    def set_invoice_id(self):
        for lot in self:
            lot.invoice_id = lot.invoice_ids[0].id if lot.invoice_ids else None

    @api.onchange('registry_lending_ids')
    def compute_amount(self):
        for lot in self:
            lot.amount_untaxed = sum(lot.registry_lending_ids.filtered(lambda l: not l.affiliate_id.taxed).mapped('informed_value'))
            lot.amount_taxed = sum(lot.registry_lending_ids.filtered(lambda l: l.affiliate_id.taxed).mapped('informed_value'))
            lot.amount_total = lot.amount_untaxed + lot.amount_taxed


class LendingLotState(models.Model):
    _inherit = 'lending.lot'

    state = fields.Selection(
        string='Estado',
        selection=[('in_progress', 'En proceso'), ('done', 'Finalizado')],
        default='in_progress'
    )

    def finish_lot(self):
        """ Cambio de estado de lote a finalizado"""
        for lot in self:
            if lot.check_lines():
                lot.update({'state': 'done'})
            else:
                raise ValidationError('Aun quedan lineas sin revisar.')

    def cancel_lot(self):
        """ Cambio de estado de lote a en progreso"""
        self.update({'state': 'in_progress'})

    def check_lines(self):
        """ Verificamos que todas las prestaciones esten revisadas"""
        if not self.revision_done:
            if any(not l.debit_motive_ids and not l.no_debit for l in self.registry_lending_ids):
                return False
        return True

    def unlink(self):
        """ Se redefine la eliminacion de lote"""
        for lot in self:
            if lot.state in ['done']:
                raise ValidationError('No se puede eliminar un lote finalizado')
            return super(LendingLotState, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
