odoo.define('wibicon_mo_scanner.scannerDB', function (require) {
    "use strict";

    var core = require('web.core');
    var utils = require('web.utils');
    var ScannersDB = core.Class.extend({
        name: 'openerp_scanner_db', //the prefix of the localstorage data
        limit: 100, // the maximum number of results returned by a search
        init: function (options) {
            options = options || {};
            this.name = options.name || this.name;
            this.limit = options.limit || this.limit;

            if (options.uuid) {
                this.name = this.name + '_' + options.uuid;
            }




            //cache the data in memory to avoid roundtrips to the localstorage
            this.cache = {};

            this.production_id = null;
            this.employee_id = null;
            this.work_in_progress_id = null;
            this.session_id = null;
            this.partner_id = null;
            this.product_id = null;
            this.production_quantity = null;
            this.employee_shift = null;
        },

        /** 
         * sets an uuid to prevent conflict in locally stored data between multiple PoS Configs. By
         * using the uuid of the config the local storage from other configs will not get effected nor
         * loaded in sessions that don't belong to them.
         *
         * @param {string} uuid Unique identifier of the PoS Config linked to the current session.
         */
        set_uuid: function (uuid) {
            this.name = this.name + '_' + uuid;
        },

        /* returns the category object from its id. If you pass a list of id as parameters, you get
         * a list of category objects. 
         */
        /* loads a record store from the database. returns default if nothing is found */
        load: function (store, deft) {
            if (this.cache[store] !== undefined) {
                return this.cache[store];
            }
            var data = localStorage[this.name + '_' + store];
            if (data !== undefined && data !== "") {
                data = JSON.parse(data);
                this.cache[store] = data;
                return data;
            } else {
                return deft;
            }
        },
        /* saves a record store to the database */
        save: function (store, data) {
            localStorage[this.name + '_' + store] = JSON.stringify(data);
            this.cache[store] = data;
        },
        _product_search_string: function (product) {
            var str = product.display_name;
            if (product.barcode) {
                str += '|' + product.barcode;
            }
            if (product.default_code) {
                str += '|' + product.default_code;
            }
            if (product.description) {
                str += '|' + product.description;
            }
            if (product.description_sale) {
                str += '|' + product.description_sale;
            }
            str = product.id + ':' + str.replace(/:/g, '') + '\n';
            return str;
        },
        add_products: function (products) {
            var stored_categories = this.product_by_category_id;

            if (!products instanceof Array) {
                products = [products];
            }
            for (var i = 0, len = products.length; i < len; i++) {
                var product = products[i];
                if (product.id in this.product_by_id) continue;
                if (product.available_in_pos) {
                    var search_string = utils.unaccent(this._product_search_string(product));
                    var categ_id = product.pos_categ_id ? product.pos_categ_id[0] : this.root_category_id;
                    product.product_tmpl_id = product.product_tmpl_id[0];
                    if (!stored_categories[categ_id]) {
                        stored_categories[categ_id] = [];
                    }
                    stored_categories[categ_id].push(product.id);

                    if (this.category_search_string[categ_id] === undefined) {
                        this.category_search_string[categ_id] = '';
                    }
                    this.category_search_string[categ_id] += search_string;

                    var ancestors = this.get_category_ancestors_ids(categ_id) || [];

                    for (var j = 0, jlen = ancestors.length; j < jlen; j++) {
                        var ancestor = ancestors[j];
                        if (!stored_categories[ancestor]) {
                            stored_categories[ancestor] = [];
                        }
                        stored_categories[ancestor].push(product.id);

                        if (this.category_search_string[ancestor] === undefined) {
                            this.category_search_string[ancestor] = '';
                        }
                        this.category_search_string[ancestor] += search_string;
                    }
                }
                this.product_by_id[product.id] = product;
                if (product.barcode) {
                    this.product_by_barcode[product.barcode] = product;
                }
            }
        },
        /* removes all the data from the database. TODO : being able to selectively remove data */
        clear: function () {
            for (var i = 0, len = arguments.length; i < len; i++) {
                localStorage.removeItem(this.name + '_' + arguments[i]);
            }
        },
        /* this internal methods returns the count of properties in an object. */
        _count_props: function (obj) {
            var count = 0;
            for (var prop in obj) {
                if (obj.hasOwnProperty(prop)) {
                    count++;
                }
            }
            return count;
        },

    });

    return ScannersDB;

});