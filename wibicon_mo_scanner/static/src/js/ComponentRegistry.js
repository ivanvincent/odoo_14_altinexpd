odoo.define('wibicon_mo_scanner.ComponentRegistry', function(require) {
    'use strict';

    const ScannerComponent = require('wibicon_mo_scanner.ScannerComponent');
    const ClassRegistry = require('wibicon_mo_scanner.ClassRegistry');

    class ComponentRegistry extends ClassRegistry {
        freeze() {
            super.freeze();
            // Make sure ScannerComponent has the compiled classes.
            // This way, we don't need to explicitly declare that
            // a set of components is children of another.
            ScannerComponent.components = {};
            for (let [base, compiledClass] of this.cache.entries()) {
                ScannerComponent.components[base.name] = compiledClass;
            }
        }
        _recompute(base, old) {
            const res = super._recompute(base, old);
            if (typeof base === 'string') {
                base = this.baseNameMap[base];
            }
            ScannerComponent.components[base.name] = res;
            return res;
        }
    }

    return ComponentRegistry;
});
