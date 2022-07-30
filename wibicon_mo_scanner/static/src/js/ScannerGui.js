odoo.define('wibicon_mo_scanner.ScannerGui', function (require) {
    'use strict';

    const config = {};

    /**
     * Call this when the user interface is ready. Provide the component
     * that will be used to control the ui.
     * @param {owl.component} component component having the ui methods.
     */
    const configureGui = ({ component }) => {
        config.component = component;
        config.availableMethods = new Set([
            'showPopup',
            'showTempScreen',
            // 'playSound',
            'setSyncStatus',
        ]);
    };

    /**
     * Import this and consume like so: `Gui.showPopup(<PopupName>, <props>)`.
     * Like you would call `showPopup` in a component.
     */
    const ScannerGui = new Proxy(config, {
        get(target, key) {
            const { component, availableMethods } = target;
            if (!component) throw new Error(`Call 'configureGui' before using Gui.`);
            const isMounted = component.__owl__.isMounted;
            if (availableMethods.has(key) && isMounted) {
                return component[key].bind(component);
            }
        },
    });

    return { configureGui, ScannerGui };
});
