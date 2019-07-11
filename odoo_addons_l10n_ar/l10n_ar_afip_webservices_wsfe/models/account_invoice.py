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
import pytz, operator
from collections import defaultdict
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from l10n_ar_api import documents
from l10n_ar_api.afip_webservices import wsfe, wsfex, wsbfe
from openerp import models, fields, api, registry
from openerp.exceptions import ValidationError

MAX_LENGTH = 199


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    date_service_from = fields.Date('Fecha servicio inicial', help='Fecha inicial del servicio brindado')
    date_service_to = fields.Date('Fecha servicio final', help='Fecha final del servicio brindado')
    cae = fields.Char('CAE', readonly=True, copy=False)
    cae_due_date = fields.Date('Vencimiento CAE', readonly=True, copy=False)
    wsfe_request_detail_ids = fields.Many2many(
        'wsfe.request.detail',
        'invoice_request_details',
        'invoice_id',
        'request_detail_id',
        string='Detalles Wsfe',
        copy=False,
    )

    def _set_dates(self, invoice_dict):
        codes_models_proxy = self.env['codes.models.relation']
        # Tomo las listas de IDs de facturas del diccionario y las "aplano" a una sola
        invoice_ids = reduce(operator.add, invoice_dict.values())
        for inv in self.browse(invoice_ids):
            if codes_models_proxy.get_code('afip.concept', inv.afip_concept_id.id) in ['2', '3']:
                if not inv.date_service_from:
                    inv.date_service_from = inv.date_invoice
                if not inv.date_service_to:
                    inv.date_service_to = inv.date_invoice

    @api.multi
    def action_move_create(self):
        """
        En el modulo de PoS, se ejecuta la funcion del tipo de talonario una vez para cada factura. Aca busco que, si
        todas las facturas seleccionadas son electronicas, lo ejecute una sola vez con todas esas, haciendo los chequeos
        correspondientes
        :return: finalmente llama al super
        """
        invoices_by_document_book = defaultdict(list)
        invoices_fiscal_bond_by_document_book = defaultdict(list)
        invoices_exportation_by_document_book = defaultdict(list)
        all_invoices = self.browse(self.ids or self.env.context.get('active_ids'))
        invoice_types = all_invoices.mapped('type')

        for invoice in all_invoices:
            if not invoice.amount_total_signed:
                raise ValidationError("Ha seleccionado una o mas facturas con monto nulo")
            invoice._validate_fiscal_position_and_denomination()
            if invoice.type in ['out_invoice', 'out_refund']:
                book = invoice.get_document_book()
                if not invoice.cae:
                    if book.book_type_id.type == 'electronic':
                        invoices_by_document_book[book].append(invoice.id)
                    if book.book_type_id.type == 'electronic_exportation':
                        invoices_exportation_by_document_book[book].append(invoice.id)
                    if book.book_type_id.type == 'fiscal_electronic_bond':
                        invoices_fiscal_bond_by_document_book[book].append(invoice.id)

        if (invoice_types == ['out_invoice'] or invoice_types == ['out_refund']) and \
                (invoices_by_document_book or invoices_exportation_by_document_book or \
                    invoices_fiscal_bond_by_document_book):
            if invoices_by_document_book:
                afip_wsfe = all_invoices[0]._get_wsfe()
            if invoices_exportation_by_document_book:
                afip_wsfex = all_invoices[0]._get_wsfex()
            if invoices_fiscal_bond_by_document_book:
                afip_wsbfe = all_invoices[0]._get_wsbfe()
            # ELECTRONICA
            for k, v in invoices_by_document_book.iteritems():
                # Obtenemos el codigo de comprobante
                inv = self.browse(v)
                document_afip_code = inv.get_document_afip_code(k, inv)
                # Validamos la numeracion
                k.action_wsfe_number(afip_wsfe, document_afip_code)

                split_ids = [v[i:i + MAX_LENGTH] for i in range(0, len(v), MAX_LENGTH)]
                for split_list in split_ids:
                    invoices = self.browse(split_list)
                    getattr(invoices, k.book_type_id.foo)(k)
                    for invoice in invoices:
                        invoice.check_invoice_duplicity()
            # ELECTORNICA EXPORTACION
            for k, v in invoices_exportation_by_document_book.iteritems():
                # Obtenemos el codigo de comprobante
                inv = self.browse(v)
                document_afip_code = inv.get_document_afip_code(k, inv)
                # Validamos la numeracion
                k.action_wsfe_number(afip_wsfex, document_afip_code)

                split_ids = [v[i:i + MAX_LENGTH] for i in range(0, len(v), MAX_LENGTH)]
                for split_list in split_ids:
                    invoices = self.browse(split_list)
                    getattr(invoices, k.book_type_id.foo)(k)
                    for invoice in invoices:
                        invoice.check_invoice_duplicity()
            # BONO FISCAL ELECTORNICO
            for k, v in invoices_fiscal_bond_by_document_book.iteritems():
                # Obtenemos el codigo de comprobante
                inv = self.browse(v)
                document_afip_code = inv.get_document_afip_code(k, inv)
                # Validamos la numeracion
                k.action_wsfe_number(afip_wsbfe, document_afip_code)

                split_ids = [v[i:i + MAX_LENGTH] for i in range(0, len(v), MAX_LENGTH)]
                for split_list in split_ids:
                    invoices = self.browse(split_list)
                    getattr(invoices, k.book_type_id.foo)(k)
                    for invoice in invoices:
                        invoice.check_invoice_duplicity()

        res = super(AccountInvoice, self).action_move_create()
        if invoices_by_document_book:
            self._set_dates(invoices_by_document_book)
        if invoices_exportation_by_document_book:
            self._set_dates(invoices_exportation_by_document_book)
        if invoices_fiscal_bond_by_document_book:
            self._set_dates(invoices_fiscal_bond_by_document_book)
        return res

    def action_electronic(self, document_book):
        """
        Realiza el envio a AFIP de la factura y escribe en la misma el CAE y su fecha de vencimiento.
        :raises ValidationError: Si el talonario configurado no tiene la misma numeracion que en AFIP.
                                 Si hubo algun error devuelto por afip al momento de enviar los datos.
        """
        electronic_invoices = []
        pos = document_book.pos_ar_id
        invoices = self.filtered(lambda l: not l.cae and l.amount_total and l.pos_ar_id == pos).sorted(lambda l: l.id)
        if invoices:
            afip_wsfe = invoices[0]._get_wsfe()

        for invoice in invoices:
            # Validamos los campos
            invoice._validate_required_electronic_fields()
            # Obtenemos el codigo de comprobante
            document_afip_code = invoice.get_document_afip_code(document_book, invoice)
            # Armamos la factura
            electronic_invoices.append(invoice._set_electronic_invoice_details(document_afip_code))

        if electronic_invoices:
            response = None
            new_cr = None

            # Chequeamos la conexion y enviamos las facturas a AFIP, guardando el JSON enviado, el response y mostrando
            # los errores (en caso de que los haya)
            try:
                afip_wsfe.check_webservice_status()
                response, invoice_detail = afip_wsfe.get_cae(electronic_invoices, pos.name)
                afip_wsfe.show_error(response)
            except Exception, e:
                new_cr = registry(self.env.cr.dbname).cursor()
                self.env.cr.rollback()
                raise ValidationError(e.message)
            finally:
                # Commiteamos para que no haya inconsistencia con la AFIP. Como ya tenemos el CAE escrito en la factura,
                # al validarla nuevamente no se vuelve a enviar y se va a mantener la numeracion correctamente
                if response and response.FeDetResp:
                    with api.Environment.manage():
                        cr_to_use = new_cr or self.env.cr
                        new_env = api.Environment(cr_to_use, self.env.uid, self.env.context)
                        invoices.write_wsfe_response(new_env, invoice_detail, response)
                        new_invoices = new_env['account.invoice'].browse(invoices.ids)
                        for invoice in new_invoices:
                            # Busco, dentro del detalle de la respuesta, el segmento correspondiente a la factura
                            number = document_book.next_number()
                            filt = filter(lambda l: l.CbteDesde == long(number[-8:]),
                                          response.FeDetResp.FECAEDetResponse)
                            resp = filt[0] if filt else None
                            if resp and resp.Resultado == 'A':
                                invoice.write({
                                    'cae': resp.CAE,
                                    'cae_due_date': datetime.strptime(resp.CAEFchVto,
                                                                      '%Y%m%d') if resp.CAEFchVto else None,
                                    'name': number
                                })
                            # Si el envio no fue exitoso, se retrocede un numero en el talonario para compensar el
                            # aumento realizado al enviar la factura fallida
                            else:
                                document_book.prev_number()
                        self._commit(new_env)

            if response and response.FeCabResp and response.FeCabResp.Resultado == 'R':
                # Traemos el conjunto de errores
                errores = '\n'.join(obs.Msg for obs in response.FeDetResp.FECAEDetResponse[0].Observaciones.Obs) \
                    if hasattr(response.FeDetResp.FECAEDetResponse[0], 'Observaciones') else ''
                raise ValidationError('Hubo un error al intentar validar el documento\n{0}'.format(errores))

    def write_wsfe_response(self, env, invoice_detail, response):
        """ Escribe el envio y respuesta de un envio a AFIP """
        if response.FeCabResp:
            # Nos traemos el offset de la zona horaria para dejar en la base en UTC como corresponde
            offset = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).utcoffset().total_seconds() / 3600
            fch_proceso = datetime.strptime(response.FeCabResp.FchProceso, '%Y%m%d%H%M%S') - relativedelta(hours=offset)
            result = response.FeCabResp.Resultado
            date = fch_proceso
        else:
            result = "Error"
            date = fields.Datetime.now()

        env['wsfe.request.detail'].sudo().create({
            'invoice_ids': [(4, self.ids)],
            'request_sent': invoice_detail,
            'request_received': response,
            'result': result,
            'date': date,
        })

    def _commit(self, env):
        env.cr.commit()

    @staticmethod
    def convert_currency(from_currency, to_currency, amount=1.0, d=None):
        """
        Convierte `amount` de `from_currency` a `to_currency` segun la cotizacion de la fecha `d`.
        :param from_currency: La moneda que queremos convertir.
        :param to_currency: La moneda a la que queremos convertir.
        :param amount: La cantidad que queremos convertir (1 para sacar el rate de la moneda).
        :param d: La fecha que se usara para tomar la cotizacion de ambas monedas.
        :return: El valor en la moneda convertida segun el rate de conversion.
        """
        if from_currency.id == to_currency.id:
            return amount
        if not d:
            d = str(date.today())
        from_currency_with_context = from_currency.with_context(date=d)
        to_currency_with_context = to_currency.with_context(date=d)
        converted_amount = from_currency_with_context.compute(
            amount, to_currency_with_context, round=False
        )
        return converted_amount

    def _set_electronic_invoice_details(self, document_afip_code):
        """ Mapea los valores de ODOO al objeto ElectronicInvoice"""

        self._set_empty_invoice_details()
        denomination_c = self.env.ref('l10n_ar_afip_tables.account_denomination_c')
        codes_models_proxy = self.env['codes.models.relation']

        # Seteamos los campos generales de la factura
        electronic_invoice = wsfe.invoice.ElectronicInvoice(document_afip_code)
        # Para comprobantes C solo se informa el importe total conciliado que corresponde con el taxed_amount de la API
        electronic_invoice.taxed_amount = self.amount_to_tax if self.denomination_id != denomination_c else self.amount_total
        electronic_invoice.untaxed_amount = self.amount_not_taxable if self.denomination_id != denomination_c else 0
        electronic_invoice.exempt_amount = self.amount_exempt if self.denomination_id != denomination_c else 0
        electronic_invoice.document_date = datetime.strptime(
            self.date_invoice or fields.Date.context_today(self),
            '%Y-%m-%d'
        )
        if codes_models_proxy.get_code('afip.concept', self.afip_concept_id.id) in ['2', '3']:
            electronic_invoice.service_from = datetime.strptime(self.date_service_from or fields.Date.context_today(self), '%Y-%m-%d')
            electronic_invoice.service_to = datetime.strptime(self.date_service_to or fields.Date.context_today(self), '%Y-%m-%d')
        electronic_invoice.payment_due_date = datetime.strptime(
            self.date_due or fields.Date.context_today(self),
            '%Y-%m-%d'
        )
        electronic_invoice.customer_document_number = self.partner_id.vat
        electronic_invoice.customer_document_type = codes_models_proxy.get_code(
            'partner.document.type',
            self.partner_id.partner_document_type_id.id
        )
        electronic_invoice.mon_id = self.env['codes.models.relation'].get_code(
            'res.currency',
            self.currency_id.id
        )
        electronic_invoice.mon_cotiz = self.convert_currency(
            from_currency=self.currency_id,
            to_currency=self.company_id.currency_id,
            d=self.date_invoice
        )

        electronic_invoice.concept = int(codes_models_proxy.get_code(
            'afip.concept',
            self.afip_concept_id.id
        ))
        # Agregamos impuestos y percepciones
        self._add_vat_to_electronic_invoice(electronic_invoice)
        self._add_perceptions_to_electronic_invoice(electronic_invoice)
        return electronic_invoice

    def _add_vat_to_electronic_invoice(self, electronic_invoice):
        """ Agrega los impuestos que son iva a informar """

        group_vat = self.env.ref('l10n_ar.tax_group_vat')
        codes_models_proxy = self.env['codes.models.relation']
        for tax in self.tax_line_ids:
            if tax.tax_id.tax_group_id == group_vat and not tax.tax_id.is_exempt:
                code = int(codes_models_proxy.get_code('account.tax', tax.tax_id.id))
                electronic_invoice.add_iva(documents.tax.Iva(code, tax.amount, tax.base))

    def _add_perceptions_to_electronic_invoice(self, electronic_invoice):
        """ Agrega los impuestos que son percepciones """

        group_vat = self.env.ref('l10n_ar.tax_group_vat')
        perception_perception_proxy = self.env['perception.perception']

        for tax in self.tax_line_ids.filtered(lambda t: t.amount > 0):
            if tax.tax_id.tax_group_id != group_vat:
                perception = perception_perception_proxy.search([('tax_id', '=', tax.tax_id.id)], limit=1)

                if not perception:
                    raise ValidationError("Percepcion no encontrada para el impuesto {}".format(tax.tax_id.name))

                code = perception.get_afip_code()
                tribute_aliquot = round(tax.amount / tax.base if tax.base else 0, 2)
                electronic_invoice.add_tribute(documents.tax.Tribute(code, tax.amount, tax.base, tribute_aliquot))

    def _get_wsfe(self):
        """
        Busca el objeto de wsfe para utilizar sus servicios
        :return: instancia de Wsfe
        """
        wsfe_config = self.env['wsfe.configuration'].search([
            ('wsaa_token_id.name', '=', 'wsfe'),
            ('company_id', '=', self.company_id.id),
        ])

        if not wsfe_config:
            raise ValidationError('No se encontro una configuracion de factura electronica')

        access_token = wsfe_config.wsaa_token_id.get_access_token()
        homologation = False if wsfe_config.type == 'production' else True
        afip_wsfe = wsfe.wsfe.Wsfe(access_token, self.company_id.vat, homologation)

        return afip_wsfe

    def _set_empty_invoice_details(self):
        """ Completa los campos de la invoice no establecidos a un default """

        vals = {}

        if not self.afip_concept_id:
            vals['afip_concept_id'] = self._get_afip_concept_based_on_products().id

        self.write(vals)

    def _validate_required_electronic_fields(self):
        if not (self.partner_id.vat and self.partner_id.partner_document_type_id):
            raise ValidationError('Por favor, configurar tipo y numero de documento en el cliente')

    def _validate_required_electronic_exportation_fields(self):
        if any(line.invoice_line_tax_ids for line in self.invoice_line_ids):
            raise ValidationError('Las líneas no deben contener impuestos cargados.')
        if not self.partner_id.partner_document_type_id:
            raise ValidationError('Por favor, configurar tipo de documento en el cliente')

    def _validate_required_fiscal_electronic_bond_fields(self):
        if not (self.partner_id.vat and self.partner_id.partner_document_type_id):
            raise ValidationError('Por favor, configurar tipo y numero de documento en el cliente')

        denomination_a = self.env.ref('l10n_ar_afip_tables.account_denomination_a')
        cuit = self.env.ref('l10n_ar_afip_tables.partner_document_type_80')
        if self.partner_id.partner_document_type_id == cuit and not self.denomination_id == denomination_a:
            raise ValidationError("El tipo de documento del cliente debe ser\
                                  CUIT en comprobantes tipo A.")

        exempt_iva = self.env.ref('l10n_ar_afip_tables.codes_models_afip_account_tax_2_sale').id_model
        for line in self.invoice_line_ids:
            if line.invoice_line_tax_ids:
                for tax in line.invoice_line_tax_ids:
                    if tax.id == exempt_iva and not self.amount_exempt:
                        raise ValidationError("El importe de operaciones exentas debe ser\
                                               mayor a 0 donde exista algun ítem de factura con Iva exento")

    def _get_afip_concept_based_on_products(self):
        """
        Devuelve el concepto de la factura en base a los tipos de productos
        :return: afip.concept, tipo de concepto
        """
        product_types = self.invoice_line_ids.mapped('product_id.type')

        # Estaria bueno pensar una forma para no hardcodearlo, ponerle el concepto en el producto
        # me parecio mucha configuracion a la hora de importar datos o para el cliente, quizas hacer un
        # compute?

        if len(product_types) > 1 and 'service' in product_types:
            # Productos y servicios
            code = '3'
        else:
            if 'service' in product_types:
                # Servicio
                code = '2'
            else:
                # Producto
                code = '1'

        return self.env['codes.models.relation'].get_record_from_code('afip.concept', code)

    # EXPORTACION
    def _get_wsfex(self):
        """
        Busca el objeto de wsfex para utilizar sus servicios
        :return: instancia de Wsfex
        """
        wsfex_config = self.env['wsfe.configuration'].search([
            ('wsaa_token_id.name', '=', 'wsfex'),
            ('company_id', '=', self.company_id.id),
        ])

        if not wsfex_config:
            raise ValidationError('No se encontro una configuracion de factura electronica exportacion')
        if not self.partner_id.country_id.vat:
            raise ValidationError('Falta cargar el cuit del pais.')

        access_token = wsfex_config.wsaa_token_id.get_access_token()
        homologation = False if wsfex_config.type == 'production' else True
        afip_wsfex = wsfex.wsfex.Wsfex(access_token, self.company_id.vat, homologation)

        return afip_wsfex

    def action_electronic_exportation(self, document_book):
        """
        Realiza el envio a AFIP de la factura de exportacion y escribe en la misma el CAE y su fecha de vencimiento.
        :raises ValidationError: Si el talonario configurado no tiene la misma numeracion que en AFIP.
                                 Si hubo algun error devuelto por afip al momento de enviar los datos.
        """
        electronic_invoices = []
        pos = document_book.pos_ar_id
        invoices = self.filtered(lambda l: not l.cae and l.amount_total and l.pos_ar_id == pos).sorted(lambda l: l.id)
        if invoices:
            afip_wsfex = invoices[0]._get_wsfex()
        for invoice in invoices:
            # Validamos los campos
            invoice._validate_required_electronic_exportation_fields()
            # Obtenemos el codigo de comprobante
            document_afip_code = invoice.get_document_afip_code(document_book, invoice)
            # Armamos la factura
            electronic_invoices.append(invoice._set_electronic_exportation_invoice_details(document_afip_code))
        if electronic_invoices:
            responses = None
            new_cr = None
            # Chequeamos la conexion y enviamos las facturas a AFIP, guardando el JSON enviado, el response y mostrando
            # los errores (en caso de que los haya)
            try:
                afip_wsfex.check_webservice_status()
                responses, invoice_details = afip_wsfex.get_cae(electronic_invoices, pos.name)
                for r in responses:
                    afip_wsfex.show_error(r)
                if len(responses) != len(invoice_details):
                    raise ValidationError('Las longitudes son distintas')
            except Exception, e:
                new_cr = registry(self.env.cr.dbname).cursor()
                self.env.cr.rollback()
                raise ValidationError(e.message)
            finally:
                # Commiteamos para que no haya inconsistencia con la AFIP. Como ya tenemos el CAE escrito en la factura,
                # al validarla nuevamente no se vuelve a enviar y se va a mantener la numeracion correctamente
                if responses:
                    for idx, response in enumerate(responses):
                        if response and response.FEXResultAuth:
                            with api.Environment.manage():
                                cr_to_use = new_cr or self.env.cr
                                new_env = api.Environment(cr_to_use, self.env.uid, self.env.context)
                                invoices.write_wsfex_response(new_env, invoice_details[idx], response)
                                new_invoices = new_env['account.invoice'].browse(invoices.ids)
                                for invoice in new_invoices:
                                    # Busco, dentro del detalle de la respuesta, el segmento correspondiente a la factura
                                    number = document_book.next_number()
                                    if response.FEXResultAuth.Resultado == 'A':
                                        invoice.write({
                                            'cae': response.FEXResultAuth.Cae,
                                            'cae_due_date': datetime.strptime(
                                                response.FEXResultAuth.Fch_venc_Cae,
                                                '%Y%m%d'
                                            ) if response.FEXResultAuth.Fch_venc_Cae else None,
                                            'name': number
                                        })
                                    # Si el envio no fue exitoso, se retrocede un numero en el talonario para compensar el
                                    # aumento realizado al enviar la factura fallida
                                    else:
                                        document_book.prev_number()
                                self._commit(new_env)

                        if response and response.FEXResultAuth and response.FEXResultAuth.Resultado == 'R':
                            # Traemos el conjunto de errores
                            errores = '\n'.join(response.FEXResultAuth.Motivos_Obs) \
                                if hasattr(response.FEXResultAuth.Motivos_Obs, 'Observaciones') else ''
                            raise ValidationError('Hubo un error al intentar validar el documento\n{0}'.format(errores))

    def _set_electronic_exportation_invoice_details(self, document_afip_code):
        """ Mapea los valores de ODOO al objeto ExportationElectronicInvoice"""

        self._set_empty_invoice_details()
        codes_models_proxy = self.env['codes.models.relation']

        # Seteamos los campos generales de la factura
        electronic_invoice = wsfex.invoice.ExportationElectronicInvoice(document_afip_code)
        electronic_invoice.document_date = datetime.strptime(
            self.date_invoice or fields.Date.context_today(self),
            '%Y-%m-%d'
        )
        if codes_models_proxy.get_code('afip.concept', self.afip_concept_id.id) in ['2', '3']:
            electronic_invoice.service_from = datetime.strptime(self.date_service_from, '%Y-%m-%d')
            electronic_invoice.service_to = datetime.strptime(self.date_service_to, '%Y-%m-%d')
        electronic_invoice.payment_due_date = datetime.strptime(
            self.date_due or fields.Date.context_today(self),
            '%Y-%m-%d'
        )
        electronic_invoice.destiny_country = int(codes_models_proxy.get_code(
            'res.country',
            self.partner_id.country_id.id
        ))
        electronic_invoice.customer_name = self.partner_id.name
        electronic_invoice.customer_street = self.partner_id.street
        electronic_invoice.destiny_country_cuit = self.partner_id.country_id.vat
        electronic_invoice.customer_document_type = codes_models_proxy.get_code(
            'partner.document.type',
            self.partner_id.partner_document_type_id.id
        )
        electronic_invoice.mon_id = self.env['codes.models.relation'].get_code(
            'res.currency',
            self.currency_id.id
        )
        electronic_invoice.mon_cotiz = self.convert_currency(
            from_currency=self.currency_id,
            to_currency=self.company_id.currency_id,
            d=self.date_invoice
        )
        electronic_invoice.concept = int(codes_models_proxy.get_code(
            'afip.concept',
            self.afip_concept_id.id
        ))
        # 1 = Exportación definitiva de bienes, 2 = Servicios, 4 = Otros
        electronic_invoice.exportation_type = electronic_invoice.concept
        if electronic_invoice.concept == 3:
            electronic_invoice.exportation_type = 4
        # 1: Español, 2: Inglés, 3: Portugués
        electronic_invoice.document_language = 1
        ndc_document_code = int(self.env['codes.models.relation'].get_code(
            'afip.voucher.type',
            self.env.ref('l10n_ar_afip_tables.afip_voucher_type_020').id))
        ncc_document_code = int(self.env['codes.models.relation'].get_code(
            'afip.voucher.type',
            self.env.ref('l10n_ar_afip_tables.afip_voucher_type_021').id))
        fcc_document_code = int(self.env['codes.models.relation'].get_code(
            'afip.voucher.type',
            self.env.ref('l10n_ar_afip_tables.afip_voucher_type_019').id))
        document_codes = [ndc_document_code, ncc_document_code]
        electronic_invoice.existent_permission = '' \
            if (electronic_invoice.exportation_type in [2, 4] and electronic_invoice.document_code == fcc_document_code)\
            or electronic_invoice.document_code in document_codes else 'N'
        electronic_invoice.incoterms = 'CIF'
        # Agregamos items
        electronic_invoice.array_items = self.add_item_exportation()
        return electronic_invoice

    def add_item_exportation(self):
        """ Mapea los valores de ODOO al objeto ExportationElectronicInvoiceItem """
        array_items = []
        for line in self.invoice_line_ids:
            item = wsfex.invoice.ExportationElectronicInvoiceItem(line.product_id.name)
            item.quantity = line.quantity
            try:
                item.measurement_unit = self.env['codes.models.relation'].get_code(
                    'product.uom',
                    line.uom_id.id
                )
            except:
                item.measurement_unit = 98
            item.unit_price = line.price_unit
            item.bonification = ((line.price_unit * line.quantity) * (line.discount / 100)) if line.discount else 0.0
            array_items.append(item)
        return array_items

    def get_document_afip_code(self, document_book, invoice):
        """ Busco el codigo del documento de AFIP"""
        document_type_id = document_book.document_type_id.id
        voucher_type = self.env['afip.voucher.type'].search([
            ('document_type_id', '=', document_type_id),
            ('denomination_id', '=', invoice.denomination_id.id)],
            limit=1
        )
        return int(self.env['codes.models.relation'].get_code('afip.voucher.type', voucher_type.id))

    def write_wsfex_response(self, env, invoice_detail, response):
        """ Escribe el envio y respuesta de un envio a AFIP """
        if response.FEXResultAuth:
            # Nos traemos el offset de la zona horaria para dejar en la base en UTC como corresponde
            offset = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).utcoffset().total_seconds() / 3600
            fch_proceso = datetime.now() - relativedelta(hours=offset)
            result = response.FEXResultAuth.Resultado
            date = fch_proceso
        else:
            result = "Error"
            date = fields.Datetime.now()

        env['wsfe.request.detail'].sudo().create({
            'invoice_ids': [(4, self.ids)],
            'request_sent': invoice_detail,
            'request_received': response,
            'result': result,
            'date': date,
        })

    # BONO FISCAL
    def action_fiscal_electronic_bond(self, document_book):
        """
        Realiza el envio a AFIP del bono y escribe en el mismo el CAE y su fecha de vencimiento.
        :raises ValidationError: Si el talonario configurado no tiene la misma numeracion que en AFIP.
                                 Si hubo algun error devuelto por afip al momento de enviar los datos.
        """
        electronic_invoices = []
        pos = document_book.pos_ar_id
        invoices = self.filtered(lambda l: not l.cae and l.amount_total and l.pos_ar_id == pos).sorted(lambda l: l.id)
        if invoices:
            afip_wsbfe = invoices[0]._get_wsbfe()

        for invoice in invoices:
            # Validamos los campos
            invoice._validate_required_fiscal_electronic_bond_fields()
            # Obtenemos el codigo de comprobante
            document_afip_code = invoice.get_document_afip_code(document_book, invoice)
            # Armamos la factura
            electronic_invoices.append(invoice._set_electronic_bond_details(document_afip_code))

        if electronic_invoices:
            responses = None
            new_cr = None

            # Chequeamos la conexion y enviamos las facturas a AFIP, guardando el JSON enviado, el response y mostrando
            # los errores (en caso de que los haya)
            try:
                afip_wsbfe.check_webservice_status()
                responses, invoice_details = afip_wsbfe.get_cae(electronic_invoices, pos.name)
                for r in responses:
                    afip_wsbfe.show_error(r)
                if len(responses) != len(invoice_details):
                    raise ValidationError('Las longitudes son distintas')
            except Exception, e:
                new_cr = registry(self.env.cr.dbname).cursor()
                self.env.cr.rollback()
                raise ValidationError(e.message)
            finally:
                # Commiteamos para que no haya inconsistencia con la AFIP. Como ya tenemos el CAE escrito en el bono,
                # al validarla nuevamente no se vuelve a enviar y se va a mantener la numeracion correctamente
                if responses:
                    for idx, response in enumerate(responses):
                        if response and response.BFEResultAuth:
                            with api.Environment.manage():
                                cr_to_use = new_cr or self.env.cr
                                new_env = api.Environment(cr_to_use, self.env.uid, self.env.context)
                                invoices.write_wsbfe_response(new_env, invoice_details[idx], response)
                                new_invoices = new_env['account.invoice'].browse(invoices.ids)
                                for invoice in new_invoices:
                                    # Busco, dentro del detalle de la respuesta, el segmento correspondiente a la factura
                                    number = document_book.next_number()
                                    if response.BFEResultAuth.Resultado == 'A':
                                        invoice.write({
                                            'cae': response.BFEResultAuth.Cae,
                                            'cae_due_date': datetime.strptime(
                                                response.BFEResultAuth.Fch_venc_Cae,
                                                '%Y%m%d'
                                            ) if response.BFEResultAuth.Fch_venc_Cae else None,
                                            'name': number
                                        })
                                    # Si el envio no fue exitoso, se retrocede un numero en el talonario para compensar el
                                    # aumento realizado al enviar la factura fallida
                                    else:
                                        document_book.prev_number()
                                self._commit(new_env)

                        if response and response.BFEResultAuth and response.BFEResultAuth.Resultado == 'R':
                            # Traemos el conjunto de errores
                            errores = '\n'.join(response.BFEResultAuth.Obs) \
                                if hasattr(response.BFEResultAuth.Obs, 'Observaciones') else ''
                            raise ValidationError('Hubo un error al intentar validar el documento\n{0}'.format(errores))

    def _set_electronic_bond_details(self, document_afip_code):
        """ Mapea los valores de ODOO al objeto FiscalElectronicBond"""

        denomination_c = self.env.ref('l10n_ar_afip_tables.account_denomination_c')
        codes_models_proxy = self.env['codes.models.relation']

        # Seteamos los campos generales del bono
        electronic_bond = wsbfe.invoice.FiscalElectronicBond(document_afip_code)
        electronic_bond.taxed_amount = self.amount_to_tax
        electronic_bond.untaxed_amount = self.amount_not_taxable if self.denomination_id != denomination_c else 0
        electronic_bond.exempt_amount = self.amount_exempt if self.denomination_id != denomination_c else 0
        electronic_bond.document_date = datetime.strptime(
            self.date_invoice or fields.Date.context_today(self),
            '%Y-%m-%d'
        )
        electronic_bond.customer_document_number = self.partner_id.vat
        electronic_bond.customer_document_type = codes_models_proxy.get_code(
            'partner.document.type',
            self.partner_id.partner_document_type_id.id
        )
        electronic_bond.mon_id = self.env['codes.models.relation'].get_code(
            'res.currency',
            self.currency_id.id
        )
        electronic_bond.mon_cotiz = self.convert_currency(
            from_currency=self.currency_id,
            to_currency=self.company_id.currency_id,
            d=self.date_invoice
        )
        electronic_bond.zone_id = 0 #Por el momento se utiliza 0

        # Agrego items
        electronic_bond.array_items = self.add_item_bond()

        # Agregamos impuestos y percepciones
        perceptions_amount = self.get_perceptions_amount()
        electronic_bond.reception_amount = perceptions_amount['total']
        electronic_bond.municipal_reception_amount = perceptions_amount['mun']
        electronic_bond.iibb_amount = perceptions_amount['gross_income']
        electronic_bond.pay_off_tax_amount = 0.00
        electronic_bond.rni_pay_off_tax_amount = 0.00
        electronic_bond.internal_tax_amount = 0.00

        return electronic_bond

    def add_item_bond(self):
        """ Mapea los valores de ODOO al objeto FiscalElectronicBondItem """
        array_items = []
        for line in self.invoice_line_ids:

            try:
                measurement_unit = self.env['codes.models.relation'].get_code(
                    'product.uom',
                    line.uom_id.id
                )
            except:
                measurement_unit = 98
            unit_price = line.price_unit
            bonification = ((line.price_unit * line.quantity) * (line.discount / 100)) if line.discount else 0.0
            iva_id = self.env['codes.models.relation'].get_code('account.tax', line.invoice_line_tax_ids[0].id) if line.invoice_line_tax_ids else 0
            product_ncm_code = self.check_product(line)
            ncm_code = product_ncm_code
            item = wsbfe.invoice.FiscalElectronicBondItem(ncm_code, line.product_id.name, line.quantity, measurement_unit, unit_price, bonification, iva_id)
            array_items.append(item)

        return array_items

    def check_product(self, invoice_line):
        """ Chequeo que tenga producto y este nomenclado"""
        if not invoice_line.product_id:
            raise ValidationError('Las lineas deben contener productos.')
        if not invoice_line.product_id.ncm_id:
            raise ValidationError('Es necesario que el producto {} este nomenclado.'.format(invoice_line.product_id.name))
        return invoice_line.product_id.ncm_id.code

    def _get_wsbfe(self):
        """
        Busca el objeto de wsbfe para utilizar sus servicios
        :return: instancia de Wsbfe
        """
        wsbfe_config = self.env['wsfe.configuration'].search([
            ('wsaa_token_id.name', '=', 'wsbfe'),
            ('company_id', '=', self.company_id.id),
        ])

        if not wsbfe_config:
            raise ValidationError('No se encontro una configuracion de bono fiscal electronico')

        access_token = wsbfe_config.wsaa_token_id.get_access_token()
        homologation = False if wsbfe_config.type == 'production' else True
        afip_wsbfe = wsbfe.wsbfe.Wsbfe(access_token, self.company_id.vat, homologation)

        return afip_wsbfe

    def get_perceptions_amount(self):
        total_amount = 0
        mun_perceptions_amount = 0
        gross_income_amount = 0
        for perception in self.perception_ids:
            total_amount += perception.amount
            if perception.perception_id.jurisdiction == 'municipal':
                mun_perceptions_amount += perception.amount
            if perception.perception_id.type == 'gross_income':
                gross_income_amount += perception.amount

        perceptions_amount = {'total': total_amount,
                              'mun': mun_perceptions_amount,
                              'gross_income': gross_income_amount}
        return perceptions_amount

    def write_wsbfe_response(self, env, invoice_detail, response):
        """ Escribe el envio y respuesta de un envio a AFIP """
        if response.BFEResultAuth:
            # Nos traemos el offset de la zona horaria para dejar en la base en UTC como corresponde
            offset = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).utcoffset().total_seconds() / 3600
            fch_proceso = datetime.now() - relativedelta(hours=offset)
            result = response.BFEResultAuth.Resultado
            date = fch_proceso
        else:
            result = "Error"
            date = fields.Datetime.now()

        env['wsfe.request.detail'].sudo().create({
            'invoice_ids': [(4, self.ids)],
            'request_sent': invoice_detail,
            'request_received': response,
            'result': result,
            'date': date,
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
