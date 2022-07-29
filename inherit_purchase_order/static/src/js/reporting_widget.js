odoo.define("reporting.ReportJsWidget", function (require) {
  "use strict";

  let core = require("web.core");
  let Widget = require("web.Widget");
  let QWeb = core.qweb;

  let _t = core._t;

  let ReportJsWidget = Widget.extend({
    events: {
      'click span.o_purchase_reports_foldable': 'fold',
      'click span.o_purchase_reports_unfoldable': 'unfold',
      'click .o_purchase_reports_web_action': 'boundLink',

    },
    init: function (parent) {
      this._super.apply(this, arguments);
      this.title = parent.title;
      console.log('==============');
      console.log('report widget');
      console.log(this);
      console.log('==============');
    },

    willStart: function () {
      let self = this;
      return this._super.apply(this, arguments);
    },

    start: function () {
      let self = this;
      QWeb.add_template("/inherit_purchase_order/static/src/xml/purchase_report_line.xml");
      return this._super.apply(this.arguments);
    },

    boundLink: function(e) {
      e.preventDefault();
      console.log('model')
      console.log($(e.target).data('res-model'))
      return this.do_action({
          type: 'ir.actions.act_window',
          res_model: $(e.target).data('res-model'),
          res_id: $(e.target).data('active-id'),
          views: [[false, 'form']],
          target: 'current'
      });
  },

    destroy: function () {
      let self = this;
      this._super();
    },
  });

  return ReportJsWidget;
});
