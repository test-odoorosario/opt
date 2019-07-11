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


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_lender = fields.Boolean(
        string='Prestador?'
    )
    customer_id = fields.Many2one(
        comodel_name='lending.customer',
        string='Cliente'
    )
    lender_ids = fields.Many2many(
        comodel_name='lending.lender',
        compute='get_lender'
    )

    @api.depends('customer_id')
    def get_lender(self):
        for user in self:
            if user.customer_id:
                lender_ids = user.customer_id.lender_ids + user.customer_id.mapped('lender_ids.child_ids')
                user.lender_ids = lender_ids
            else:
                user.lender_ids = False

    lender_id = fields.Many2one(
        comodel_name='lending.lender',
        string='Prestador',
    )
    
    def _domain_lender(self):
        """ Busco los prestadores segun el cliente y devuelvo el dominio para el campo"""
        ids = self.customer_id.lender_ids.ids + self.customer_id.mapped('lender_ids.child_ids').ids
        return {'domain': {'lender_id': [('id', 'in', ids)]}}

    @api.onchange('customer_id')
    def onchange_customer(self):
        self.lender_id = False
        return self._domain_lender()

    @api.onchange('is_lender')
    def onchange_lender(self):
        self.update({
            'customer_id': False,
            'lender_id': False
    })

    @api.onchange('lender_id')
    def onchange_lender_id(self):
        rule_lot = self.env.ref('lending_lender.lending_lot_lender_rule')
        rule_lender = self.env.ref('lending_lender.lending_lender_lender_rule')
        rule_invoice = self.env.ref('lending_lender.lending_invoice_lender_rule')
        rule_customer = self.env.ref('lending_lender.lending_customer_lender_rule')
        (rule_lot | rule_lender | rule_invoice | rule_customer).clear_caches()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
