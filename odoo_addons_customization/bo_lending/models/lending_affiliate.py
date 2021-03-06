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


class LendingAffiliate(models.Model):
    _name = 'lending.affiliate'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    document_type = fields.Selection(
        selection=[('dni', 'DNI'), ('cuit', 'CUIT'), ('cuil', 'CUIL')],
        string='Tipo de documento',
        required=True
    )
    vat = fields.Char(
        string='Documento',
        required=True
    )
    plan_id = fields.Many2one(
        comodel_name='lending.plan.agreement',
        string='Plan/Convenio',
        copy=False
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    entry_date = fields.Date(
        string='Fecha de alta',
    )
    exit_date = fields.Date(
        string='Fecha de baja',
    )
    taxed = fields.Boolean(
        string='Gravado'
    )

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            return self.search(['|', ('name', operator, name), ('vat', operator, name)] + args, limit=limit).name_get()
        return super(LendingAffiliate, self).name_search(name, args, operator, limit)

    _sql_constraints = [
        ('number_uniq', 'unique (document_type, vat)', 'Ya existe un afiliado con este tipo y numero de documento.')
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
