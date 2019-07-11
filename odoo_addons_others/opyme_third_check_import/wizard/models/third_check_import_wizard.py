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

import datetime
from openerp import models, fields, api
from openerp.exceptions import Warning


class ThirdCheckImportWizard(models.TransientModel):
    _name = 'third.check.import.wizard'

    HEADER_HEIGHT = 1
    STARTING_ROW = HEADER_HEIGHT + 1

    COLS = {
        'name': 0,
        'issue_date': 1,
        'payment_date': 2,
        'payment_type': 3,
        'bic': 4,
        'amount': 5,
    }

    PAYMENT_TYPES = {
        'comun': 'common',
        'diferido': 'postdated',
    }

    file = fields.Binary(
        string="Archivo",
        filters='*.xlsx,*.XLSX',
        required=True,
    )

    filename = fields.Char(
        string="Nombre de archivo",
    )

    @api.multi
    def import_file(self):
        """
        Importo el archivo cargado en el formulario (uso api.multi para devolver una vista despues)
        :return: una tree (con form) que muestra los cheques creados
        """
        book = self.open_excel_book()
        ids = self.create_checks(self.sheet_to_array(book.sheet_by_index(0)), book.datemode)
        return {
            'name': 'Cheques importados',
            'res_model': 'account.third.check',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', ids)],
            'views': [[False, "tree"], [False, "form"]],
        }

    def create_checks(self, array, datemode):
        """
        Crea cheques a partir de un array con datos
        :param array: array de arrays, cada elemento posee 6 columnas (numero de cheque, fechas de emision y pago, tipo
        de pago, banco e importe)
        :return: los ids de los cheques creados
        """
        import xlrd
        third_check_proxy = self.env['account.third.check']
        bank_proxy = self.env['res.bank']
        r = self.STARTING_ROW
        ids = []
        error_rows = []
        for row in array:
            try:
                name = str(row[self.COLS['name']])
                issue_date_tuple = xlrd.xldate_as_tuple(row[self.COLS['issue_date']], datemode)
                issue_date = datetime.datetime(*issue_date_tuple[0:6]).date()
                payment_date_tuple = xlrd.xldate_as_tuple(row[self.COLS['payment_date']], datemode)
                payment_date = datetime.datetime(*payment_date_tuple[0:6]).date()
                payment_type = self.PAYMENT_TYPES.get(row[self.COLS['payment_type']].lower())
                bank_id = bank_proxy.search([('bic', '=', str(row[self.COLS['bic']]))])
                amount = float(row[self.COLS['amount']])
                if name and issue_date and payment_date and payment_type and bank_id:
                    if not error_rows:
                        check = third_check_proxy.create({
                            'name': name,
                            'issue_date': issue_date,
                            'payment_date': payment_date,
                            'payment_type': payment_type,
                            'bank_id': bank_id.id,
                            'amount': amount,
                            'currency_id': self.env.ref('base.ARS').id,
                            'state': 'wallet',
                        })
                        ids.append(check.id)
                else:
                    error_rows.append(r)
            except:
                error_rows.append(r)
            r += 1
        if error_rows:
            error_rows_str = str(error_rows)[1:-1]  # para no mostrar los corchetes
            raise Warning("ERROR! los siguientes numeros de fila no poseen datos validos: \n{}".format(error_rows_str))
        return ids

    def open_excel_book(self):
        """
        Guarda el archivo especificado en el campo en una carpeta temporal y lo abre.
        :return: la primer hoja del archivo de Excel subido, abierta.
        """
        if self.filename.split(".")[-1].lower() != "xlsx":
            raise Warning('Error\nDebe utilizar un archivo xlsx (Excel 2007 o superior).')
        try:
            import xlrd
        except:
            raise Warning('Error\nEl modulo xlrd no esta instalado.')
        try:
            file_path = "/tmp/" + self.filename
            tmp_file = open(file_path, "wb")
            tmp_file.write(base64.b64decode(self.file))
            tmp_file.close()
        except:
            raise Warning('Error\nEl archivo elegido no es valido.')
        try:
            return xlrd.open_workbook(file_path)
        except:
            raise Warning('Error\nEl archivo elegido no es valido.')

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
                # Si el dato leido es un float con decimal .0, lo convierte a int
                try:
                    if col.is_integer():
                        col = int(col)
                except:
                    pass
                row.append(col)
            values.append(row)
        return values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
