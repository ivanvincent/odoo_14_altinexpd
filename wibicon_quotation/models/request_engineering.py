from odoo import models, fields, api

class RequestEngineering(models.Model):
    _name = 'request.engineering'

    name = fields.Char(string='Name')
    state = fields.Selection([("draft","Draft"),("approve","Approve")], string='State', default='draft')
    line_ids = fields.One2many('request.engineering.line', 'request_engineering_id', 'Line')
    # type = fields.Selection([("from_quotation","Quotation"),("from_wo","Mor")], string='Type')
    type_id = fields.Many2one('request.engineering.type', string='Type')
    picking_id = fields.Many2one('stock.picking', string='Picking')
    quotation_id = fields.Many2one('quotation', string='Quotation')

    def action_approve(self):
        print("action_approve")
        type = self.type_id
        if self.state != 'approve':
            if type.name == 'Quotation':
                for line in self.line_ids:
                    move_line = []
                    location_id = type.picking_type_id.default_location_src_id.id
                    location_dest_id = type.picking_type_id.default_location_dest_id.id
                    hob = line.product_hob_id
                    baut = line.product_baut_id
                    # tonase = line.tonase_id.id
                    sepi = line.product_sepi_id
                    if hob:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : hob.name,
                            'product_id'      : hob.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : hob.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    if baut:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : baut.name,
                            'product_id'      : baut.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : baut.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    # if tonase:
                    #     move_line.append((0,0, {
                    #         'type_material'   : line.name,
                    #         'name'            : tonase.name,
                    #         'product_id'      : tonase.id,
                    #         'product_uom_qty' : 1,
                    #         'product_uom'     : baut.uom_id.id,
                    #         'location_id'     : location_id,
                    #         'location_dest_id': location_dest_id,
                    #     }))
                    if sepi:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : sepi.name,
                            'product_id'      : sepi.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : sepi.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    
                    picking_obj = self.env['stock.picking'].create({
                        'picking_type_id' : type.picking_type_id.id,
                        'location_id'     : location_id,
                        'location_dest_id': location_dest_id,
                        "origin"          : self.quotation_id.name,
                        'move_ids_without_package': move_line
                    })
                    line.picking_id = picking_obj.id
            else:
                for line in self.line_ids:
                    move_line = []
                    location_id = type.picking_type_id.default_location_src_id.id
                    location_dest_id = type.picking_type_id.default_location_dest_id.id
                    seweul_punch = line.product_seweul_punch_id
                    seweul_die = line.product_seweul_die_id
                    mall_tip = line.product_mall_tip_id
                    mall_siku = line.product_mall_siku_id
                    mall_die = line.product_mall_die_id
                    mall_honing = line.product_mall_honing_id
                    mall_holder = line.product_mall_holder_id
                    mall_cup_holder = line.product_mall_cup_holder_id
                    alat_bantu =  line.product_alat_bantu_id
                    
                    if seweul_punch:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : seweul_punch.name,
                            'product_id'      : seweul_punch.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : seweul_punch.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    if seweul_die:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : seweul_die.name,
                            'product_id'      : seweul_die.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : seweul_die.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    if mall_tip:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : mall_tip.name,
                            'product_id'      : mall_tip.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : mall_tip.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    if mall_siku:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : mall_siku.name,
                            'product_id'      : mall_siku.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : mall_siku.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    if mall_die:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : mall_die.name,
                            'product_id'      : mall_die.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : mall_die.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    if mall_honing:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : mall_honing.name,
                            'product_id'      : mall_honing.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : mall_honing.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    if mall_holder:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : mall_holder.name,
                            'product_id'      : mall_holder.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : mall_holder.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    if mall_cup_holder:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : mall_cup_holder.name,
                            'product_id'      : mall_cup_holder.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : mall_cup_holder.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    if alat_bantu:
                        move_line.append((0,0, {
                            'type_material'   : line.name,
                            'name'            : alat_bantu.name,
                            'product_id'      : alat_bantu.id,
                            'product_uom_qty' : 1,
                            'product_uom'     : alat_bantu.uom_id.id,
                            'location_id'     : location_id,
                            'location_dest_id': location_dest_id,
                        }))
                    
                    picking_obj = self.env['stock.picking'].create({
                        'picking_type_id' : type.picking_type_id.id,
                        'location_id'     : location_id,
                        'location_dest_id': location_dest_id,
                        "origin"          : self.quotation_id.name,
                        'move_ids_without_package': move_line
                    })
                    line.picking_id = picking_obj.id

            self.state = 'approve'


