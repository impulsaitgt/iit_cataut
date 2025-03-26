from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Marca(models.Model):
    _name = 'caa.marca'
    _description = 'Marcas'

    name = fields.Char(string="Marca",required=True)
    caa_corr = fields.Char(string="Prefijo para correlativo", required=True)
