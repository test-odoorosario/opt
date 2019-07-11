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
import base64
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class ImportNomenclatorLineWizard(models.TransientModel):
    _name = 'import.nomenclator.line.wizard'

    HEADER_HEIGHT = 1
    STARTING_ROW = HEADER_HEIGHT + 1

    COLS = {
        'code': 0,
        'description': 1,
        'unit': 2,
        'expense_type_code': 3,
        'unit_expense': 4,
        'amount_total': 5,
        'unit_type_code': 6,
    }

    file = fields.Binary(
        string="Archivo",
    )
    filename = fields.Char(
        string="Nombre de archivo",
    )

    @api.multi
    def import_file(self):
        """
        Importo el archivo para generar lineas en el formulario
        :return: el form del active id con las lineas importadas
        """
        if not self.file:
            raise ValidationError('Debe subir un archivo para realizar la importacion.')
        book = self.open_excel_book()
        self.create_lines(self.sheet_to_array(book.sheet_by_index(0)))

    def open_excel_book(self):
        """
        Guarda el archivo especificado en el campo en una carpeta temporal y lo abre.
        :return: la primer hoja del archivo de Excel subido, abierta.
        """
        if self.filename.split(".")[-1].lower() not in ["xlsx", "xls"]:
            raise ValidationError('Error\nDebe utilizar un archivo xlsx o xls.')
        try:
            import xlrd
        except:
            raise ValidationError('Error\nEl modulo xlrd no esta instalado.')
        try:
            file_path = "/tmp/" + self.filename
            tmp_file = open(file_path, "wb")
            tmp_file.write(base64.b64decode(self.file))
            tmp_file.close()
        except:
            raise ValidationError('Error\nEl archivo elegido no es valido.')
        try:
            return xlrd.open_workbook(file_path)
        except:
            raise ValidationError('Error\nEl archivo elegido no es valido.')

    def sheet_to_array(self, sheet):
        """
        Lee todos los datos de una hoja de Excel.
        :param sheet: la hoja a leer
        :return: un array con todas las filas y columnas.
        """
        values = []
        for r in range(sheet.nrows - self.HEADER_HEIGHT):
            row = []
            for c in range(sheet.ncols):
                col = sheet.cell(r + self.HEADER_HEIGHT, c).value
                row.append(col)
            values.append(row)
        return values

    def create_lines(self, array):
        """
        Crea lineas a partir de un array con datos
        :param array: array de arrays, cada elemento posee 5 columnas (codigo, descripcion de cada linea, 
        unidades, tipo de gasto, unidades de gasto)
        :return: los ids de las lineas creadas
        """
        active_id = self.env.context.get('active_id')
        r = self.STARTING_ROW
        error_rows = []
        lending_proxy = self.env['lending']
        ids = []
        for row in array:
            if not (str(row[self.COLS['code']]) and str(row[self.COLS['code']]).strip()):
                continue
            if not str(row[self.COLS['description']]) or str(row[self.COLS['description']]) == '':
                continue
            code = str(row[self.COLS['code']]).replace('.', '').replace(' ', '').strip()
            if len(code) != 6:
                continue
            try:
                expense = self.env['lending.expense.type'].search([
                        ('code', '=', str(row[self.COLS['expense_type_code']]) or '')
                    ])
                unit_expense_type = self.env['lending.expense.type'].search([
                    ('code', '=', str(row[self.COLS['unit_type_code']]) or '')
                ])
                expense_id = expense.id if expense else False
                unit_expense_type_id = unit_expense_type.id if unit_expense_type else False

                try:
                    unit = float(row[self.COLS['unit']])
                except ValueError:
                    unit = 0
                try:
                    unit_expense = float(row[self.COLS['unit_expense']])
                except ValueError:
                    unit_expense = 0
                try:
                    amount = float(row[self.COLS['amount_total']])
                except ValueError:
                    amount = 0
                description_line = str(row[self.COLS['description']])
                lending = lending_proxy.search([('code', '=', str(code))], limit=1)
                # Creo la linea del nomenclador, si no existe la prestacion la creo
                line_exists = self.env['lending.nomenclator.line'].search([
                    ('code', '=', code),
                    ('nomenclator_id', '=', active_id)
                ])
                if not line_exists:
                    line = self.env['lending.nomenclator.line'].create({
                        'nomenclator_id': active_id,
                        'lending_id': lending.id if lending else self.create_lending(code, description_line).id,
                        'unit': unit,
                        'unit_expense': unit_expense,
                        'expense_type_id': expense_id,
                        'unit_type_id': unit_expense_type_id,
                        'amount': amount
                    })
                    ids.append(line.id)
            except:
                error_rows.append("Error de tipo de campo en la fila {}!". format(r))
            r += 1
        if error_rows:
            raise ValidationError("\n".join(set(error_rows)))
        return ids

    def create_lending(self, code, name):
        """ Creo una prestacion con codigo y nombre"""
        return self.env['lending'].create({
            'code': code,
            'name': name
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
