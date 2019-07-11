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

from openerp import models, fields
from openerp.exceptions import ValidationError
import os
import zipfile
import base64
import StringIO
import glob

PADRON_DELIMITER = ';'
QTY_DELIMITER = 11


class PadronIIBBCABAWizard(models.TransientModel):
    _name = 'padron.iibb.caba.wizard'
    _description = 'Importacion padron IIBB CABA'

    file = fields.Binary(string='Archivo', filename="filename", required=True)
    filename = fields.Char(string='Nombre Archivo')

    @staticmethod
    def _normalize_padron(filepath, newfilepath):
        try:
            with open(filepath) as oldfile, open(newfilepath, 'w') as newfile:
                for line in oldfile:
                    if line.count(PADRON_DELIMITER) <= QTY_DELIMITER:
                        newfile.write(line)
        except:
            raise ValidationError('Ha ocurrido un error al intentar normalizar el archivo.')

    def import_zip(self):
        """ Importa archivo de IIBB CABA y genera las reglas para los partners correspondientes"""
        padron_caba_path = "/tmp/padron_caba/"
        if self.filename.split(".")[-1].lower() != "zip":
            raise ValidationError('Error\nDebe utilizar un archivo ZIP.')
        # Creo el directorio si no existe
        if not os.path.isdir(padron_caba_path):
            os.mkdir(padron_caba_path)
        try:
            zip_ref = zipfile.ZipFile(StringIO.StringIO(base64.b64decode(self.file)))
        except:
            raise ValidationError('Error de formato de archivo, debe utilizar un archivo ZIP')
        # Extraigo todos los archivos en el directorio generado
        zip_ref.extractall(padron_caba_path)
        zip_ref.close()
        # Busco todos los archivos txt dentro del directorio
        files_txt = glob.glob(padron_caba_path + "*.txt")
        if files_txt:
            txt_file = files_txt[0]
            normalize_file_path = '{}.ok'.format(txt_file)
            self._normalize_padron(txt_file, normalize_file_path)
            # Le doy permisos al archivo extraido
            os.chmod(txt_file, 0o777)
            try:
                # Copio los registros del archivo en la tabla
                self.env['padron.iibb.caba'].truncate_table()
                self.env['padron.iibb.caba'].action_import(normalize_file_path)
            except:
                raise ValidationError('Ha ocurrido un error al intentar cargar el padron. Vuelva a intentarlo.')
        # Elimino archivos
        os.system("rm -r /tmp/padron_caba")
        
        self.massive_update_iibb_caba_values()

    def massive_update_iibb_caba_values(self):
        self.massive_update_iibb_caba_perceptions()
        self.massive_update_iibb_caba_retentions()

    def massive_update_iibb_caba_perceptions(self):
        """ Actualiza el valor de percepcion de IIBB de todos los partners """
        perception = self.env['perception.perception'].get_caba_perception()
        self.env['perception.partner.rule'].delete_rules_for(perception)
        self.env.cr.execute(
            """INSERT into perception_partner_rule (date_from, date_to, percentage, perception_id, partner_id, company_id)
               SELECT 
                    to_date(padron_iibb_caba.date_from, 'DDMMYY') as date_from, 
                    to_date(padron_iibb_caba.date_to, 'DDMMYY') as date_to,
                    cast(replace(perception_aliquot, ',', '.') as float) as percentage, {perception_id} as perception_id,
                    res_partner.id as partner_id,
                    res_partner.company_id as company_id
                FROM res_partner
                JOIN padron_iibb_caba on res_partner.vat = padron_iibb_caba.cuit and up_down_flag != 'B'
                WHERE res_partner.parent_id is null and res_partner.vat is not null and res_partner.active = True;"""
                .format(perception_id=perception.id)
        )

    def massive_update_iibb_caba_retentions(self):
        """ Actualiza el valor de percepcion de IIBB de todos los partners """
        retention = self.env['retention.retention'].get_caba_retention()
        self.env['retention.partner.rule'].delete_rules_for(retention)
        self.env.cr.execute(
            """INSERT into retention_partner_rule (date_from, date_to, percentage, retention_id, partner_id, company_id)
               SELECT 
                    to_date(padron_iibb_caba.date_from, 'DDMMYY') as date_from, 
                    to_date(padron_iibb_caba.date_to, 'DDMMYY') as date_to,
                    cast(replace(retention_aliquot, ',', '.') as float) as percentage, {retention_id} as retention_id,
                    res_partner.id as partner_id,
                    res_partner.company_id as company_id
                FROM res_partner
                JOIN padron_iibb_caba on res_partner.vat = padron_iibb_caba.cuit and up_down_flag != 'B'
                WHERE res_partner.parent_id is null and res_partner.vat is not null and res_partner.active = True;"""
                .format(retention_id=retention.id)
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
