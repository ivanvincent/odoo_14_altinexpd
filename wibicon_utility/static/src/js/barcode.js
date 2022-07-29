odoo.define("wibicon_utility.BarcodeFormView", function (require) {
  "use strict";

  var BarcodeEvents = require("barcodes.BarcodeEvents"); // handle to trigger barcode on bus
  var concurrency = require("web.concurrency");
  var core = require("web.core");
  var Dialog = require("web.Dialog");
  var FormController = require("web.FormController");
  var FormRenderer = require("web.FormRenderer");

  var _t = core._t;

  FormController.include({
    /**
     * add default barcode commands for from view
     *
     * @override
     */
    init: function () {
      this._super.apply(this, arguments);
      core.bus.on("barcode_scanned", this, this._onBarcodeScanned);

    },

    _onBarcodeScanned: function (barcode) {
      var self = this;
      if (this.initialState.model === 'stock.picking') {
        self._rpc({
          model: "stock.picking",
          method: "barcode_scan",
          args: [
            barcode,
            self.initialState.data.id,
          ],
        }).then(
          function (result) {
            if (result.error) self.do_warn(result.message)
            else self.update({}, {
              reload: true
            });
          },
        );
      } else if (this.initialState.model === 'product.packing.textile') {
        self._rpc({
          model: "product.packing.textile",
          method: "barcode_scan",
          args: [
            barcode,
            self.initialState.data.id,
          ],
        }).then(
          function (result) {
            if (result.error) self.do_warn(result.message)
            else self.update({}, {
              reload: true
            });
          },
        );
      } else if (this.initialState.model === 'opname.barcode') {
        self._rpc({
          model: "opname.barcode",
          method: "barcode_scan",
          args: [
            barcode,
            self.initialState.data.id,
          ],
        }).then(
          function (result) {
            if (result.error) self.do_warn(result.message)
            else self.update({}, {
              reload: true
            });
          },
        );
      }
    },
  });
});