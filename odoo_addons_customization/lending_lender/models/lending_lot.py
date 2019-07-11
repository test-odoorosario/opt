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

from openerp import models, fields, registry, api
from openerp.exceptions import ValidationError


class LendingLot(models.Model):
    _inherit = 'lending.lot'

    file = fields.Binary(
        string='Archivo a importar'
    )
    filename = fields.Char(
        string="Nombre de archivo",
    )

    def import_lines(self):
        """ Se importa el archivo seleccionado y se generan las lineas"""
        self.ensure_one()
        if not self.file:
            raise ValidationError('Debe cargar un archivo antes de importar.')
        wizard = self.env['import.lot.lines.wizard'].with_context(active_id=self.id).create({
            'file': self.file,
            'filename': self.filename,
        })
        try:
            wizard.import_file()
        except Exception as e:
            raise ValidationError(e)
        finally:
            with api.Environment.manage():
                with registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                    body = 'Archivo de importación'
                    self.with_env(new_env).sudo().message_post(
                        body=body,
                        type='comment',
                        attachments=[(self.filename, self.file)],
                        partner_ids=new_env.user
                    )
                    new_env.cr.commit()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
