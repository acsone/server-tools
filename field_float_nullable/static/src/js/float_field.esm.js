/** @odoo-module **/

import {Component} from "@odoo/owl";
import {_lt} from "@web/core/l10n/translation";
import {formatFloat} from "@web/views/fields/formatters";
import {parseFloat} from "@web/views/fields/parsers";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useInputField} from "@web/views/fields/input_field_hook";
import {useNumpadDecimal} from "@web/views/fields/numpad_decimal_hook";

export class FloatNullableField extends Component {
    setup() {
        this.inputRef = useInputField({
            getValue: () => this.formattedValue,
            refName: "numpadDecimal",
            parse: (v) => this.parse(v),
        });
        useNumpadDecimal();
    }

    parse(value) {
        if (value === "" || value === null) {
            return null;
        }
        return parseFloat(value);
    }

    get formattedValue() {
        if (this.props.value === null || this.props.value === false) {
            return "";
        }
        return formatFloat(this.props.value, {digits: this.props.digits});
    }
}

FloatNullableField.template = "field_float_nullable.FloatNullable";
FloatNullableField.props = {
    ...standardFieldProps,
    inputType: {type: String, optional: true},
    step: {type: Number, optional: true},
    digits: {type: Array, optional: true},
    placeholder: {type: String, optional: true},
};
FloatNullableField.defaultProps = {
    inputType: "text",
};

FloatNullableField.displayName = _lt("Float (Nullable)");
FloatNullableField.supportedTypes = ["float_nullable", "float"];

FloatNullableField.extractProps = ({attrs, field}) => {
    // eslint-disable-next-line init-declarations
    let digits;
    if (attrs.digits) {
        digits = JSON.parse(attrs.digits);
    } else if (attrs.options.digits) {
        digits = attrs.options.digits;
    } else if (Array.isArray(field.digits)) {
        digits = field.digits;
    }
    return {
        inputType: attrs.options.type,
        step: attrs.options.step,
        digits,
        placeholder: attrs.placeholder,
    };
};

registry.category("fields").add("float_nullable", FloatNullableField);
