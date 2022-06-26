from odoo import api, models, fields
from odoo.exceptions import ValidationError
from datetime import date

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def action_confirm(self):
        autorizado = True
        for linea in self.order_line:
            if not (linea.sol_autorizado and (linea.sol_precio_solicitado == linea.price_unit)):
                if linea.product_id.categ_id.sol_tipo_desc == 'Monto':
                    descuento = linea.product_id.lst_price - linea.price_reduce
                else:
                    descuento = (linea.product_id.lst_price - linea.price_reduce) / linea.product_id.lst_price * 100

                if descuento > 0:
                    rango = self.env['sol.rango.autorizacion'].search([('company_id', '=', self.env.company.id),
                                                                       ('category_id', '=', linea.product_id.categ_id.id),
                                                                       ('monto_inicial_autorizado', '<=', descuento),
                                                                       ('monto_final_autorizado', '>=', descuento)],
                                                                       order='monto_inicial_autorizado')
                    if rango:
                        vals = {
                            'sol_supervisores': rango.user_id,
                            'sol_autorizado': False,
                            'sol_requiere_autorizacion': True,
                            'sol_precio': linea.product_id.lst_price,
                            'sol_precio_solicitado': linea.price_reduce,
                            'sol_descuento': linea.product_id.lst_price - linea.price_reduce,
                            'sol_fecha_autorizado': None
                        }
                        linea_act = self.env['sale.order.line'].search([('id', '=', linea.id)])
                        linea_act.write(vals)
                        autorizado = False
                    else:
                        vals = {
                            'sol_supervisores': None,
                            'sol_autorizado': True,
                            'sol_requiere_autorizacion': False,
                            'sol_precio': linea.product_id.lst_price,
                            'sol_precio_solicitado': linea.price_unit,
                            'sol_descuento': descuento,
                            'sol_fecha_autorizado': date.today()
                        }
                        linea_act = self.env['sale.order.line'].search([('id', '=', linea.id)])
                        linea_act.write(vals)

        if autorizado:
            res = super(SaleOrder, self).action_confirm()
        else:
            res = self.action_muestra_autorizaciones()
        return res


    def action_muestra_autorizaciones(self):
        action = self.env.ref('iit_solares.action_autorizacion_pendiente').read()[0]
        action['domain'] = [('sol.autorizacion.pendiente.wizard.sale_id', '=', self.id)]
        return action

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sol_autorizado = fields.Boolean(string='Autorizado', default=True)
    sol_requiere_autorizacion = fields.Boolean(string='Requiere Autorizacion', default=False)
    sol_supervisores = fields.Many2many(string="Superviso(es)", comodel_name="res.users")
    sol_autorizo = fields.Many2one(string="Usuario que autorizo", comodel_name="res.users")
    sol_fecha_autorizado = fields.Date(string="Fecha de autorizacion")
    sol_precio = fields.Float(string="Precio Lista", default=0)
    sol_precio_solicitado = fields.Float(string="Precio Solicitado", default=0)
    sol_descuento = fields.Float(string="Descuento Requerido", default=0)
    sol_etiqueta_autorizacion = fields.Char(string="Autorizado", compute="_etiquetas_")
    sol_etiqueta_requiere_autorizacion = fields.Char(string="Requiere Autorizacion", compute="_etiquetas_")
    sol_partner_name = fields.Char(string="Cliente", related="order_id.partner_id.name")

    def _etiquetas_(self):
        for linea in self:
            if linea.sol_autorizado:
                linea.sol_etiqueta_autorizacion = "Autorizado"
            else:
                linea.sol_etiqueta_autorizacion = "No Autorizado"

            if linea.sol_requiere_autorizacion:
                linea.sol_etiqueta_requiere_autorizacion = "Requiere Autornizacion"
            else:
                linea.sol_etiqueta_requiere_autorizacion = "Autorizacion Automatica"


    def action_autoriza(self):
        permite_autorizar = False
        for usuario in self.sol_supervisores:
            if self.env.user.id == usuario.id:
                permite_autorizar = True

        if permite_autorizar:
            self.sol_autorizado = True
            self.sol_fecha_autorizado = date.today()
            self.sol_autorizo = self.env.user
        else:
            raise ValidationError('Usted no tiene derechos para autorizar, solo los supervisores asignados!!')

