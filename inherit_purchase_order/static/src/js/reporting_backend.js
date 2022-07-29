odoo.define("reporting.purchase_report_generic", function (require) {
  "use strict";

  let AbstractAction = require("web.AbstractAction");
  let core = require("web.core");
  let Dialog = require("web.Dialog");
  let Session = require("web.session");
  let ReportWidget = require("reporting.ReportJsWidget");

  let framework = require("web.framework");
  let QWeb = core.qweb;

  let _t = core._t;

  let purchase_report_generic = AbstractAction.extend({
    hasControlPanel: true,
    events: {},
    init: function (parent, action) {
      this._super.apply(this, arguments);
      this.actionManager = parent;
      this.given_context = Object.assign({}, Session.user_context);
      this.controller_url = action.context.url;
      if (action.context.context) {
        this.given_context = action.context.context;
      }
      this.given_context.active_id =
        action.params.active_id || action.context.active_id;
      this.given_context.model = action.context.active_model || false;
      this.given_context.ttype = action.context.ttype || false;
      this.given_context.auto_unfold = action.context.auto_unfold || false;
      this.given_context.report_type = action.params.report_type || false;
      this.given_context.lot_name = action.context.lot_name || false;
    },

    willStart: function () {
      let self = this;
      return Promise.all([this._super.apply(this, arguments), this.get_html()]);
    },

    set_html: function () {
      var self = this;
      var def = Promise.resolve();
      if (!this.report_widget) {
        this.report_widget = new ReportWidget(this, this.given_context);
        def = this.report_widget.appendTo(this.$(".o_content"));
      }

      console.log("==============");
      console.log("report backend");
      console.log(this.report_widget);
      console.log("==============");

      return def.then(function () {
        self.report_widget.$el.html(self.html);
        self.report_widget.$el
          .find(".o_report_heading")
          .html("<h1>Purchase All Vendor Report</h1>");
        if (self.given_context.auto_unfold) {
          _.each(self.$el.find(".fa-caret-right"), function (line) {
            self.report_widget.autounfold(line, self.given_context.lot_name);
          });
        }
      });
    },

    get_html: async function () {
      const { html } = await this._rpc({
        args: [this.given_context],
        method: "get_html",
        model: "purchase.custom.report",
      });
      this.html = html;
      console.log("==============");
      console.log(this);
      console.log("==============");
      this.renderButtons();
    },

    start: async function () {
      this.controlPanelProps.cp_content = { $buttons: this.$buttons };
      await this._super(...arguments);
      this.set_html();
    },

    destroy: function () {
      let self = this;
      this._super();
    },
    do_show: function () {
      this._super();
      // this.update_cp();
    },
  });

  core.action_registry.add("purchase_report_generic", purchase_report_generic);

  return purchase_report_generic;
});
