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


class Lending(models.Model):
    _name = 'lending'
    _rec_name = 'code'
    _order = 'code'

    code = fields.Char(
        string='Codigo',
        required=True
    )
    name = fields.Char(
        string='Nombre',
        required=True
    )
    description = fields.Text(
        string='Descripcion'
    )
    module = fields.Boolean(
        string='Modulo'
    )
    lending_ids = fields.One2many(
        comodel_name='lending.module',
        inverse_name='parent_lending_id',
        string='Prestaciones',
        copy=False
    )
    has_coinsurance = fields.Boolean(
        string="Lleva coseguro?",
    )
    medicine = fields.Boolean(
        string='Medicamento'
    )

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, "[{}] {}".format(record.code, record.name)))
        return res
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        rate = self.env['lending.rate'].search([
            ('date', '<=', self.env.context.get('date')),
            ('end_date', '=', False),
            ('lender_id', '=', self.env.context.get('lender_id'))
        ], limit=1, order='date desc')
        lendings = self.env['lending']
        new_id = 0
        for line in rate.line_ids:
            if line.code_range:
                list_range = range(int(line.lending_id.code), int(line.code_range) + 1)
                list_range_str = [str(item).zfill(6) for item in list_range]
                lendings |= self.search([('code', 'in', list_range_str)])
            else:
                lendings |= self.search([('id', '=', line.lending_id.id)])
                if name and name == line.lender_code:
                    new_id = line.lending_id.id
        if name:
            if lendings:
                return self.search(
                    [('id', 'in', lendings.ids), '|', ('name', operator, name), ('code', operator, name)] + args, limit=limit).name_get() \
                    if not new_id else self.with_context(new_value=name).search([('id', '=', new_id)] + args, limit=limit).name_get()
            else:
                return self.search(['|', ('name', operator, name), ('code', operator, name)] + args, limit=limit).name_get()
        if not name and (self.env.context.get('date') and self.env.context.get('lender_id')):
            return self.search(
                [
                    ('id', 'in', lendings.ids), '|', ('name', operator, name), ('code', operator, name)
                ] + args, limit=limit).name_get()
        return super(Lending, self).name_search(name, args, operator, limit)

    @api.onchange('module')
    def onchange_module(self):
        self.lending_ids = False

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Ya existe una prestacion con este mismo codigo.')
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
