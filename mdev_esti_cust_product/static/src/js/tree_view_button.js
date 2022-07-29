odoo.define('mdev_esti_cust_product.tree_view_button', function (require) {
    "use strict";

    var core = require('web.core');
    var ListView = require('web.ListView');
    var ListController = require("web.ListController");

    var IncludeListView = {

        renderButtons: function() {
            this._super.apply(this, arguments);

            if (this.modelName === "res.partner.product") {
                var summary_apply_leave_btn = this.$buttons.find('button.o_create_mdev_upload_res_partner_product');
                summary_apply_leave_btn.on('click', this.proxy('create_mdev_upload_res_partner_product'))
            }

        },
        create_mdev_upload_res_partner_product: function(){
            var self = this;
            var action = {
                type: "ir.actions.act_window",
                name: "Customer Products - Upload",
                res_model: "res.partner.product.xls",
                views: [[false,'form']],
                target: 'new',
                views: [[false, 'form']],
                view_type : 'form',
                view_mode : 'form',
                flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
            };
            return this.do_action(action);
        },

    };
    ListController.include(IncludeListView);
});