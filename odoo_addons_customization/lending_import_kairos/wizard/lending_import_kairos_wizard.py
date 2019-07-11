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
import base64
import os
from datetime import datetime

MEDICINE_INITIAL = 'M'


class LendingImportKairosWizard(models.TransientModel):
    _name = 'lending.import.kairos.wizard'

    file = fields.Binary(string='Archivo', filename="filename", required=True)
    filename = fields.Char(string='Nombre Archivo')

    def import_file(self):
        """ Importacion de base de datos del kairos """
        kairos_path = "/tmp/kairos/"
        csv_path = "/tmp/kairos/csv/"
        if self.filename.split(".")[-1].lower() != "mdb":
            raise ValidationError('Error\nDebe utilizar un archivo mdb.')
        # Creo directorios si no existen
        if not os.path.isdir(kairos_path):
            os.mkdir(kairos_path)
        if not os.path.isdir(csv_path):
            os.mkdir(csv_path)
        # Elimino archivos
        os.system("rm -r /tmp/kairos/csv/*.csv")
        os.system("rm -r /tmp/kairos/*.mdb")
        # Guardo el archivo en el servidor
        mdb_path = kairos_path + "kairos.mdb"
        tmp_file = open(mdb_path, "wb")
        tmp_file.write(base64.b64decode(self.file))
        # Ejecuto el scripts
        os.system('bash /opt/odoo_addons_customization/lending_import_kairos/scripts/create_csv.sh')
        # Itero todos los archivos del
        for f in os.listdir(csv_path):
            # Me traigo el nombre del archivo que es el mismo nombre que la tabla
            file_name = os.path.splitext(f)[0]
            # Copio los datos del archivo en la tabla
            self.env.cr.execute("""
                    COPY {} FROM '{}' WITH DELIMITER ';' CSV HEADER encoding 'UTF-8' """.format(
                file_name, csv_path + f)
            )
        # Busco los datos necesarios de cada tabla para generar los registros en el sistema
        price_lines = self.search_price_lines()
        # Itero la lista de tuplas
        for line in price_lines:
            # Busco la prestacion de la linea
            medicine = self.search_medicine(line)
            if not medicine:
                # Si no existe la creo
                medicine = self.create_medicine(line)
            # Creo el registro de la medicamento con el precio
            self.create_kairos_line(line, medicine)
        # Elimino datos
        for f in os.listdir(csv_path):
            # Me traigo el nombre del archivo que es el mismo nombre que la tabla
            file_name = os.path.splitext(f)[0]
            # Elimino los datos de las tablas
            self.env.cr.execute("DELETE FROM {}".format(file_name))

    def search_price_lines(self):
        """ Busco en las tablas generadas por el archivo mdb los registros con precios y
         busco los datos necesarios para el sistema"""
        self.env.cr.execute('''SELECT 
                pro."Descripcion", pre."Descripcion", prc."PrecioPublico", 
                pro."Clave", prc."ClavePresentacion", prc."FechaVigencia", lab."Descripcion", string_agg(distinct 
                dro."Descripcion", ', ') as "DescripcionDroga" 
                FROM 
                prc, pro, lab, pre 
                LEFT JOIN 
                drp on drp."ClaveProducto" = pre."ClaveProducto" 
                LEFT JOIN 
                dro on dro."Clave" = drp."ClaveDroga" 
                WHERE 
                pre."ClaveProducto" = prc."ClaveProducto" and 
                pre."ClavePresentacion" = prc."ClavePresentacion" and 
                pre."ClaveProducto" = pro."Clave" and 
                pro."ClaveLab" = lab."Clave" 
                GROUP BY 
                pro."Descripcion", pre."Descripcion", 
                prc."PrecioPublico", pro."Clave", prc."ClavePresentacion", prc."FechaVigencia", lab."Descripcion", 
                pre."ClaveProducto" 
                ORDER BY 
                pre."ClaveProducto", prc."ClavePresentacion"''', )

        # Devuelvo la busqueda del query
        # [(DESCRIPCION_PRODUCTO, DESCRIPCION_PRESENTACION, PRECIO_PUBLICO, CLAVE_PRODUCTO,
        # CLAVE_PRESENTACION, DESCRIPCION_LABORATIORIO, FECHA_VIGENCIA, DESCRIPCION_DROGA)]
        return self.env.cr.fetchall()

    def search_medicine(self, line):
        """ Busco si existe la prestacion con el codigo de kairos"""
        code = MEDICINE_INITIAL + str(line[3]) + str(line[4])
        medicine = self.env['lending'].search([
            ('code', '=', code), ('description_presentation', '=', line[1]), ('description_laboratory', '=', line[6]),
            ('description_drug', '=', line[7]), ('description_product', '=', line[0])
        ], limit=1)
        return medicine

    def create_medicine(self, line):
        """ Creo la medicina como prestacion con sus descripciones"""
        code = MEDICINE_INITIAL + str(line[3]) + str(line[4])
        medicine = self.env['lending'].create({
            'code': code,
            'name': line[0],
            'medicine': True,
            'description_presentation': line[1],
            'description_laboratory': line[6],
            'description_drug': line[7],
            'description_product': line[0],
        })
        return medicine

    def create_kairos_line(self, line, lending):
        """
        Busco el registro de Kairos correspondiente al medicamento (lo creo si no existe) y cargo un registro en la
        grilla con la fecha y el precio del archivo
        @param line: línea con los datos del archivo de Kairos
        @param lending: objeto lending correspondiente al medicamento
        """
        kairos_line = self.search_kairos_line(lending)
        if not kairos_line:
            kairos_line = self.env['lending.kairos.line'].create({
                'lending_id': lending.id,
            })
        date = datetime.strptime(line[5], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        value_line = self.search_kairos_value_line(kairos_line, date)
        if not value_line:
            self.env['lending.kairos.value.line'].create({
                'kairos_id': kairos_line.id,
                'value': float(line[2]),
                'date': date
            })
            kairos_line.write({'date': date, 'value': float(line[2])})

    def search_kairos_line(self, lending):
        """ Busco si el medicamento ya está cargado """
        price_line = self.env['lending.kairos.line'].search([
            ('lending_id', '=', lending.id),
        ], limit=1)
        return price_line

    def search_kairos_value_line(self, kairos, date):
        """ Busco si el registro de Kairos ya tiene un valor para una fecha determinada """
        value_line = self.env['lending.kairos.value.line'].search([
            ('kairos_id', '=', kairos.id),
            ('date', '=', date),
        ], limit=1)
        return value_line

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
