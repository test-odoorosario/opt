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

from openerp import models, fields
from openerp.exceptions import ValidationError
import locale
locale.setlocale(locale.LC_ALL, '')


class PrintCheckConfiguration(models.Model):

    _name = 'print.check.configuration'

    name = fields.Char('Nombre', default='Configuracion de impresion')
    vertical = fields.Boolean('Vertical?')
    vertical_displacement = fields.Float('Desplazamiento vertical')

    amount_x = fields.Float('Importe X')
    amount_y = fields.Float('Importe Y')

    issue_date_y = fields.Float('Fecha de emision Y')
    issue_date_day_x = fields.Float('Fecha de emision dia X')
    issue_date_month_x = fields.Float('Fecha de emision dia X')
    issue_date_year_x = fields.Float('Fecha de emision dia X')

    payment_date_y = fields.Float('Fecha de pago Y')
    payment_date_day_x = fields.Float('Fecha de pago dia X')
    payment_date_month_x = fields.Float('Fecha de pago dia X')
    payment_date_year_x = fields.Float('Fecha de pago dia X')

    partner_1_y = fields.Float('Partner 1 Y')
    partner_1_x = fields.Float('Partner 1 X')
    partner_characters = fields.Integer('Caracteres')
    two_partner_lines = fields.Boolean('Otra linea?')
    partner_2_y = fields.Float('Partner 2 Y')
    partner_2_x = fields.Float('Partner 2 X')

    amount_text_1_y = fields.Float('Importe texto 1 Y')
    amount_text_1_x = fields.Float('Importe texto 1 X')
    amount_characters = fields.Integer('Caracteres')
    amount_text_2_y = fields.Float('Importe texto 2 Y')
    amount_text_2_x = fields.Float('Importe texto 2 X')

    def get_raw_html(self, check):
        """
        Construye un HTML utilizando las medidas configuradas y los datos del cheque
        :param check: Diccionario con los valores del cheque
        :return: HTML con las posiciones y los datos del cheque
        """

        check = self._build_check_dic(check)
        issue_date = fields.Date.from_string(check.get('issue_date'))
        partner_1, partner_2 = self.split_text(check.get('partner'), self.partner_characters)
        amount_text_1, amount_text_2 = self.split_text(check.get('amount_text'), self.amount_characters)

        # Rotacion si se desea imprimir vertical
        if self.vertical:
            vertical_configuration = """position: absolute; left: {size}cm; -webkit-transform: rotate(90deg);transform: rotate(90deg);""".format(
                size=self.vertical_displacement
            )
        else:
            vertical_configuration = ''

        if check.get('postdated'):
            payment_date = fields.Date.from_string(check.get('payment_date'))
            payment_date_data = """
                <span style="text-align:center;position: absolute;left:{payment_date_day_x}cm;top:{payment_date_y}cm">{payment_date_day}</span>
                <span style="text-align:center;width:3.1cm;position: absolute;left:{payment_date_month_x}cm;top:{payment_date_y}cm">{payment_date_month}</span>
                <span style="text-align:center;position: absolute;left:{payment_date_year_x}cm;top:{payment_date_y}cm">{payment_date_year}</span>
            """.format(
                payment_date_y=self.payment_date_y,
                payment_date_day_x=self.payment_date_day_x,
                payment_date_month_x=self.payment_date_month_x,
                payment_date_year_x=self.payment_date_year_x,
                payment_date_day=payment_date.day,
                payment_date_month=payment_date.strftime('%B').upper(),
                payment_date_year=payment_date.year,
            )
        else:
            payment_date_data = ''

        if self.two_partner_lines:
            second_partner_line_data = """
                <span style="width:9.6cm;text-align:left;position: absolute;left:{partner_2_x}cm;top:{partner_2_y}cm">{partner_2}</span>
            """.format(
                partner_2_x=self.partner_2_x,
                partner_2_y=self.partner_2_y,
                partner_2=partner_2
            )
        else:
            second_partner_line_data = ''

        html = """
        <div style="font-size: 11px;{vertical_configuration}">
            <span style="font-size: 15px;position: absolute;left:{amount_x}cm;top:{amount_y}cm">{amount}</span>
            <span style="position: absolute;left:{issue_date_day_x}cm;top:{issue_date_y}cm">{issue_date_day}</span>
            <span style="text-align:center;width:2.6cm;position: absolute;left:{issue_date_month_x}cm;top:{issue_date_y}cm">{issue_date_month}</span>
            <span style="position: absolute;left:{issue_date_year_x}cm;top:{issue_date_y}cm">{issue_date_year}</span>
            {payment_date_data}

            <span style="width:8.5cm;text-align:left;position: absolute;left:{partner_1_x}cm;top:{partner_1_y}cm">{partner_1}</span>
            {second_partner_line_data}
            <span style="width:11.7cm;text-align:left;position: absolute;left:{amount_text_1_x}cm;top:{amount_text_1_y}cm">{amount_text_1}</span>
            <span style="width:14.2cm;text-align:left;position: absolute;left:{amount_text_2_x}cm;top:{amount_text_2_y}cm">{amount_text_2}</span>
        </div>
        """.format(
            vertical_configuration=vertical_configuration,
            amount_x=self.amount_x,
            amount_y=self.amount_y,
            amount=locale.format('%.2f', check.get('amount'), True),
            issue_date_y=self.issue_date_y,
            issue_date_day_x=self.issue_date_day_x,
            issue_date_month_x=self.issue_date_month_x,
            issue_date_year_x=self.issue_date_year_x,
            payment_date_data=payment_date_data,
            partner_1_x=self.partner_1_x,
            partner_1_y=self.partner_1_y,
            second_partner_line_data=second_partner_line_data,
            amount_text_1_x=self.amount_text_1_x,
            amount_text_1_y=self.amount_text_1_y,
            amount_text_2_x=self.amount_text_2_x,
            amount_text_2_y=self.amount_text_2_y,
            issue_date_day=issue_date.day if issue_date else '',
            issue_date_month=issue_date.strftime('%B').upper() if issue_date else '',
            issue_date_year=issue_date.year if issue_date else '',
            partner_1=partner_1.upper(),
            amount_text_1=amount_text_1.upper(),
            amount_text_2=amount_text_2.upper(),
        )

        return html

    @staticmethod
    def split_text(text, max_amount):
        """
        Divide el texto en dos si supera la cantidad maxima de caracteres
        :param text: Texto a dividir
        :param max_amount: Cantidad maxima de caracteres permitidas
        :return: dos strings, el segundo vacio en el caso que sea necesario dividir
        """
        if len(text) < max_amount:
            res = text, ''
        else:
            try:
                res = text[:max_amount].rsplit(' ', 1)[0], \
                      text[:max_amount].rsplit(' ', 1)[1] + text[max_amount:]
            except Exception:
                raise ValidationError("No se puede imprimir el cheque")
        return res

    @staticmethod
    def _build_check_dic(check):
        """ Construye un diccionario en base a los atributos de un account.issued.check """

        try:
            from num2words import num2words
        except Exception:
            raise ValidationError("Por favor, descargar la libreria num2words")

        check_amount = (int(str(check.amount).split('.')[0]),
                        int(str(check.amount).split('.')[1].ljust(2, '0')))
        amount_text = num2words(check_amount, lang='es_CO', to='currency')  # No existe es_AR
        amount_text = amount_text.replace("pesos y", "pesos con").replace("peso y", "peso con")
        return {
            'issue_date': check.issue_date,
            'partner': check.destination_payment_id.partner_id.name,
            'amount_text': amount_text,
            'postdated': check.payment_type == 'postdated',
            'payment_date': check.payment_date,
            'amount': check.amount
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
