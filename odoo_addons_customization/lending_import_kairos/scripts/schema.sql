-- ----------------------------------------------------------
-- MDB Tools - A library for reading MS Access database files
-- Copyright (C) 2000-2011 Brian Bruns and others.
-- Files in libmdb are licensed under LGPL and the utilities under
-- the GPL, see COPYING.LIB and COPYING files respectively.
-- Check out http://mdbtools.sourceforge.net
-- ----------------------------------------------------------

-- That file uses encoding UTF-8

CREATE TABLE [ate]
 (
	[Clave]			Long Integer, 
	[Descripcion]			Text (90), 
	[Estado]			Text (2)
);

CREATE TABLE [atp]
 (
	[ClaveAccion]			Long Integer, 
	[ClaveProducto]			Long Integer, 
	[Especificacion]			Text (12), 
	[ViaAdministracion]			Text (12), 
	[Medio]			Text (12), 
	[Importancia]			Long Integer
);

CREATE TABLE [dro]
 (
	[Clave]			Long Integer, 
	[Descripcion]			Text (90), 
	[Estado]			Text (2)
);

CREATE TABLE [drp]
 (
	[ClaveDroga]			Long Integer, 
	[ClaveProducto]			Long Integer, 
	[Especificacion]			Text (12), 
	[ViaAdministracion]			Text (12), 
	[Medio]			Text (12), 
	[Importancia]			Long Integer
);

CREATE TABLE [iom]
 (
	[ClaveProducto]			Long Integer, 
	[ClavePresentacion]			Long Integer, 
	[Precio]			Text (30)
);

CREATE TABLE [lab]
 (
	[Clave]			Long Integer, 
	[Descripcion]			Text (30), 
	[RazonSocial]			Text (100), 
	[Estado]			Text (2)
);

CREATE TABLE [pam]
 (
	[ClaveProducto]			Long Integer, 
	[ClavePresentacion]			Long Integer, 
	[Precio]			Text (30)
);

CREATE TABLE [prc]
 (
	[ClaveProducto]			Long Integer, 
	[ClavePresentacion]			Long Integer, 
	[PrecioPublico]			Text (30), 
	[FechaVigencia]			DateTime
);

CREATE TABLE [pre]
 (
	[ClaveProducto]			Long Integer, 
	[ClavePresentacion]			Long Integer, 
	[Descripcion]			Text (120), 
	[CodigoPAMI]			Text (2), 
	[CodigoTroquel]			Text (18), 
	[CodigoIOMA]			Text (2), 
	[CodigoSIFAR]			Text (2), 
	[Especificacion]			Text (12), 
	[ViaAdministracion]			Text (12), 
	[Medio]			Text (12), 
	[UsoNormatizado]			Text (2), 
	[CodigoBarras]			Text (28), 
	[Estado]			Text (2), 
	[EsCanasta]			Text (2)
);

CREATE TABLE [pro]
 (
	[Clave]			Long Integer, 
	[Descripcion]			Text (80), 
	[ClaveLab]			Long Integer, 
	[ClaveLabCom]			Long Integer, 
	[CodigoOrigen]			Text (2), 
	[CodigoPsico]			Text (2), 
	[CodigoVenta]			Text (2), 
	[CodigoEstup]			Text (2), 
	[Estado]			Text (2)
);


