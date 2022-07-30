odoo.define('wibicon_mo_scanner.ScannerComponent', function (require) {
    'use strict';

    const {
        Component
    } = owl;

    class ScannerComponent extends Component {
        showTempScreen(name, props) {
            return new Promise((resolve) => {
                this.trigger('show-temp-screen', {
                    name,
                    props,
                    resolve
                });
            });
        }
        showScreen(name, props) {
            this.trigger('show-main-screen', {
                name,
                props
            });
        }
        /**
         * @param {String} name 'bell' | 'error'
         */
        // playSound(name) {
        //     this.trigger('play-sound', name);
        // }
        /**
         * Control the SyncNotification component.
         * @param {String} status 'connected' | 'connecting' | 'disconnected' | 'error'
         * @param {String} pending number of pending orders to sync
         */
        setSyncStatus(status, pending) {
            this.trigger('set-sync-status', {
                status,
                pending
            });
        }
    }

    return ScannerComponent;
});