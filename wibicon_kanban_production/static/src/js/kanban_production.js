odoo.define("wibicon_kanban_production.kanban_production_view", function (require) {
    "use strict";

    let AbstractAction = require("web.AbstractAction");
    let core = require("web.core");
    let Dialog = require("web.Dialog");
    let Session = require("web.session");
    let field_utils = require("web.field_utils");
    let time = require("web.time");
    let QWeb = core.qweb;
    let _t = core._t;


    let KanbanProductionAction = AbstractAction.extend({
        template: "KanbanProduction",
        init: function (parent) {
            this._super.apply(this, arguments);
            this.session = Session;
        },


        willStart: function () {
            let self = this;
            return this._super.apply(this, arguments);
        },

        start: function () {
            let self = this;
            this.initial_render = true;
            this.context = this.searchModelConfig.context;
            this.renderController();


        },

        renderController: async function () {
            let self = this;

            let workcenters = await this._rpc({
                model: "mrp.workcenter",
                method: "search_read",
                kwargs: {
                    // domain: [["invoice_id", "=", line_id]],
                    fields: ["name"],
                },
                }).then((result) => {
                    self.list_workcenters = result
                });

                let data = await this._rpc({
                    model: "mrp.production",
                    method: "get_data_kanban_production",
                    kwargs: {
                        // domain: [["invoice_id", "=", line_id]],
                        // fields: ["name"],
                    },
                    }).then((result) => {
                        self.data_record = result
                    });
    
                

            if (this.initial_render) {
                console.log(self.list_workcenters);
                // self.$(".kb-main").html(QWeb.render("KanbanProduction",{
                //     title: "Kanban Production"
                // }));
                this.$el.html(QWeb.render('KanbanProduction', {
                    title: 'Kanban Production',
                    list_workcenter: self.list_workcenters,
                    data_record: self.data_record
                })
                );   
                return $.when();
            }
        },

        destroy: function () {
            let self = this;
            this._super();
        },
    });

    core.action_registry.add("kanban_production_view", KanbanProductionAction);
});