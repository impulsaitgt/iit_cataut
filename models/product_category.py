from odoo import api, models, fields
from odoo.exceptions import ValidationError
from datetime import date

class ProductCategory(models.Model):
    _inherit = "product.category"

    caa_tipo_desc = fields.Selection([('Monto', 'Monto'), ('Porcentaje', 'Porcentaje')], default='Monto', string='Tipo de Descuento')
    caa_corr = fields.Char(string="Prefijo para correlativo", required=True)