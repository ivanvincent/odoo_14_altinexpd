odoo.define("wibicon_mo_scanner.OrderScannerScreen", function (require) {
  "use strict";

  const { Component, UseState } = owl;
  const { useRef, useDispatch, useStore } = owl.hooks;

  const { loadCSS } = require("web.ajax");
  const framework = require("web.framework");

  class OrderScannerScreen extends Component {
    constructor() {
      super(...arguments);
      console.log(this);
      console.log(this.props.scanned.isScanned);
    }

    async willStart() {
      // loadCSS("/wibicon_mo_scanner/static/src/css/wscanner.css");
      console.log("willstartscanner");
    }

    _createFormData(data) {
      let formData = new FormData();
      formData.append("mrp_barcode", data);
      return formData;
    }

    // shouldUpdate() {
    //   console.log("on shouldUpdate scanner");
    //   // to prevent the parent rendering from rendering the children automatically
    //   // needed to actually notice the effect (or lack of) from useState
    //   return false;
    // }

    destroy() {
      super.destroy(...arguments);
      // self.props.scanned.isScanned = true;
      console.log("on destroy order scanner screen");
    }

    // patched() {
    //   console.log("patched");
    //   console.log(this.props);
    // }

    mounted() {
      console.log("on mounted scanner screen");

      $(".w_scanner").focus();
      let self = this;

      // const $ = (s) => document.querySelector(s);
      // const $$ = (s) => document.querySelectorAll(s);
      // const $$$ = (a) => Array.from(a);

      async function searchBarcode(sugg) {
        return await fetch(`/api/mrp/wo/`, {
          method: "POST", // *GET, POST, PUT, DELETE, etc.
          mode: "cors", // no-cors, *cors, same-origin
          cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
          credentials: "same-origin", // include, *same-origin, omit
          redirect: "follow", // manual, *follow, error
          referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
          body: self._createFormData(sugg), // body data type must match "Content-Type" header
        });
      }

      // async function searchEmployee(sugg) {
      //   return await fetch(`/api/employee/`, {
      //     method: "POST", // *GET, POST, PUT, DELETE, etc.
      //     mode: "cors", // no-cors, *cors, same-origin
      //     cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
      //     credentials: "same-origin", // include, *same-origin, omit
      //     redirect: "follow", // manual, *follow, error
      //     referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
      //     body: self._createFormData(sugg), // body data type must match "Content-Type" header
      //   });
      // }

      const inputBarcode = document.getElementById("formOrderScanner");

      if (inputBarcode) {
        inputBarcode.addEventListener("keypress", (ev) => {
          // console.log(
          //   "on enter ",
          //   document.getElementById("inputBarcode").value
          // );

          if (ev.keyCode === 13) {
            framework.blockUI();

            try {
              let barcode = document.getElementById("inputOrderBarcode").value;
              searchBarcode(barcode)
                .then((res) => {
                  return res.json();
                })
                .then((result) => {
                  if (result.status < 200 || result.status >= 300) {
                    framework.unblockUI();

                  } else {
                    framework.unblockUI();

                    if (result.data.id) {
                      let count_done = result.data.workorder_ids.filter((x) => {
                        return x.state === "done";
                      });

                      if (
                        count_done.length === result.data.workorder_ids.length
                      ) {
                        self.props.scanned.isFinished = true;
                        alertify.error("Work Orders has been finished");
                        $("#inputOrderBarcode").val("");
                      } else {
                        switch (result.data.state) {
                          case "draft":
                            alertify.error("Order Not Confirmed !!!");
                            setTimeout(() => {
                              window.location.reload();
                            }, 2000);
                            break;
                          case "cancel":
                            alertify.error("Order Cancelled !!!");
                            setTimeout(() => {
                              window.location.reload();
                            }, 2000);
                            break;
                          case "to_cancel":
                            alertify.error("Order to Cancelled !!!");
                            setTimeout(() => {
                              window.location.reload();
                            }, 2000);
                            break;
                          case "done":
                            alertify.error("Order has been done !!!");
                            setTimeout(() => {
                              window.location.reload();
                            }, 2000);
                            break;
                          case "confirmed":
                            self.props.scanned.isMo = true;
                            self.props.scanned.mrp = result.data;
                            self.props.scanned.workcenter_ids =
                              result.data.workcenter_ids;
                            self.props.scanned.machine_ids =
                              result.data.machine_ids;
                            self.props.scanned.finalset_ids =
                              result.data.finalset_ids;
                            self.props.scanned.progress_of_done =
                              count_done.length;
                          case "to_close":
                            self.props.scanned.isMo = true;
                            self.props.scanned.mrp = result.data;
                            self.props.scanned.workcenter_ids =
                              result.data.workcenter_ids;
                            self.props.scanned.machine_ids =
                              result.data.machine_ids;
                            self.props.scanned.finalset_ids =
                              result.data.finalset_ids;
                            self.props.scanned.progress_of_done =
                              count_done.length;
                          case "progress":
                            self.props.scanned.isMo = true;
                            self.props.scanned.mrp = result.data;
                            self.props.scanned.workcenter_ids =
                              result.data.workcenter_ids;
                            self.props.scanned.machine_ids =
                              result.data.machine_ids;
                            self.props.scanned.finalset_ids =
                              result.data.finalset_ids;
                            self.props.scanned.progress_of_done =
                              count_done.length;
                          default:
                            break;
                        }
                      }

                      // self.props.scanned.line_ids = result.line;
                      // self.props.scanned.head = result.head;
                      // document.body.style.background = "#FFF";

                      console.log(result);
                    } else {
                      $("#inputOrderBarcode").val("");
                      alertify.error("Order Not found");

                      //   self.env.services.notification.notify({
                      //     title: 'Error',
                      //     message: self.env._t("Barcode not Found"),
                      //     type: 'danger',
                      // });
                      // var myAlert = document.getElementById("barcodeAlert");
                      // var bsAlert = new bootstrap.Alert(myAlert);
                    }
                  }
                });
            } catch (error) {
              console.log(error);
            }
          }
        });
      }
    }
  }

  OrderScannerScreen.template = "OrderScannerScreen";

  return OrderScannerScreen;
});
