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


class LendingRate(models.Model):
    _name = 'lending.rate'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Nombre',
        required=True
    )
    date = fields.Date(
        string='Fecha',
        default=fields.Date.context_today,
        required=True,
        track_visibility='onchange'
    )
    end_date = fields.Date(
        string='Fecha fin',
        track_visibility='onchange'
    )
    qty_expiration_days = fields.Integer(
        string='Días de expiración',
        required=True,
        track_visibility='onchange'
    )
    lender_id = fields.Many2one(
        comodel_name='lending.lender',
        string='Prestador',
        required=True,
        track_visibility='onchange'
    )
    customer_id = fields.Many2one(
        comodel_name='lending.customer',
        required=True,
        string='Cliente',
        track_visibility='onchange'
    )
    line_ids = fields.One2many(
        comodel_name='lending.rate.line',
        inverse_name='rate_id',
        string='Prestaciones',
        track_visibility='onchange'
    )
    qty_liquidation_days = fields.Integer(
        string='Días de liquidación',
        required=True,
        track_visibility='onchange'
    )

    @api.constrains('qty_liquidation_days', 'qty_expiration_days')
    def check_quantities(self):
        if any(r.qty_liquidation_days < 0 or r.qty_expiration_days < 0 for r in self):
            raise ValidationError("Las cantidades de días no pueden ser números negativos.")

    def _domain_lender(self):
        """ Busco los prestadores segun el cliente y devuelvo el dominio para el campo"""
        ids = self.customer_id.lender_ids.ids + self.customer_id.mapped('lender_ids.child_ids').ids
        return {'domain': {'lender_id': [('id', 'in', ids)]}}

    @api.onchange('customer_id')
    def onchange_customer(self):
        self.lender_id = False
        return self._domain_lender()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
