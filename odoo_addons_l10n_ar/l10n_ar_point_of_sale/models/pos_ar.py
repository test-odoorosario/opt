# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from openerp.exceptions import ValidationError


class PosAr(models.Model):
    _name = 'pos.ar'

    name = fields.Char('Nombre', required=True)
    description = fields.Char('Descripcion')
    document_book_ids = fields.One2many(
        'document.book',
        'pos_ar_id',
        'Talonarios'
    )
    active = fields.Boolean('Activo', default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    prefix_quantity = fields.Integer('Cantidad de digitos prefijo', default=4)

    @api.constrains('name')
    def check_name(self):
        for pos_ar in self:
            try:
                int(pos_ar.name)
            except Exception:
                raise ValidationError('El nombre debe contener solo números enteros')
            if len(pos_ar.name) > pos_ar.prefix_quantity:
                raise ValidationError("No puede haber más dígitos que lo establecidos en la cantidad.")

    @api.constrains('prefix_quantity')
    def prefix_quantity_constraint(self):
        if any(pos.prefix_quantity <= 0 for pos in self):
            raise ValidationError("La cantidad de dígitos del prefijo debe ser mayor que 0")

    @api.multi
    def name_get(self):

        name_get = []
        name_list = super(PosAr, self).name_get()
        for name in name_list:
            pos = self.env['pos.ar'].browse(name[0])
            name_get.append((name[0], name[1].zfill(pos.prefix_quantity)))
        return name_get

    def get_pos(self, category, denomination=None, company=None):
        """
        Busca el punto de venta con mas prioridad para esa categoria y denominacion
        :param category: categoria (invoice, receipt, picking)
        :param denomination: account.denomination
        :return: Punto de venta prioritario
        """

        search_domain = [('category', '=', category)]
        if company:
            search_domain.append(('company_id', '=', company.id))
        if denomination:
            search_domain.append(('denomination_id', '=', denomination.id))

        document_book = self.env['document.book'].search(
            search_domain,
            order="sequence asc",
            limit=1
        )

        if not document_book:
            raise ValidationError('No se encontro un talonario para este tipo de documento\n'
                                  'por favor, configurar uno')

        return document_book.pos_ar_id

    _sql_constraints = [
        ('type_unique', 'unique(name, company_id)', 'Ya existe un punto de venta con ese nombre para esta empresa')
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
