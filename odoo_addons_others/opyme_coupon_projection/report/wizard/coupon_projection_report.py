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
from datetime import datetime
from openerp import models, fields, api, http
import StringIO
import base64
import xlwt
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception, content_disposition


class CouponProjectionReport(models.TransientModel):
    _name = 'coupon.projection.report'

    report = fields.Binary('Reporte')

    def search_coupons(self):
        """
        Busco todos los cupones publicados y que contengan calculado el monto estimado y
        la fecha estimada.
        :return: recordset de cupones
        """
        coupons = self.env['bank.card.coupon'].search([
            ('state', '=', 'posted'),
            ('estimated_amount', '!=', False),
            ('estimated_date', '!=', False),
        ])
        return coupons

    def search_account_banks(self, coupons):
        """
        Busco todas las cuentas bancarias para los cupones filtrados
        :param coupons: recordset de cupones
        :return: Recordset de bancos
        """
        # Ordeno alfabeticamente los bancos
        sorted_bank = coupons.mapped(
            'bank_card_id.bank_account_id'
        ).sorted(lambda x: x.name)
        return sorted_bank

    @api.multi
    def generate_report_xls(self):
        """
        Busco los cupones con filtros requeridos, y se lo pasa al reporte.
        :return: accion que levanta el reporte.
        """
        # Traemos los recordset
        coupons = self.search_coupons()
        banks = self.search_account_banks(coupons)

        # Preparamos el workbook y la hoja
        wbk = xlwt.Workbook()
        # STYLES
        style_bank = xlwt.easyxf(
            'font: bold on,height 240,color_index 0X36;'
            'align: horiz center;'
            'pattern: pattern solid, fore_colour 0x16;'
            'borders: left_color 0X36, right_color 0X36, top_color 0X36,'
            ' bottom_color 0X36, left thin, right thin, top thin, bottom thin;'
        )
        style_header = xlwt.easyxf(
            'font: bold on, height 210, color_index 0X36;'
            'align: horiz left;'
            'borders: bottom_color 0X36, bottom thin;'
        )
        style_info = xlwt.easyxf(
            'font: height 180, color_index 0x08;'
            'align: horiz left;'
        )
        name = 'Proyeccion de cupones'
        sheet = wbk.add_sheet(name)
        # Ancho de las columnas
        sheet.col(0).width = 6000
        sheet.col(1).width = 6000
        sheet.col(2).width = 6000

        row_number = 0
        col_number = 0
        # Detalles
        for bank in banks:
            # Escribimos el nombre del banco
            sheet.write_merge(row_number, row_number, col_number, col_number + 2, bank.name,
                              style_bank)
            row_number += 1
            # Escribo el encabezado por banco
            sheet.write(row_number, col_number, 'Fecha estimada', style_header)
            sheet.write(row_number, col_number + 1, 'Monto', style_header)
            sheet.write(row_number, col_number + 2, 'Acumulado', style_header)
            row_number += 1
            # Traigo los cupones para ese banco y los ordeno por la fecha estimada
            coupons_of_bank = coupons.filtered(
                lambda x: x.bank_card_id.bank_account_id.name == bank.name
            ).sorted(lambda x: x.estimated_date)
            total_acum = 0
            for coupon in coupons_of_bank:
                total_acum += coupon.estimated_amount
                sheet.write(row_number, col_number, datetime.strptime(
                    coupon.estimated_date, '%Y-%m-%d').strftime('%d/%m/%Y'), style_info)
                sheet.write(row_number, col_number + 1, coupon.estimated_amount, style_info)
                sheet.write(row_number, col_number + 2, total_acum, style_info)
                row_number += 1

        # Exportamos y guardamos
        file_data = StringIO.StringIO()
        wbk.save(file_data)
        out = base64.encodestring(file_data.getvalue())
        self.report = out

        filename = 'ProjeccionDeCupones'

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_coupon_projection?wizard_id=%s&filename=%s' % (self.id, filename + '.xls'),
            'target': 'new',
        }


class CouponProjectionReportRoute(http.Controller):
    @http.route('/web/binary/download_coupon_projection', type='http', auth="public")
    @serialize_exception
    def download_coupon_projection(self, debug=1, wizard_id=0, filename=''):
        """ Descarga un documento cuando se accede a la url especificada en http route.
        :param debug: Si esta o no en modo debug.
        :param int wizard_id: Id del modelo que contiene el documento.
        :param filename: Nombre del archivo.
        :returns: :class:`werkzeug.wrappers.Response`, descarga del archivo excel.
        """
        filecontent = base64.b64decode(request.env['coupon.projection.report'].browse(int(wizard_id)).report or '')
        return request.make_response(filecontent, [('Content-Type', 'application/excel'),
                                                   ('Content-Disposition', content_disposition(filename))])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
