from odoo import models,fields,api


class AutorizacionPendiente(models.TransientModel):
    _name = 'sol.autorizacion.pendiente.wizard'
    _description = 'Muestra autorizaciones pendientes'

    estado = fields.Char(string="Estatus", default='Autorizaciones Pendientes')
    sale_id = fields.Many2one(string="Pedido de Venta", comodel_name="sale.order", readonly=True)
    autorizacion_lines = fields.One2many(comodel_name="sol.autorizacion.pendiente.line.wizard", inverse_name="autorizacion_id")

    @api.onchange('estado')
    def onchanche_estado(self):
        self.sale_id = self.env['sale.order'].search([('id', '=', self.env.context['active_id'])])

        for linea in self.sale_id.order_line:
            if linea.sol_requiere_autorizacion:
                vals = {
                    'autorizacion_id': self.id,
                    'user_id': linea.sol_supervisores,
                    'producto_id': linea.product_id.id
                }
                self.env['sol.autorizacion.pendiente.line.wizard'].create(vals)



class AutorizacionPendienteLine(models.TransientModel):
    _name = 'sol.autorizacion.pendiente.line.wizard'
    _descripcion = 'Detalle de autorizaciones Pendientes'

    autorizacion_id = fields.Many2one(comodel_name="sol.autorizacion.pendiente.wizard")
    user_id = fields.Many2many(string="Supervisores", comodel_name="res.users")
    producto_id = fields.Many2one(string="Producto", comodel_name="product.template")