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

{

    'name': 'Opyme project report',

    'version': '1.0',

    'category': '',

    'summary': 'Opyme project report',

    'author': 'OPENPYME S.R.L',

    'website': 'openpyme.com.ar',

    'depends': [

        'opyme_cash_flow',
        'sale_contract',

    ],

    'data': [
    
        'wizard/views/project_report_wizard_view.xml',
        'wizard/views/change_cashflow_date_view.xml',
        'views/sale_order_view.xml',
        'views/res_currency_rate_cash_flow_view.xml',
        'security/ir.model.access.csv',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
Opyme project report
======================================
* Nuevo menu en Tesoreria/Cash Flow/Cash flow de ventas para generar un reporte de cash flow de ventas de los contratos activos y ventas sin facturar
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
