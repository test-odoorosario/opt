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


class LendingLender(models.Model):
    _name = 'lending.lender'
    _order = 'code'

    code = fields.Char(
        string='Codigo',
        required=True,
    )
    name = fields.Char(
        string='Nombre',
        required=True,
    )
    plan_ids = fields.Many2many(
        comodel_name='lending.plan.agreement',
        string='Planes',
        copy=False,
    )
    rate_ids = fields.One2many(
        comodel_name='lending.rate',
        inverse_name='lender_id',
        string='Tarifarios',
        copy=False,
    )
    lot_ids = fields.One2many(
        comodel_name='lending.lot',
        inverse_name='lender_id',
        string='Lotes',
        copy=False,
    )
    is_parent = fields.Boolean(
        string='Tiene prestadores?',
    )
    parent_id = fields.Many2one(
        comodel_name='lending.lender',
        string='Prestador padre'
    )
    child_ids = fields.Many2many(
        comodel_name='lending.lender',
        relation='child_lender_to_lender_rel',
        column1='child_id',
        column2='parent_id',
        string='Prestadores',
        domain=[('is_parent', '=', False)]
    )
    category_ids = fields.Many2many(
        comodel_name='lending.category',
        string='Categorias',
        copy=False,
    )

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, "[{}] {}".format(record.code, record.name)))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            return self.search(['|', ('name', operator, name), ('code', operator, name)] + args, limit=limit).name_get()
        return super(LendingLender, self).name_search(name, args, operator, limit)

    @api.depends('line_ids')
    def _compute_amount(self):
        for invoice in self:
            total = sum(line.amount_total for line in invoice.line_ids)
            invoice.amount_total = total

    def _get_parent(self):
        for lender in self:
            parent = self.env['lending.lender'].search([('child_ids', 'in', lender.id)])
            if parent:
                lender.is_child = True

    is_child = fields.Boolean(
        string='Tiene padre?',
        compute=_get_parent,
    )

    @api.onchange('is_parent')
    def onchange_is_parent(self):
        self.child_ids = False

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Ya existe un prestador con este mismo codigo.')
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
