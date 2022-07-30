odoo.define('web.web_client', function (require) {
    'use strict';

    const AbstractService = require('web.AbstractService');
    const env = require('web.env');
    const WebClient = require('web.AbstractWebClient');
    const MoScannerApp = require('wibicon_mo_scanner.ScannerApp');
    const Registries = require('wibicon_mo_scanner.Registries');
    const {
        configureGui
    } = require('wibicon_mo_scanner.ScannerGui');

    owl.config.mode = env.isDebug() ? 'dev' : 'prod';
    owl.Component.env = env;

    Registries.Component.add(owl.misc.Portal);

    function setupResponsivePlugin(env) {
        const isMobile = () => window.innerWidth <= 768;
        env.isMobile = isMobile();
        const updateEnv = owl.utils.debounce(() => {
            env.isMobile = !env.isMobile;
            env.qweb.forceUpdate();

        }, 15);
        window.addEventListener("resize", updateEnv);
    }

    setupResponsivePlugin(owl.Component.env);

    async function startMoScannerApp(webClient) {
        Registries.Component.freeze();
        await env.session.is_bound;
        env.qweb.addTemplates(env.session.owlTemplates);
        env.bus = new owl.core.EventBus();
        await owl.utils.whenReady();
        await webClient.setElement(document.body);
        await webClient.start();
        webClient.isStarted = true;
        const app = new(Registries.Component.get(MoScannerApp))(null, {
            webClient
        });
        await app.mount(document.querySelector('.o_action_manager'));
        // await app.start();
        configureGui({
            component: app
        });
    }

    AbstractService.prototype.deployServices(env);
    const webClient = new WebClient();
    startMoScannerApp(webClient);
    return webClient;
});