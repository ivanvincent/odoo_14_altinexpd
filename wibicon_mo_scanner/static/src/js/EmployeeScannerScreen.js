odoo.define("wibicon_mo_scanner.EmployeeScannerScreen", function (require) {
  "use strict";

  const { Component, UseState } = owl;
  const { useRef, useDispatch, useStore } = owl.hooks;

  const { loadCSS } = require("web.ajax");
  const framework = require("web.framework");

  class EmployeeScannerScreen extends Component {
    constructor() {
      super(...arguments);
    }

    async willStart() {
      loadCSS("/wibicon_mo_scanner/static/src/css/wscanner.css");
    }

    _createFormData(data) {
      let formData = new FormData();
      formData.append("employee_barcode", data);
      return formData;
    }

    mounted() {
      document.body.style.background = "#222";

      $(".w_scanner").focus();
      let self = this;

      // const $ = (s) => document.querySelector(s);
      // const $$ = (s) => document.querySelectorAll(s);
      // const $$$ = (a) => Array.from(a);

      async function searchBarcode(sugg) {
        return await fetch(`/get_production/`, {
          method: "POST", // *GET, POST, PUT, DELETE, etc.
          mode: "cors", // no-cors, *cors, same-origin
          cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
          credentials: "same-origin", // include, *same-origin, omit
          redirect: "follow", // manual, *follow, error
          referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
          body: self._createFormData(sugg), // body data type must match "Content-Type" header
        });
      }

      async function searchEmployee(sugg) {
        return await fetch(`/api/employee/`, {
          method: "POST", // *GET, POST, PUT, DELETE, etc.
          mode: "cors", // no-cors, *cors, same-origin
          cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
          credentials: "same-origin", // include, *same-origin, omit
          redirect: "follow", // manual, *follow, error
          referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
          body: self._createFormData(sugg), // body data type must match "Content-Type" header
        });
      }

      const inputBarcode = document.getElementById("formScanner");

      if (inputBarcode) {
        inputBarcode.addEventListener("keypress", (ev) => {
          if (ev.keyCode === 13) {
            framework.blockUI();

            try {
              // ev.preventDefault();
              let barcode = document.getElementById("inputBarcode").value;
              searchEmployee(barcode)
                .then((res) => {
                  return res.json();
                })
                .then((result) => {
                  // console.log(result);
                  // toggleLoading(false);
                  if (result.status < 200 || result.status >= 300) {

                    // updateSuggestionList(
                    //   {
                    //     message: "Barcode Not Found",
                    //     type: suggestionsType.ERROR,
                    //   },
                    //   true
                    // );
                  } else {
                    // use

                    framework.unblockUI();

                    // self.props.scanned.set('isScanned',true);

                    if (result.data.id) {
                      self.props.scanned.isEmployee = true;
                      self.props.scanned.employee.id = result.data.id;
                      self.props.scanned.employee.name = result.data.name;
                      // self.props.scanned.barcode = barcode;
                      self.props.scanned.line_ids = result.line;
                      // self.props.scanned.head = result.head;
                      // document.body.style.background = "#FFF";
                    } else {
                      $("#inputBarcode").val("");
                      // console.log(alertify);
                      alertify.error("Employee Not found");

                      //   self.env.services.notification.notify({
                      //     title: 'Error',
                      //     message: self.env._t("Barcode not Found"),
                      //     type: 'danger',
                      // });
                      // var myAlert = document.getElementById("barcodeAlert");
                      // var bsAlert = new bootstrap.Alert(myAlert);
                    }
                    // updateSuggestionList(result.data);
                  }

                  // return result;
                });
              // if (ev.key.ENTER) {
              // }
            } catch (error) {
              console.log(error);
            }
          }
        });
      }
    }
  }

  EmployeeScannerScreen.template = "EmployeeScannerScreen";

  return EmployeeScannerScreen;
});
