from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from datetime import date

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def action_confirm(self):
        autorizado = True
        for linea in self.order_line:
            if not (linea.caa_autorizado and (linea.caa_precio_solicitado == linea.price_unit)):
                if linea.product_id.categ_id.caa_tipo_desc == 'Monto':
                    descuento = linea.product_id.lst_price - linea.price_reduce_taxinc
                else:
                    descuento = (linea.product_id.lst_price - linea.price_reduce_taxinc) / linea.product_id.lst_price * 100

                if descuento > 0:
                    rango = self.env['caa.rango.autorizacion'].search([('company_id', '=', self.env.company.id),
                                                                       ('category_id', '=', linea.product_id.categ_id.parent_id.id),
                                                                       ('monto_inicial_autorizado', '<=', descuento),
                                                                       ('monto_final_autorizado', '>=', descuento)],
                                                                       order='monto_inicial_autorizado')
                    if rango:
                        vals = {
                            'caa_supervisores': rango.user_id,
                            'caa_autorizado': False,
                            'caa_requiere_autorizacion': True,
                            'caa_precio': linea.product_id.lst_price,
                            'caa_precio_solicitado': linea.price_reduce_taxinc,
                            'caa_descuento': linea.product_id.lst_price - linea.price_reduce_taxinc,
                            'caa_fecha_autorizado': None
                        }
                        linea_act = self.env['sale.order.line'].search([('id', '=', linea.id)])
                        linea_act.write(vals)
                        autorizado = False
                    else:
                        vals = {
                            'caa_supervisores': None,
                            'caa_autorizado': True,
                            'caa_requiere_autorizacion': False,
                            'caa_precio': linea.product_id.lst_price,
                            'caa_precio_solicitado': linea.price_unit,
                            'caa_descuento': descuento,
                            'caa_fecha_autorizado': date.today()
                        }
                        linea_act = self.env['sale.order.line'].search([('id', '=', linea.id)])
                        linea_act.write(vals)

        if autorizado:
            res = super(SaleOrder, self).action_confirm()
        else:
            res = self.action_muestra_autorizaciones()
        return res


    def action_muestra_autorizaciones(self):
        action = self.env.ref('iit_cataut.action_autorizacion_pendiente').read()[0]
        action['domain'] = [('caa.autorizacion.pendiente.wizard.sale_id', '=', self.id)]
        return action

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    caa_autorizado = fields.Boolean(string='Autorizado', default=True)
    caa_requiere_autorizacion = fields.Boolean(string='Requiere Autorizacion', default=False)
    caa_supervisores = fields.Many2many(string="Superviso(es)", comodel_name="res.users")
    caa_autorizo = fields.Many2one(string="Usuario que autorizo", comodel_name="res.users")
    caa_fecha_autorizado = fields.Date(string="Fecha de autorizacion")
    caa_precio = fields.Float(string="Precio Lista", default=0)
    caa_precio_solicitado = fields.Float(string="Precio Solicitado", default=0)
    caa_descuento = fields.Float(string="Descuento Requerido", default=0)
    caa_etiqueta_autorizacion = fields.Char(string="Autorizado", compute="_etiquetas_")
    caa_etiqueta_requiere_autorizacion = fields.Char(string="Requiere Autorizacion", compute="_etiquetas_")
    caa_partner_name = fields.Char(string="Cliente", related="order_id.partner_id.name")

    def _etiquetas_(self):
        for linea in self:
            if linea.caa_autorizado:
                linea.caa_etiqueta_autorizacion = "Autorizado"
            else:
                linea.caa_etiqueta_autorizacion = "No Autorizado"

            if linea.caa_requiere_autorizacion:
                linea.caa_etiqueta_requiere_autorizacion = "Requiere Autornizacion"
            else:
                linea.caa_etiqueta_requiere_autorizacion = "Autorizacion Automatica"


    def action_autoriza(self):
        permite_autorizar = False
        for usuario in self.caa_supervisores:
            if self.env.user.id == usuario.id:
                permite_autorizar = True

        if permite_autorizar:
            self.caa_autorizado = True
            self.caa_fecha_autorizado = date.today()
            self.caa_autorizo = self.env.user
        else:
            raise ValidationError('Usted no tiene derechos para autorizar, solo los supervisores asignados!!')

