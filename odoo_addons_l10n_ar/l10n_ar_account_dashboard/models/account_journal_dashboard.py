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

from datetime import datetime, timedelta

from babel.dates import format_datetime, format_date

from odoo import models, api, _, fields
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import formatLang


class AccountJournal(models.Model):

    _inherit = "account.journal"

    @api.multi
    def get_line_graph_datas(self):
        """Pisamos la funcion definida en account/models/account_journal_dashboard"""
        data = []
        today = datetime.strptime(fields.Date.context_today(self), DF)
        data.append({'label': _('Past'), 'value': 0.0, 'type': 'past'})
        day_of_week = int(format_datetime(today, 'e', locale=self._context.get('lang') or 'en_US'))
        first_day_of_week = today + timedelta(days=-day_of_week + 1)
        for i in range(-1, 4):
            if i == 0:
                label = _('This Week')
            elif i == 3:
                label = _('Future')
            else:
                start_week = first_day_of_week + timedelta(days=i * 7)
                end_week = start_week + timedelta(days=6)
                if start_week.month == end_week.month:
                    label = str(start_week.day) + '-' + str(end_week.day) + ' ' + format_date(end_week, 'MMM',
                                                                                              locale=self._context.get(
                                                                                                  'lang') or 'en_US')
                else:
                    label = format_date(start_week, 'd MMM',
                                        locale=self._context.get('lang') or 'en_US') + '-' + format_date(end_week,
                                                                                                         'd MMM',
                                                                                                         locale=self._context.get(
                                                                                                             'lang') or 'en_US')
            data.append({'label': label, 'value': 0.0, 'type': 'past' if i < 0 else 'future'})

        # Build SQL query to find amount aggregated by week
        select_sql_clause = """SELECT sum(debit - credit) as total, min(date) as aggr_date from account_move_line where account_id = %(account_id)s"""
        query = ''
        start_date = (first_day_of_week + timedelta(days=-7))
        for i in range(0, 6):
            if i == 0:
                query += "(" + select_sql_clause + " and date < '" + start_date.strftime(DF) + "')"
            elif i == 5:
                query += " UNION ALL (" + select_sql_clause + " and date >= '" + start_date.strftime(DF) + "')"
            else:
                next_date = start_date + timedelta(days=7)
                query += " UNION ALL (" + select_sql_clause + " and date >= '" + start_date.strftime(
                    DF) + "' and date < '" + next_date.strftime(DF) + "')"
                start_date = next_date

        if not self.default_debit_account_id.id:
            return [{'values': False}]

        self.env.cr.execute(query, {'account_id': self.default_debit_account_id.id})
        query_results = self.env.cr.dictfetchall()
        for index in range(0, len(query_results)):
            if query_results[index].get('aggr_date') != None:
                data[index]['value'] = query_results[index].get('total')

        return [{'values': data}]

    @api.multi
    def get_journal_dashboard_datas(self):
        """ Tomo todos los valores originales y sustituyo el de pagos pendientes para mostrar el restante a pagar """
        res = super(AccountJournal, self).get_journal_dashboard_datas()
        sum_waiting = 0.0
        currency = self.currency_id or self.company_id.currency_id
        query = "SELECT residual, currency_id, type FROM account_invoice WHERE journal_id = %s AND state = 'open'"
        self.env.cr.execute(query, (self.id,))
        query_results = self.env.cr.dictfetchall()
        for result in query_results:
            factor = -1 if result['type'] in ['in_refund', 'out_refund'] else 1
            cur = self.env['res.currency'].browse(result.get('currency_id'))
            sum_waiting += cur.compute(result.get('residual'), currency) * factor
        res['sum_waiting'] = formatLang(self.env, currency.round(sum_waiting), currency_obj=currency)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
