odoo.define("wibicon_mo_scanner.HeaderScreen", function (require) {
    "use strict";

    // import mqtt from 'mqtt'
    const {
        Component,
        useState
    } = owl;
    const Registries = require("wibicon_mo_scanner.Registries");
    const {
        useListener
    } = require("web.custom_hooks");
    const {
        CrashManager
    } = require("web.CrashManager");

    const {
        useRef,
        useDispatch,
        useStore
    } = owl.hooks;


    class HeaderScreen extends Component {

        constructor() {
            super(...arguments);

        }


        mounted() {
            let self = this;

            $(".btn-sign-out").on("click", (e) => {
                self.props.state.isEmployee = false;
            });

        }

        destroy() {
            super.destroy(...arguments);
        }
        catchError(error) {
            console.error(error);
        }
    }

    HeaderScreen.template = "HeaderScannerScreen";

    Registries.Component.add(HeaderScreen);

    return HeaderScreen;
});