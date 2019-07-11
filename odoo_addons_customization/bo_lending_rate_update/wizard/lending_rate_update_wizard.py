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


class LendingRateUpdateWizard(models.TransientModel):
    _name = 'lending.rate.update.wizard'

    def _get_prev_rate(self):
        return self.env['lending.rate'].browse(self.env.context.get('active_id'))

    def _get_name(self):
        return self._get_prev_rate().name

    prev_rate_id = fields.Many2one(
        comodel_name="lending.rate",
        string="Tarifario anterior",
        default=_get_prev_rate,
    )

    name = fields.Char(
        string="Nuevo nombre",
        default=_get_name,
        required=True,
    )

    global_percentage = fields.Float(
        string="Porcentaje global",
    )

    line_ids = fields.One2many(
        comodel_name="lending.rate.update.line.wizard",
        inverse_name='wizard_id',
        string="Lineas",
    )

    @api.model
    def create(self, vals):
        """
        Redefino el create porque al apretar el boton se crea el wizard con id y pierdo la referencia a las lineas
        :param vals: valores de la creacion
        :return: objeto creado
        """
        res = super(LendingRateUpdateWizard, self).create(vals)
        if vals.get('line_ids'):
            update_line_ids = [val[1] for val in vals['line_ids']]
            self.env['lending.rate.update.line.wizard'].browse(update_line_ids).write({'wizard_id': res.id})
        return res

    @api.constrains('line_ids')
    def check_lines(self):
        """
        Valido que no haya lineas repetidas
        """
        if len(self.line_ids) > len(self.line_ids.mapped('lending_id')):
            raise ValidationError("Existen lineas con codigo repetido")

    def create_rate(self):
        """
        Crea un tarifario nuevo con los valores de lineas actualizados y lo muestra
        :return: vista form del tarifario nuevo
        """
        rate = self.env['lending.rate'].create({
            'name': self.name,
            'qty_expiration_days': self.prev_rate_id.qty_expiration_days,
            'lender_id': self.prev_rate_id.lender_id.id,
            'customer_id': self.prev_rate_id.customer_id.id,
        })

        new_line_ids = []
        for line in self.prev_rate_id.line_ids:
            update_line = self.line_ids.filtered(lambda l: l.lending_id == line.lending_id)
            value_proportion = (1 + (update_line.variation_percentage or self.global_percentage) / 100)
            new_line_ids.append(
                self.env['lending.rate.line'].create({
                    'lending_id': line.lending_id.id,
                    'code_range': line.code_range,
                    'calculation_type': line.calculation_type,
                    'value': line.value * value_proportion,
                    'lender_code': line.lender_code,
                    'description': line.description,
                    'nomenclator_id': line.nomenclator_id.id if line.nomenclator_id else False,
                    'no_agreed': line.no_agreed,
                }).id
            )
        rate.line_ids = [(6, 0, new_line_ids)]

        return {
            'name': "Tarifario actualizado",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'lending.rate',
            'res_id': rate.id,
            'type': 'ir.actions.act_window',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