class RequestEngineeringLine(models.Model):
    _name = 'request.engineering.line'

    request_engineering_id = fields.Many2one('request.engineering', string='Engineering')
    name = fields.Char(string='Material')
    # value = fields.Char(string='Value')
    picking_id = fields.Many2one('stock.picking', string='Picking')


    #From Quotation
    product_id = fields.Many2one('product.product', string='Value')
    product_hob_id = fields.Many2one('product.product', string='Hob')
    qty_available_hob = fields.Float(string='Qty Available Hob')
    qty_available_sepi = fields.Float(string='Qty Available Sepi')
    product_baut_id = fields.Many2one('product.product', string='Baut')
    # product_tonase_id = fields.Many2one('product.product', string='Tonase')
    tonase_id = fields.Many2one('tonase', string='Tonase')
    product_sepi_id = fields.Many2one('product.product', string='Sepi')
    qty_available_sepi = fields.Float(string='Avb Sepi')
    no_drawing = fields.Char(string='No. Drawing')
    uk_bahan = fields.Char(string='Ukuran Bahan')

    #From MOR
    product_seweul_punch_id = fields.Many2one('product.product', string='Seweul Punch')
    product_seweul_die_id = fields.Many2one('product.product', string='Seweul Die')
    product_mall_tip_id = fields.Many2one('product.product', string='Mall Tip')
    product_mall_siku_id = fields.Many2one('product.product', string='Mall Siku')
    product_mall_leher_id = fields.Many2one('product.product', string='Mall Leher')
    product_mall_die_id = fields.Many2one('product.product', string='Mall Die')
    product_mall_honing_id = fields.Many2one('product.product', string='Mall Honing')
    product_mall_holder_id = fields.Many2one('product.product', string='Mall Holder')
    product_mall_cup_holder_id = fields.Many2one('product.product', string='Mall Cup Holder')
    product_alat_bantu_id = fields.Many2one('product.product', string='Alat Bantu')
    program_id = fields.Many2one('program', string='Program')
    workcenter_ids = fields.One2many('engineering.workcenter', 'request_line_id', 'Line')

    def action_open_workcenter(self):
        self.ensure_one()
        workcenter_obj = self.env['mrp.workcenter'].search([('is_default_in_engneering', '=', True)])
        if not self.workcenter_ids:
            self.write({
                'workcenter_ids' : [(0, 0, {'workcenter_id': w.id}) for w in workcenter_obj]
            })
        action = self.env.ref('wibicon_quotation.request_engineering_line_action').read()[0]
        action['name'] = '%s - %s' % (self.product_id.name, 'Workcenter')
        action['display_name'] = '%s - %s' % (self.product_id.name, 'Workcenter')
        action['res_id'] = self.id
        return action

class RequestEngineeringType(models.Model):
    _name = 'request.engineering.type'

    name = fields.Char(string='Name')
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')

class EngineeringWorkcenter(models.Model):
    _name = 'engineering.workcenter'

    sequence      = fields.Integer(string='No',compute="_get_sequence")
    workcenter_id = fields.Many2one('mrp.workcenter', string='Workcenter')
    date = fields.Date(string='Date')
    request_line_id = fields.Many2one('request.engineering.line', 'Engineering Line')

    def _get_sequence(self):
        seq = 0
        for line in self:
            seq +=1
            line.sequence = seq