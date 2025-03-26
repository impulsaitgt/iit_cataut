from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RangoAutorizacion(models.Model):
    _name = 'caa.rango.autorizacion'
    _description = 'Rangos para autorizacion de precios especiales'

    name = fields.Char(string="Rango",required=True)
    user_id = fields.Many2many(string="Usuario(s)", required=True, comodel_name="res.users")
    monto_inicial_autorizado = fields.Float(string="Desde", default=0)
    monto_final_autorizado = fields.Float(string="Hasta", default=0)
    category_id = fields.Many2one(string="Categoria de Productos", required=True, comodel_name="product.category")
    caa_tipo_desc = fields.Selection(string="Monto/Porcentaje", related="category_id.caa_tipo_desc")
    company_id = fields.Many2one(comodel_name='res.company', required=True)

    _sql_constraints = [
        ('referencia_unica', 'unique(name)', "Ese rango ya existe especifica otro nombre")
    ]

    @api.model
    def create(self, vals):
        vals['company_id'] = self.env.company.id
        rangos = self.env['caa.rango.autorizacion'].search([('company_id', '=', self.env.company.id),
                                                            ('category_id', '=', vals['category_id'])],
                                                          order='monto_inicial_autorizado')
        resultado, mensaje = self.valida(vals, rangos)

        if not resultado:
            raise ValidationError(mensaje)

        res = super(RangoAutorizacion, self).create(vals)
        return res

    def write(self, vals):
        if ('monto_inicial_autorizado' in vals) or ('monto_final_autorizado' in vals):
            if not 'monto_inicial_autorizado' in vals:
                vals['monto_inicial_autorizado'] = self.monto_inicial_autorizado
            if not 'monto_final_autorizado' in vals:
                vals['monto_final_autorizado'] = self.monto_final_autorizado
            rangos = self.env['sol.rango.autorizacion'].search([('company_id', '=', self.env.company.id),
                                                                ('category_id', '=', self.category_id.id),
                                                                ('id', '!=', self.id)],
                                                              order='monto_inicial_autorizado')
            resultado, mensaje = self.valida(vals, rangos)

            if not resultado:
                raise ValidationError(mensaje)
        res = super(RangoAutorizacion, self).write(vals)
        return res


    def valida(self, vals, rangos):
        result = False
        mensaje = 'Exito'
        if vals['monto_inicial_autorizado'] >= vals['monto_final_autorizado']:
            mensaje = 'El rango final debe ser mayor al rango inicial'
        else:
            result = True
            for rango in rangos:
                if (((vals['monto_inicial_autorizado'] >= rango.monto_inicial_autorizado) and
                     (vals['monto_inicial_autorizado'] <= rango.monto_final_autorizado)) or
                    ((vals['monto_final_autorizado'] >= rango.monto_inicial_autorizado) and
                     (vals['monto_final_autorizado'] <= rango.monto_final_autorizado))):
                    result = False
                    mensaje = 'Existe un rango que entra en conflicto con este rango, por favor revisar '
        return result, mensaje