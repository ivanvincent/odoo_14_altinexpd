odoo.define('mdev_estimate.tree_view_button', function (require) {
    "use strict";

    var core = require('web.core');
    var ListView = require('web.ListView');
    var ListController = require("web.ListController");

    var IncludeListView = {

        renderButtons: function() {
            this._super.apply(this, arguments);

            if (this.modelName === "estimate") {
                var summary_apply_leave_btn = this.$buttons.find('button.o_create_mdev_estimate');
                summary_apply_leave_btn.on('click', this.proxy('create_mdev_estimate'))
            }

            if (this.modelName === "estimate") {
                var summary_apply_leave_btn = this.$buttons.find('button.o_create_mdev_estimate_uploader');
                summary_apply_leave_btn.on('click', this.proxy('create_mdev_estimate_uploader'))
            }

            if (this.modelName === "estimate") {
                var summary_apply_leave_btn = this.$buttons.find('button.o_mdev_estimate_action');
                summary_apply_leave_btn.on('click', this.proxy('mdev_estimate_action'))
            }

        },
        create_mdev_estimate: function(){
            var self = this;
            var action = {
                type: "ir.actions.act_window",
                name: "Estimate Generator",
                res_model: "estimate.generator.wizard",
                views: [[false,'form']],
                target: 'new',
                views: [[false, 'form']],
                view_type : 'form',
                view_mode : 'form',
                flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
            };
            return this.do_action(action);
        },

        create_mdev_estimate_uploader: function(){
            var self = this;
            var action = {
                type: "ir.actions.act_window",
                name: "Estimate Uploader",
                res_model: "estimate.uploader.wizard",
                views: [[false,'form']],
                target: 'new',
                views: [[false, 'form']],
                view_type : 'form',
                view_mode : 'form',
                flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
            };
            return this.do_action(action);
        },

        mdev_estimate_action: function(){
            var self = this;
            var action = {
                type: "ir.actions.act_window",
                name: "Estimate Action",
                res_model: "estimate.action.wizard",
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