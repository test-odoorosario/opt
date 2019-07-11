# -*- coding: utf-8 -*-
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api
from l10n_ar_api.presentations import presentation
from openerp.exceptions import ValidationError
from datetime import datetime


class RetentionSicore(models.Model):  # Validacion de campos
    _name = "retention.sicore"

    name = fields.Char(
        string='Nombre',
        required=True
    )
    date_from = fields.Date(
        string='Desde',
        required=True
    )
    date_to = fields.Date(
        string='Hasta',
        required=True
    )
    file = fields.Binary(
        string='Archivo',
        filename='filename'
    )
    filename = fields.Char(
        string='Nombre Archivo'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        readonly=True,
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('retention.sicore')
    )

    @api.constrains('date_from', 'date_to')
    def check_date(self):
        if self.date_from > self.date_to:
            raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin.")

    def validate_fields(self, retention):
        """ Validaciones de campos necesarios para la generacion del archivo"""
        errors = []
        if not retention.payment_id.partner_id.vat:
            errors.append('Falta el numero de documento para el partner "{}" de la retencion: {}'.format(
                retention.payment_id.partner_id.name, retention.certificate_no)
            )
        else:
            document_afip_code = self.env['codes.models.relation'].get_code(
                'partner.document.type',
                retention.payment_id.partner_id.partner_document_type_id.id
            )
            if not document_afip_code:
                errors.append('Falta tipo de documento o el codigo afip del tipo de documento {} de '
                              'la retencion: {}'.format(
                    retention.payment_id.partner_id.partner_document_type_id.name, retention.certificate_no
                ))
            if len(retention.payment_id.partner_id.vat) < 11:
                errors.append('Numero de cuit erroneo para el partner "{}" de la retencion: {}'.format(
                    retention.payment_id.partner_id.name, retention.certificate_no
                ))

        if retention.activity_id and not retention.activity_id.code:
            errors.append('Falta el codigo de regimen de la actividad "{}" para la retencion: {}'.format(
                retention.activity_id.name, retention.certificate_no
            ))
        return errors


class RetentionSicoreSearch(models.Model):  # Busqueda de retenciones para archivo
    _inherit = 'retention.sicore'

    def search_retentions(self):
        """ Busco las retenciones de los pagos validados de proveedor en un rango de fechas"""
        retentions = self.env['account.payment.retention'].search([
            ('payment_id.payment_date', '>=', self.date_from),
            ('payment_id.payment_date', '<=', self.date_to),
            ('type', 'in', ('profit', 'vat')),
            ('payment_id.state', '=', 'posted'),
            ('payment_id.payment_type', '=', 'outbound')
        ]).sorted(key=lambda r: (r.payment_id.payment_date, r.certificate_no))
        return retentions


class RetentionSicoreData(models.Model):  # Obtencion de datos para generacion de archivo
    _inherit = 'retention.sicore'

    def get_code(self, document):
        # CODIGO DE COMPROBANTE
        # 01 Factura
        # 02 Recibo
        # 03 Nota de Crédito
        # 04 Nota de Débito
        # 05 Otro comprobante
        # 06 Orden de Pago
        # 07 Recibo de Sueldo
        # 08 Recibo de Sueldo- Devolución
        # 09 Escritura Pública
        # 10 C.1116
        # 11 Factura (16 Dígitos)
        code = ''
        if document._name == 'account.payment':
            code = '06'
        return code

    def get_tax_code(self, retention):
        # CODIGO DE IMPUESTO
        # 064 Fondo Nacional de Incentivo Docente
        # 172 Impuesto a la Transferencia de Inmuebles
        # 210 Ganancias Régimen Especial de Ingreso R.G. 830
        # 217 Impuesto a las Ganancias
        # 218 Impuesto a las Ganancias - Beneficiarios del Exterior
        # 466 Gravamen de Emergencia a los Premios de determinados juegos de sorteoy concursos deportivos
        # 767 Impuesto al Valor Agregado
        return '767' if retention.type == 'vat' else '217'

    def get_condition_code(self):
        # CODIGO DE CONDICION
        # 00 Ninguna
        # 01 Inscripto
        # 02 No inscripto.
        # 03 No categorizado
        # 06 Contratación hora día estadía
        # 07 Contratación mensual
        # 08 Incluido en el régimen fiscal de granos
        # 09 No incluido en el régimen fiscal de granos
        # 10 Inscripto demás sujetos
        # 11 Inscripto retenciones IVA estaciones de servicios
        # 12 Servicios públicos
        # 13 Venta de cosas muebles y locación - Alícuota general
        # 14 Venta de cosas muebles y locación - Alícuota reducida
        # 15 Retención sustitutiva
        return '01'

    def get_document_afip_code(self, document_id):
        document_afip_code = self.env['codes.models.relation'].get_code(
            'partner.document.type',
            document_id
        )
        return document_afip_code


class RetentionSicoreCreateLine(models.Model):  # Creacion de linea de archivo
    _inherit = 'retention.sicore'

    def create_line(self, lines, r):
        line = lines.create_line()
        line.codigoComprobante = self.get_code(r.payment_id)
        line.fechaDocumento = datetime.strptime(r.payment_id.payment_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        line.referenciaDocumento = r.payment_id.name.replace('-', '').rjust(16)
        line.importeDocumento = '{0:.2f}'.format(r.payment_id.amount).zfill(16).replace('.', ',')
        line.codigoImpuesto = self.get_tax_code(r)
        line.codigoRegimen = str(r.activity_id.code).zfill(3)
        line.codigoOperacion = '1'  # 1 Retención, 2 Percepción, 4 Imposibilidad de Retención
        line.base = '{0:.2f}'.format(r.base).zfill(14).replace('.', ',')
        line.fecha = datetime.strptime(r.payment_id.payment_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        line.codigoCondicion = self.get_condition_code()
        line.retencionPracticadaSS = '0'
        line.importe = '{0:.2f}'.format(r.amount).zfill(14).replace('.', ',')
        line.porcentaje = '{0:.2f}'.format(0).zfill(6).replace('.', ',')
        line.fechaEmision = ''.ljust(10)
        line.codigoDocumento = self.get_document_afip_code(r.payment_id.partner_id.partner_document_type_id.id)
        line.cuit = r.payment_id.partner_id.vat.rjust(20)
        line.numeroCertificado = r.certificate_no.replace('-', '').rjust(14)


class RetentionSicoreFile(models.Model):  # Generacion de archivo
    _inherit = 'retention.sicore'

    def generate_file(self):
        lines = presentation.Presentation("sicore", "retenciones")
        retentions = self.search_retentions()
        errors = []
        for r in retentions:
            errors = self.validate_fields(r)
            if errors:
                continue
            self.create_line(lines, r)
        if errors:
            raise ValidationError("\n".join(errors))
        else:
            self.file = lines.get_encoded_string()
            self.filename = 'ret_gan_{}_{}.txt'.format(
                str(self.date_from).replace('-', ''),
                str(self.date_to).replace('-', '')
            )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
