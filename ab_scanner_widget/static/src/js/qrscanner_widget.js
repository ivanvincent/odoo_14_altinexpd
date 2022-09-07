odoo.define("ab_scanner_widget.barcode_scanner_widget", function (require) {
    "use strict";
    var FieldRegistry = require("web.field_registry");
    var AbstractField = require("web.AbstractField");

    var QrScanner = AbstractField.extend({
        template: "qrscanner_template",
        jsLibs: [
            '/ab_scanner_widget/static/src/lib/zxing.js',
        ],
        events: {
            'click #resetButton': '_onReloadCamera',
            'change #sourceSelect': '_onChangeCamera',
        },
        init: function () {
            this._super.apply(this, arguments);
            this.codeReader = null;
            this.scanning = true;
            this.selectedDeviceId = [];
        },
        start: function () {
            let self = this
            this._super.apply(this, arguments);
            this.codeReader = new ZXing.BrowserMultiFormatReader();
            this.codeReader.listVideoInputDevices()
                .then((videoInputDevices) => {
                    const sourceSelect = self.$('#sourceSelect')[0]
                    self.selectedDeviceId = videoInputDevices[0].deviceId
                    if (videoInputDevices.length >= 1) {
                        videoInputDevices.reverse().forEach((element) => {
                            const sourceOption = document.createElement('option')
                            sourceOption.text = element.label
                            sourceOption.value = element.deviceId
                            sourceSelect.appendChild(sourceOption)
                            
                            if (!self.selectedDeviceId) {
                                self.selectedDeviceId = element.deviceId
                            }
                        })

                        const sourceSelectPanel = self.$('#sourceSelectPanel')[0]
                        sourceSelectPanel.style.display = 'block'
                    }

                    self._onChangeCamera();
                })
                .catch((err) => {
                    // document.getElementById('result').textContent = err
                })
        },
        _onReloadCamera: function (event) {
            navigator.permissions.query({name: 'microphone'})
            .then((permissionObj) => {
             console.log(permissionObj.state);
            })
            .catch((error) => {
             console.log('Got error :', error);
            })
           
            navigator.permissions.query({name: 'camera'})
            .then((permissionObj) => {
             console.log(permissionObj.state);
            })
            .catch((error) => {
             console.log('Got error :', error);
            })
           this._onChangeCamera()
        },
        _onStartCamera: function (event) {
            var self = this;
            this.codeReader.decodeFromVideoDevice(this.selectedDeviceId, 'qr_scanner', (result, err) => {
                if (self.scanning){
                    if (result) {
                        var changes = {}
                        changes[self.attrs.name] = result.text;
                        self.trigger_up("field_changed", {
                            dataPointID: self.dataPointID,
                            changes: changes,
                            viewType: self.viewType,
                        });
                        new Audio('/ab_scanner_widget/static/src/lib/beep.mp3').play()
                        self.scanning = false
                        setTimeout(()=>self.scanning = true, 1200);
                    }
                }
            }).catch((err) => {
                document.getElementById('result').textContent = err
            })
        },
        _onResetCamera: function (event) {
            this.codeReader.reset();
        },
        _onChangeCamera: function (event) {
            this.codeReader.reset();
            const sourceSelect = self.$('#sourceSelect')[0];
            if (sourceSelect){
                this.selectedDeviceId = sourceSelect.value;
            }
            this._onStartCamera();
        },
        destroy: function () {
            this._super.apply(this, arguments);
            this.codeReader.reset();
        },
    });

    FieldRegistry.add("qrscanner", QrScanner);
});