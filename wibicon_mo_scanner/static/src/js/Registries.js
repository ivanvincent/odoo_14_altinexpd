odoo.define('wibicon_mo_scanner.Registries', function(require) {
    'use strict';

    /**
     * This definition contains all the instances of ClassRegistry.
     */

    const ComponentRegistry = require('wibicon_mo_scanner.ComponentRegistry');

    return { Component: new ComponentRegistry() };
});
