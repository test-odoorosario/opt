# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import models, fields
from openerp.exceptions import ValidationError
from datetime import datetime
from .. import xls


class LendingLot(models.Model):
    _inherit = 'lending.lot'

    file = fields.Binary(string="Archivo")

    def debit_report(self):
        """
        Genera un archivo XLS con los datos de todos los debitos del lote
        :return: URL de descarga del archivo
        """
        self.ensure_one()
        debit_registry_lendings = self.registry_lending_ids.filtered(lambda l: l.debit)
        if not debit_registry_lendings:
            raise ValidationError("No hay ningun registro con debito")

        styles = {
            'regular': ['align: horiz left;'],
            'bold': ['font: bold on; align: horiz left;'],
            'bold_underline': ['font: bold on, underline on; align: horiz left;'],
            'date_regular': ['align: horiz left;', 'dd/mm/yyyy'],
            'money_regular': ['align: horiz left;', '$0.00'],
            'money_bold': ['font: bold on; align: horiz left;', '$0.00'],
        }
        builder = xls.XlsBuilder("Debitos", styles)

        builder.write_cell(1, 1, "DEBITOS DE {}".format(self.name), 'bold_underline')
        header = ["Afiliado", "Tipo doc", "Nro doc", "Codigo", "Descripcion", "Fecha",
                  "Valor informado", "Valor tarifario", "Debito", "A pagar", "Observaciones"]
        builder.write_row(3, header, ['bold'])

        row = 4
        for line in debit_registry_lendings:
            builder.write_cell(row, 1, line.affiliate_id.name, 'regular')
            builder.write_cell(row, 2, line.affiliate_id.document_type.upper(), 'regular')
            builder.write_cell(row, 3, line.affiliate_id.vat, 'regular')
            builder.write_cell(row, 4, line.code, 'regular')
            builder.write_cell(row, 5, line.description, 'regular')
            builder.write_cell(row, 6, datetime.strptime(line.date, "%Y-%m-%d") if line.date else '', 'date_regular')
            builder.write_cell(row, 7, line.informed_value, 'money_regular')
            builder.write_cell(row, 8, line.rate_value, 'money_regular')
            builder.write_cell(row, 9, line.debit, 'money_regular')
            builder.write_cell(row, 10, line.total_to_pay, 'money_regular')
            builder.write_cell(row, 11, line.observations or '', 'regular')
            row += 1
        builder.write_cell(row, 1, "TOTALES", 'bold')
        builder.write_cell(row, 7, sum(self.registry_lending_ids.mapped('informed_value')), 'money_bold')
        builder.write_cell(row, 8, sum(self.registry_lending_ids.mapped('rate_value')), 'money_bold')
        builder.write_cell(row, 9, sum(self.registry_lending_ids.mapped('debit')), 'money_bold')
        builder.write_cell(row, 10, sum(self.registry_lending_ids.mapped('total_to_pay')), 'money_bold')
        self.file = builder.get_file()

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/xls?id=%s&filename=%s&model=%s' % (self.id, 'Debitos.xls', 'lending.lot'),
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
