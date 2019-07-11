# coding: utf-8
##############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

import xlwt
import base64
from StringIO import StringIO
from openerp.http import Controller, route, request
from openerp.addons.web.controllers.main import serialize_exception, content_disposition


class XlsBuilder:
    def __init__(self, sheet_name, styles={}):
        """
        Inicializa el builder para su uso
        :param sheet_name: nombre de la hoja del libro
        :param styles: diccionario de estilos a utilizar en el libro (nombre y especificacion)
        """
        self.book = xlwt.Workbook()
        self.sheet = self.book.add_sheet(sheet_name)
        self.styles = {}
        for style_name, style_detail in styles.iteritems():
            if len(style_detail) == 1:
                self.styles[style_name] = xlwt.easyxf(style_detail[0])
            else:
                self.styles[style_name] = xlwt.easyxf(style_detail[0], num_format_str=style_detail[1])

    def write_cell(self, row, col, data, style):
        """
        Escribe una celda en el archivo
        :param row: numero de fila de la celda a escribir (la primera es la 1)
        :param col: numero de columna de la celda a escribir (la primera es la 1)
        :param data: dato a escribir (si empieza con = se lo analiza como formula)
        :param style: estilo a utilizar
        """
        self.sheet.write(row - 1, col - 1,
                         xlwt.Formula(data[1:]) if isinstance(data, basestring) and data.startswith('=') else data,
                         self.styles.get(style))

    def write_row(self, row, data, styles):
        """
        Escribe una fila entera comenzando por la primera columna
        :param row: numero de la fila a escribir (la primera es la 1)
        :param data: iterable de datos que se escribiran
        :param styles: estilos a utilizar (1 para toda la fila o 1 para cada celda)
        """
        for i in xrange(len(data)):
            self.write_cell(row, i + 1, data[i], styles[0] if len(styles) == 1 else styles[i])

    def get_file(self):
        """
        Genera el archivo con los datos agregados hasta el momento
        :return: archivo encodeado
        """
        file_data = StringIO()
        self.book.save(file_data)
        return base64.encodestring(file_data.getvalue())


class XlsResponse(Controller):
    @route('/web/binary/xls', type='http', auth="public")
    @serialize_exception
    def download_xls(self, debug=1, id=0, filename='', model=''):  # pragma: no cover
        """
        Descarga un documento cuando se accede a la url especificada en http route.
        :param debug: si esta o no en modo debug.
        :param int id: id del modelo que contiene el documento.
        :param filename: nombre del archivo.
        :param model: modelo que contiene el documento.
        :returns: :class:'werkzeug.wrappers.Response', descarga del archivo excel.
        """
        filecontent = base64.b64decode(request.env[model].browse(int(id)).file or '')
        return request.make_response(filecontent, [('Content-Type', 'application/excel'),
                                                   ('Content-Disposition', content_disposition(filename))])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
