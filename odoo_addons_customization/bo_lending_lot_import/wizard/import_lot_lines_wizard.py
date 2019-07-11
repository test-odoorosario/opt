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
from datetime import datetime

from openerp import models, fields
from openerp.exceptions import ValidationError


class ImportLotLinesWizard(models.TransientModel):
    _name = 'import.lot.lines.wizard'

    HEADER_HEIGHT = 1
    STARTING_ROW = HEADER_HEIGHT

    COLS = {
        'affiliate_doc_type': 0,
        'affiliate_vat': 1,
        'affiliate_name': 2,
        'practice': 3,
        'qty': 4,
        'lending': 5,
        'date': 6,
        'expenses': 7,
        'debit': 8,
        'to_pay': 9,
        'obs': 10,
    }

    file = fields.Binary(
        string="Archivo",
    )
    filename = fields.Char(
        string="Nombre de archivo",
    )

    def import_file(self):
        """
        Importo el archivo para generar lineas en el formulario
        :return: el form del active id con las lineas importadas
        """
        if not self.file:
            raise ValidationError('Debe subir un archivo para realizar la importacion.')
        book = self.open_excel_book()
        self.create_lines(self.sheet_to_array(book.sheet_by_index(0)), book.datemode)

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

    def create_lines(self, array, datemode):

        """
        Crea lineas a partir de un array con datos
        :param array: array de arrays, cada elemento posee 11 columnas (doc de afiliado, nro de afiliado, nombre y
        apellido, practica, cantidad, prestacion, fecha, gastos, debito, a pagar y observaciones)
        :param datemode: modo de fecha de Excel para conversion
        :return: los ids de las lineas creadas
        """
        active_id = self.env.context.get('active_id')
        r = self.STARTING_ROW
        error_rows = []
        ids = []

        lot = self.env['lending.lot'].browse(active_id)
        for row in array:
            try:
                code = row[self.COLS['practice']]
                description = str(row[self.COLS['lending']])
                doc_type = row[self.COLS['affiliate_doc_type']]
                vat = row[self.COLS['affiliate_vat']]
                if not (code and str(code).strip()):
                    error_rows.append("La fila {} no tiene codigo de prestacion!".format(r+1))
                if not (description and description.strip()):
                    error_rows.append("La fila {} no tiene prestacion!".format(r+1))
                if not doc_type or not str(doc_type).strip():
                    error_rows.append("La fila {} no tiene tipo de documento de afiliado!".format(r+1))
                if not vat or not str(vat).strip():
                    error_rows.append("La fila {} no tiene numero de documento de afiliado!".format(r+1))
                try:
                    vat = str(int(float(str(vat).strip())))
                except:
                    error_rows.append("La fila {} contiene el numero de documento invalido!".format(r+1))

                affiliate = self.env['lending.affiliate'].search([
                    ('document_type', '=', doc_type.lower()),
                    ('vat', '=', vat),
                ])

                if not affiliate:
                    try:
                        affiliate = self.env['lending.affiliate'].create({
                            'document_type': doc_type.lower(),
                            'vat': vat,
                            'name': str(row[self.COLS['affiliate_name']]),
                        })
                    except ValueError:
                        error_rows.append("La fila {} posee un tipo de documento de afiliado incorrecto!".format(r+1))

                from xlrd import xldate_as_tuple
                date_tuple = xldate_as_tuple(row[self.COLS['date']], datemode)
                date = datetime(*date_tuple[0:6]).date()

                r += 1
                if error_rows:
                    continue
                if type(code) == float:
                        code = str(int(code))
                else:
                    code = str(code)
                try:
                    value = float(row[self.COLS['expenses']])
                except ValueError:
                    value = 0
                try:
                    qty = float(row[self.COLS['qty']])
                except ValueError:
                    qty = 0
                code_search = self.env['lending'].with_context(date=date, lender_id=lot.lender_id.id).name_search(code)
                code_id = self.env['lending']
                if len(code_search) == 1:
                    code_id = self.env['lending'].browse(code_search[0][0])
                line = self.env['lending.registry.lending'].create({
                    'lending_id': code_id.id if code_id else False,
                    'date': date,
                    'lot_id': active_id,
                    'code': code,
                    'qty': qty,
                    'description': description,
                    'affiliate_id': affiliate.id,
                    'informed_value': value,
                })
                ids.append(line.id)
            except:
                error_rows.append("Error de tipo de campo en la fila {}!".format(r+1))

        if error_rows:
            raise ValidationError("\n".join(set(error_rows)))
        lot.update_amount_total()
        return ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
