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

from openerp.tests.common import TransactionCase
from l10n_ar_api.presentations import presentation
from datetime import date, timedelta


class TestRetentionSicore(TransactionCase):

    def create_payment_data(self):
        self.partner = self.env['res.partner'].create({
            'name': 'Proveedor',
            'partner_document_type_id': self.env.ref('l10n_ar_afip_tables.partner_document_type_80').id,
            'vat': '30715920340',
        })
        self.payment_method = self.env['account.payment.method'].create({
            'name': 'Metodo de pago',
            'code': 'Efectivo',
            'payment_type': 'inbound',
        })
        self.payment = self.env['account.payment'].create({
            'partner_id': self.partner.id,
            'payment_type': 'outbound',
            'name': '0001-00000002',
            'payment_method_id': self.payment_method.id,
            'amount': 1400,
            'state': 'posted',
        })

    def create_retention(self):
        self.retention_sicore = self.env['retention.sicore'].create({
            'name': 'SICORE Ret',
            'date_from': date.today() - timedelta(days=1),
            'date_to': date.today() + timedelta(days=1),
        })
        self.retention_line = self.env['account.payment.retention'].create({
            'name': 'Linea con retencion en pago',
            'payment_id': self.payment.id,
            'retention_id': self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada').id,
            'jurisdiction': self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada').jurisdiction,
            'activity_id': self.env.ref('l10n_ar_retentions.ret_act_19').id,
            'base': 1400,
            'amount': 400,
            'create_date': date.today(),
            'certificate_no': '00022',
        })
        self.lines = presentation.Presentation("sicore", "retenciones")

    def setUp(self):
        super(TestRetentionSicore, self).setUp()
        self.create_payment_data()
        self.create_retention()

    def test_creo_retencion_de_ganancias_en_pago_y_verifico_que_salga_correctamente_la_linea_generada_para_el_archivo(self):
        self.retention_sicore.create_line(self.lines, self.retention_line)
        today = date.today().strftime("%d/%m/%Y")
        assert self.lines.lines[0].get_line_string() == "06{}    0001000000020000000001400,002170{}100000001400,00{}01000000000400,00000,00          80         30715920340         00022".format(today, self.env.ref('l10n_ar_retentions.ret_act_19').code, today)

    def test_saco_el_documento_al_partner_y_deberia_generar_un_error(self):
        partner = self.env['res.partner'].create({
            'name': 'Proveedor',
        })
        payment = self.env['account.payment'].create({
            'partner_id': partner.id,
            'payment_type': 'outbound',
            'name': '0001-00000002',
            'payment_method_id': self.payment_method.id,
            'amount': 1400,
            'state': 'posted',
        })
        retention_line = self.env['account.payment.retention'].create({
            'name': 'Linea con retencion en pago',
            'payment_id': payment.id,
            'retention_id': self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada').id,
            'jurisdiction': self.env.ref('l10n_ar_retentions.retention_retention_ganancias_efectuada').jurisdiction,
            'activity_id': self.env.ref('l10n_ar_retentions.ret_act_19').id,
            'base': 1400,
            'amount': 400,
            'create_date': date.today(),
            'certificate_no': '00022',
        })
        assert self.retention_sicore.validate_fields(retention_line)

    def test_creo_retenciones_en_pago_y_verifico_que_salga_correctamente_la_linea_generada_para_el_archivo(self):
        self.retention_line_vat = self.env['account.payment.retention'].create({
            'name': 'Linea con retencion IVA en pago',
            'payment_id': self.payment.id,
            'retention_id': self.env.ref('l10n_ar_retentions.retention_retention_iva_efectuada').id,
            'jurisdiction': 'nacional',
            'base': 1400,
            'amount': 500,
            'create_date': date.today(),
            'certificate_no': '00011',
        })
        self.retention_sicore.create_line(self.lines, self.retention_line)
        self.retention_sicore.create_line(self.lines, self.retention_line_vat)
        today = date.today().strftime("%d/%m/%Y")
        assert self.lines.lines[
                   0].get_line_string() == "06{}    0001000000020000000001400,002170{}100000001400,00{}01000000000400,00000,00          80         30715920340         00022".format(
            today, self.env.ref('l10n_ar_retentions.ret_act_19').code, today)
        assert self.lines.lines[
                   1].get_line_string() == "06{}    0001000000020000000001400,00767000100000001400,00{}01000000000500,00000,00          80         30715920340         00011".format(
            today, today)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
