odoo.define('wibicon_utility.date_range_owl', function (require) {
  "use strict";

  const ActionMenus = require('web.ActionMenus');
  const ComparisonMenu = require('web.ComparisonMenu');
  const ActionModel = require('web/static/src/js/views/action_model.js');
  const FavoriteMenu = require('web.FavoriteMenu');
  const FilterMenu = require('web.FilterMenu');
  const GroupByMenu = require('web.GroupByMenu');
  const patchMixin = require('web.patchMixin');
  const Pager = require('web.Pager');
  const SearchBar = require('web.SearchBar');
  const { useModel } = require('web/static/src/js/model.js');

  const { Component, hooks } = owl;
  const { useRef, useSubEnv } = hooks;

  /**
   * TODO: remove this whole mechanism as soon as `cp_content` is completely removed.
   * Extract the 'cp_content' key of the given props and return them as well as
   * the extracted content.
   * @param {Object} props
   * @returns {Object}
   */
  function getAdditionalContent(props) {
      const additionalContent = {};
      if ('cp_content' in props) {
          const content = props.cp_content || {};
          if ('$buttons' in content) {
              additionalContent.buttons = content.$buttons;
          }
          if ('$searchview' in content) {
              additionalContent.searchView = content.$searchview;
          }
          if ('$pager' in content) {
              additionalContent.pager = content.$pager;
          }
          if ('$searchview_buttons' in content) {
              additionalContent.searchViewButtons = content.$searchview_buttons;
          }
      }
      return additionalContent;
  }


  class DateRangeOwl extends Component {
      constructor() {
          super(...arguments);

          this.additionalContent = getAdditionalContent(this.props);

          useSubEnv({
              action: this.props.action,
              searchModel: this.props.searchModel,
              view: this.props.view,
          });

          // Connect to the model
          // TODO: move this in enterprise whenever possible
          if (this.env.searchModel) {
              this.model = useModel('searchModel');
          }

          // Reference hooks
          this.contentRefs = {
              // buttons: useRef('buttons'),
              // pager: useRef('pager'),
              // searchView: useRef('searchView'),
              // searchViewButtons: useRef('searchViewButtons'),
          };

          this.fields = this._formatFields(this.props.fields);
      }

      mounted() {
          this._attachAdditionalContent();
      }

      patched() {
          this._attachAdditionalContent();
      }

      async willUpdateProps(nextProps) {
          // Note: action and searchModel are not likely to change during
          // the lifespan of a ControlPanel instance, so we only need to update
          // the view information.
          if ('view' in nextProps) {
              this.env.view = nextProps.view;
          }
          if ('fields' in nextProps) {
              this.fields = this._formatFields(nextProps.fields);
          }
          this.additionalContent = getAdditionalContent(nextProps);
      }

      //---------------------------------------------------------------------
      // Private
      //---------------------------------------------------------------------

      /**
       * Attach additional content extracted from the props 'cp_content' key, if any.
       * @private
       */
      _attachAdditionalContent() {
          for (const key in this.additionalContent) {
              if (this.additionalContent[key] && this.additionalContent[key].length) {
                  const target = this.contentRefs[key].el;
                  if (target) {
                      target.innerHTML = "";
                      target.append(...this.additionalContent[key]);
                  }
              }
          }
      }

      /**
       * Give `name` and `description` keys to the fields given to the control
       * panel.
       * @private
       * @param {Object} fields
       * @returns {Object}
       */
      _formatFields(fields) {
          const formattedFields = {};
          for (const fieldName in fields) {
              formattedFields[fieldName] = Object.assign({
                  description: fields[fieldName].string,
                  name: fieldName,
              }, fields[fieldName]);
          }
          return formattedFields;
      }
  }
  ControlPanel.modelExtension = "ControlPanel";

  ControlPanel.components = {
      SearchBar,
      ActionMenus, Pager,
      ComparisonMenu, FilterMenu, GroupByMenu, FavoriteMenu,
  };
  ControlPanel.defaultProps = {
      breadcrumbs: [],
      fields: {},
      searchMenuTypes: [],
      views: [],
      withBreadcrumbs: true,
      withSearchBar: true,
  };
  ControlPanel.props = {
      action: Object,
      breadcrumbs: Array,
      searchModel: ActionModel,
      cp_content: { type: Object, optional: 1 },
      fields: Object,
      pager: { validate: p => typeof p === 'object' || p === null, optional: 1 },
      searchMenuTypes: Array,
      actionMenus: { validate: s => typeof s === 'object' || s === null, optional: 1 },
      title: { type: String, optional: 1 },
      view: { type: Object, optional: 1 },
      views: Array,
      withBreadcrumbs: Boolean,
      withSearchBar: Boolean,
  };
  ControlPanel.template = 'DateRangeOwl.buttons';

  return patchMixin(ControlPanel);
});
