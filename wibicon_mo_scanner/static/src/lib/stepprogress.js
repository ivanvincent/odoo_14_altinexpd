var r = function (e) {
    e = e || {};
    for (var t = 1; t < arguments.length; t++) {
        var s = arguments[t];
        if (s)
            for (var o in s) s.hasOwnProperty(o) && ("object" == typeof s[o] ? s[o] instanceof Array == 1 ? e[o] = s[o].slice(0) : e[o] = r(e[o], s[o]) : e[o] = s[o])
    }
    return e
};

function i(e) {
    var t = document.createElement("div");
    return t.innerHTML = e.trim(), t.firstChild
}
class e extends HTMLElement {
    constructor() {
        super(), this._defaultOptions = null, this._options = null, this._container = null, this._stepNumber = -1, this._shadowRoot = this.attachShadow({
            mode: "open"
        }), this._shadowRoot.append(i(`
    	<style>
            .progress-steps {
                /* All Steps */
                --font-size: 15px;
                --bar-thickness: 2px;
                --step-border-radius: 50%;
                --animation-speed: 0.5s;

                /* Default, Inactive Steps */
                --step-color: white;
                --step-width: 35px;
                
                --previous-label-font-color: black;

                /* Current Steps */
                --fill-color: #7A5BD3;
                --current-font-color: white;
                --current-step-label-weight: bold;
                --current-step-shadow: none;
                --current-label-font-color: var(--fill-color);

                
                --unfilled-color: #d5dce2;
                --disabled-fill-color: var(--unfilled-color);
                --disabled-font-color: #8B9DAC;
                --disabled-label-font-color: var(--unfilled-color);
                
                /* Future Steps */
                --future-label-font-color: var( --unfilled-color);


                /* Labels */
                --step-title-display: inline-block;
                --step-title-top-padding: 5px;
                --step-title-font: sans-serif;
                --step-title-weight: normal;

                display: flex;
                margin: 0 auto;
                position: relative;
                transition: width var(--animation-speed);
                justify-content: space-between;

                /* Dynamically set our width via the 2 'known' attributes updated on resizes and render */
                width: calc(100% - (var(--known-available-width) / (var(--known-step-count) - 1)) * 1px);  
            }

            /* The underlying grey line*/
            .progress-steps::before {
                content: '';
                z-index: 1;
                display: block;
                position: absolute;
                width: calc(100% - var(--step-width));
                left: calc(var(--step-width)/2);
                height: 0px;
                top: calc( (var(--step-width)/2) - (var(--bar-thickness)/2) );
                border: none;
                border-bottom: var(--bar-thickness) solid var(--unfilled-color);
            }

            /* The overlapping colored value line*/
            .progress-steps .completion-bar {
                content: '';
                z-index: 2;
                display: block;
                position: absolute;
                width: 0%;
                transition: width var(--animation-speed);
                height: 0px;
                top: calc( (var(--step-width)/2) - (var(--bar-thickness)/2) );
                left: calc(var(--step-width)/2);
                border: none;
                border-bottom: var(--bar-thickness) solid var(--fill-color);
            }

            /* The colored balls */
            .progress-steps .progress-step::before {
                content: attr(data-step-number);
                z-index: 3;
                width: calc(var(--step-width) - var(--bar-thickness)*2);
                height: calc(var(--step-width) - var(--bar-thickness)*2);
                background-color: var(--step-color);
                border: var(--bar-thickness) solid var(--unfilled-color);
                color: var(--unfilled-color);
                border-radius: var(--step-border-radius);
                position: relative;
                transition: background-color var(--animation-speed);
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: var(--step-title-font);
            }

            .progress-steps .progress-step.previous::before, .progress-steps .progress-step.current::before{
                color: var(--current-font-color);
                background-color: var(--fill-color);
                border: none;
                width: var(--step-width);
                height: var(--step-width);
            }
            

            .progress-steps .progress-step.current .progress-title {
                color: var(--current-label-font-color) !important;
                font-weight: var(--current-label-font-weight);
                font-weight: var(--current-step-label-weight) !important;
            }
            .progress-steps .progress-step.current::before {
                background-color: var(--fill-color);
                box-shadow: var(--current-step-shadow);
            }


            .progress-steps .progress-step.disabled::before {
                background-color: var(--disabled-fill-color);
                border-color: var(--unfilled-color);
                color: var(--disabled-font-color);
            }

            .progress-steps .progress-step.disabled {
                cursor: not-allowed;
            }

            .progress-steps .progress-step:not(.disabled) {
                cursor: pointer;
            }

            .progress-steps .progress-step {
                justify-content: space-evenly;
                font-size: var(--font-size);
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .progress-steps .progress-step.future .progress-title{
                color: var(--future-label-font-color);
            }
            
            .progress-steps .progress-step.disabled .progress-title{
                color: var(--disabled-label-font-color);
            }

            .progress-steps .progress-step .progress-title {
                z-index: 3;
                display: var(--step-title-display);
                position: absolute;
                text-align: center;
                top: calc( var(--step-width) + var(--step-title-top-padding));
                font-family: var(--step-title-font);
                color: var(--unfilled-color);
                font-size: var(--font-size);
                transition: color var(--animation-speed), width var(--animation-speed);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                user-select: none;
                font-weight: var(--step-title-weight);

                /* Dynamically set our own title width via the 2 'known' attributes updated on resizes and render */
                --title-clearance: 8px;
                width: calc(
                            var(--known-available-width) / (var(--known-step-count) - 1) /* width per segment */
                            * 1px /* Cast to pixels */
                            - (var(--title-clearance) * 2) /* Account for clearance */
                            );  
            }
            
            .progress-steps .progress-step.previous .progress-title {
                color: var(--previous-label-font-color);
            }        

	    </style>
        `)), this._container = i('<div class="progress-steps"></div>'), this._shadowRoot.appendChild(this._container), this._container.classList.add("progress-steps"), this._defaultOptions = {
            steps: [],
            allowStepZero: !0,
            events: {
                onStepChanged: function (e, t) {}
            },
            style: {}
        };
        let e = this;
        var t;
        this._updateKnownControlSize = function () {
            clearTimeout(t), t = setTimeout(function () {
                null !== e._options && null !== e._options.steps && (e._container.style.setProperty("--known-step-count", e._options.steps.length), e._container.style.setProperty("--known-available-width", e.getBoundingClientRect().width))
            }, 100)
        }, this._updateKnownControlSize(), window.addEventListener("resize", this._updateKnownControlSize, !1), window.addEventListener("orientationchange", this._updateKnownControlSize, !1)
    }
    init(e) {
        if (this._options = r({}, this._defaultOptions, e), this._options.steps.forEach((e, t) => {
                e.number = t + 1
            }), this._options.steps.length ? this._stepNumber = 1 : (this._stepNumber = -1, console.warn("You must provide at least 1 step")), void 0 !== this._options.style) {
            let s = "";
            for (var o in this._options.style) {
                let e = "",
                    t = this._options.style[o];
                if ("stepWidth" === o) e = "--step-width", isNaN(t) || (t += "px");
                else if ("fontSize" === o) e = "--font-size", isNaN(t) || (t += "px");
                else if ("borderRadius" === o) e = "--step-border-radius", isNaN(t) || (t += "px");
                else if ("lineThickness" === o) e = "--bar-thickness", isNaN(t) || (t += "px");
                else if ("animationSpeed" === o) e = "--animation-speed", isNaN(t) || (t += "ms");
                else if ("showLabels" === o) {
                    if (e = "--step-title-display", t) continue;
                    t = "none"
                } else "labelSpacing" === o ? (e = "--step-title-top-padding", isNaN(t) || (t += "px")) : "progressFillColor" === o ? e = "--fill-color" : "currentStepFontColor" === o ? e = "--current-font-color" : "currentStepLabelFontWeight" === o ? e = "--current-step-label-weight" : "stepLabelFontWeight" === o ? e = "--step-title-weight" : "futureStepFillColor" === o ? e = "--step-color" : "disabledStepFontColor" === o ? e = "--disabled-font-color" : "previousLabelFontColor" === o ? e = "--previous-label-font-color" : "currentLabelFontColor" === o ? e = "--current-label-font-color" : "futureLabelFontColor" === o ? e = "--future-label-font-color" : "disabledLabelFontColor" === o ? e = "--disabled-label-font-color" : "progressUnfilledColor" === o ? e = "--unfilled-color" : "disabledStepFillColor" === o && (e = "--disabled-fill-color");
                s += `
                ${e}: ${t} !important;
            `
            }
            this._shadowRoot.appendChild(i(`
            <style>
              .progress-steps{
             		 ${s}
              }
            </style>
        `))
        }
        this._render()
    }
    _render() {
        for (; this._container.firstChild;) this._container.removeChild(this._container.firstChild);
        this._container.appendChild(i('<div class="completion-bar"></div>'));
        var e = this._options.steps.filter(e => void 0 !== e.numberDisplay).length;
        let s = 1 < e,
            o = 1;
        if (e !== this._options.steps.length && 0 !== e) throw "Either all or none of your steps can have numberDisplay specified";
        this._options.steps.forEach(e => {
            let t = i(`
              <div class="progress-step" data-step-number="${s?e.numberDisplay:o++}">
          	    <div class="progress-title">${e.name}</div>
              </div>
            `);
            "" != e.name && t.setAttribute("title", e.name), e.disabled && t.classList.add("disabled"), this._container.appendChild(t)
        });
        let t = this;
        this._container.querySelectorAll(".progress-step:not(.disabled)").forEach(e => {
            e.addEventListener("click", function (e) {
                e = e.target.closest(".progress-step");
                null != e && (e = Array.from(t._container.querySelectorAll(".progress-step")).indexOf(e) + 1, t._setStepInternal(e))
            })
        }), void 0 !== this && this._setStepInternal(), setTimeout(this._updateKnownControlSize, 100)
    }
    getStep() {
        return this._getStepInternal()
    }
    setStep(e) {
        0 !== e || this._options.allowStepZero || console.warn("Cannot set to step 0"), -1 < e && e <= this._options.steps.length ? 0 < e && this._options.steps[e - 1].disabled ? console.warn("Cant set to disabled step") : (this._stepNumber = e, this._setStepInternal()) : console.warn("Step out of range")
    }
    stepUp() {
        this._stepUpInternal()
    }
    stepDown() {
        this._stepDownInternal()
    }
    disableStep(e) {
        if (this._options.steps[e - 1].disabled = !0, this._stepNumber === e) {
            let e = !1;
            for (; !e && !0 === this._options.steps[this._stepNumber - 1].disabled;) this._stepNumber--, 0 === this._stepNumber && (e = !0)
        }
        this._render()
    }
    enableStep(e) {
        this._options.steps[e - 1].disabled = !1, this._render()
    }
    _getStepInternal() {
        return 0 < this._stepNumber ? this._options.steps[this._stepNumber - 1] : null
    }
    _stepUpInternal() {
        this._stepNumber < this._options.steps.length && !this._options.steps[this._stepNumber].disabled && (this._stepNumber++, this._setStepInternal())
    }
    _stepDownInternal() {
        0 < this._stepNumber && (this._stepNumber--, 0 !== this._stepNumber || this._options.allowStepZero || (this._stepNumber = 1), this._setStepInternal())
    }
    _setStepInternal(s) {
        void 0 === s ? s = this._stepNumber : this._stepNumber = s;
        var e = (s - 1) / (this._options.steps.length - 1) * 100;
        this._container.querySelector(".completion-bar").style.width = `calc(${e}% - (var(--step-width)/2))`, this._container.querySelectorAll(".progress-step").forEach(e => {
            e.classList.remove("previous"), e.classList.remove("current"), e.classList.remove("future")
        }), this._container.querySelectorAll(".progress-step").forEach(function (e, t) {
            t + 1 < s && e.classList.add("previous"), t + 1 === s && e.classList.add("current"), s < t + 1 && e.classList.add("future")
        }), this._options.events.onStepChanged && "function" == typeof this._options.events.onStepChanged && (e = this._getStepInternal(), this._options.events.onStepChanged(s, e))
    }
}
customElements.define("progress-steps", e);