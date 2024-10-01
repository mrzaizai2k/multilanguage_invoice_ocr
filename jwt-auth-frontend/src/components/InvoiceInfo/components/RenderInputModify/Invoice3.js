import React from 'react';
import fieldLabels from "../../../../config/fieldLabels";
import { BsPlusSquare } from 'react-icons/bs';
import moment from 'moment';
import { Select } from "antd";

function ModifyFieldsInvoice3({ info, keyPath = [], onChange }) {
    const handleInputChange = (keyPath, value) => {
        let target = info;
        for (let i = 0; i < keyPath.length - 1; i++) {
            const key = keyPath[i];
            if (target[key] === undefined) {
                target[key] = isNaN(keyPath[i + 1]) ? {} : [];
            }
            target = target[key];
        }
        target[keyPath[keyPath.length - 1]] = value;
        onChange([...keyPath], value);
    };

    const addNewLineItem = (lineIndex) => {
        const currentLines = Array.isArray(info?.lines) ? info.lines : [];
        const line = currentLines[lineIndex];
        const newItem = {
            title: "",
            description: "",
            amount: null,
            amount_each: null,
            amount_ex_vat: null,
            vat_amount: null,
            vat_percentage: null,
            quantity: null,
            unit_of_measurement: "",
            sku: "",
            vat_code: ""
        };
        const updatedLine = {
            ...line,
            lineitems: [newItem, ...(line.lineitems || [])]
        };
        const updatedLines = [
            ...currentLines.slice(0, lineIndex),
            updatedLine,
            ...currentLines.slice(lineIndex + 1)
        ];
        handleInputChange([...keyPath, 'lines'], updatedLines);
    };

    const renderInputModify = (keyPath, value, fieldType, options) => {
        const key = keyPath.join('.');

        switch (fieldType) {
            case 'number':
                return (
                    <input
                        key={key}
                        type="number"
                        value={value === null ? '' : value}
                        onChange={(e) => {
                            const newValue = e.target.value === '' ? null : Number(e.target.value);
                            handleInputChange(keyPath, newValue);
                        }}
                    />
                );
            case 'string':
                return (
                    <input
                        key={key}
                        type="text"
                        value={value || ''}
                        onChange={(e) => handleInputChange(keyPath, e.target.value)}
                    />
                );
            case 'boolean':
                return (
                    <input
                        key={key}
                        type="checkbox"
                        checked={value || false}
                        onChange={(e) => handleInputChange(keyPath, e.target.checked)}
                    />
                );
            case 'select':
                return (
                    <Select
                        key={key}
                        value={value}
                        onChange={(value) => handleInputChange(keyPath, value)}
                        style={{ width: '60%', height: '38px' }}
                        showSearch
                        placeholder="Select an option"
                        filterOption={(input, option) =>
                            (option?.children ?? '').toLowerCase().includes(input.toLowerCase())
                        }
                    >
                        {options.map((option, idx) => (
                            <Select.Option key={idx} value={option}>
                                {option}
                            </Select.Option>
                        ))}
                    </Select>
                );
            case 'date':
                const formattedDate = value ? moment(value).format('YYYY-MM-DD') : '';
                return (
                    <input
                        key={key}
                        type="date"
                        value={formattedDate}
                        onChange={(e) => handleInputChange(keyPath, e.target.value)}
                    />
                );
            case 'time':
                const formattedTime = value ? moment(value, 'HH:mm:ss').format('HH:mm') : '';
                return (
                    <input
                        key={key}
                        type="time"
                        value={formattedTime}
                        onChange={(e) => handleInputChange(keyPath, e.target.value)}
                    />
                );
            case 'percentage':
                return (
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <input
                            key={key}
                            type="number"
                            value={value === null ? '' : value}
                            placeholder="Enter percentage ( % )"
                            onChange={(e) => {
                                const newValue = e.target.value === '' ? null : Number(e.target.value);
                                handleInputChange(keyPath, newValue);
                            }}
                            style={{ flexGrow: 1 }}
                        />
                    </div>
                );
            default:
                return null;
        }
    };

    const renderLineItem = (item, lineIndex, itemIndex, keyPath) => {
        const newKeyPath = [...keyPath, lineIndex, 'lineitems', itemIndex];
        const fields = [
            { label: 'Title', key: 'title', type: 'string' },
            { label: 'Description', key: 'description', type: 'string' },
            { label: 'Amount', key: 'amount', type: 'number' },
            { label: 'Amount Each', key: 'amount_each', type: 'number' },
            { label: 'Amount Ex VAT', key: 'amount_ex_vat', type: 'number' },
            { label: 'VAT Amount', key: 'vat_amount', type: 'number' },
            { label: 'VAT Percentage (%)', key: 'vat_percentage', type: 'percentage' },
            { label: 'Quantity', key: 'quantity', type: 'number' },
            { label: 'Unit of Measurement', key: 'unit_of_measurement', type: 'string' },
            { label: 'SKU', key: 'sku', type: 'string' },
            { label: 'VAT Code', key: 'vat_code', type: 'string' }
        ];

        return (
            <div className="invoice__overlay-group-item" key={`${newKeyPath.join('.')}`} style={{ marginLeft: '40px' }}>
                {fields.map(({ label, key, type }) => (
                    <div key={key} className='invoice__overlay-input' style={{ marginLeft: '20px' }}>
                        <label>{label}</label>
                        {renderInputModify([...newKeyPath, key], item[key], type)}
                    </div>
                ))}
            </div>
        );
    };

    const renderLine = (line, index, keyPath) => {
        const newKeyPath = [...keyPath, index];
        return (
            <div className="invoice__overlay-group-item" key={`${newKeyPath.join('.')}`}>
                <div className="invoice__overlay-input" style={{ marginLeft: '20px' }}>
                    <label>Description</label>
                    {renderInputModify([...newKeyPath, 'description'], line.description, 'string')}
                </div>
                <div className="invoice__overlay-label" style={{ marginLeft: '40px' }}>
                    <h5>Line Items</h5>
                    <button type="button" onClick={() => addNewLineItem(index)}>
                        <BsPlusSquare />
                        Add Line Item
                    </button>
                </div>
                {line.lineitems.map((item, itemIndex) => renderLineItem(item, index, itemIndex, keyPath))}
            </div>
        );
    };

    const renderFieldsModify = (info, keyPath = []) => {
        return Object.entries(info || {}).map(([key, field]) => {
            const newKeyPath = [...keyPath, key];
            const label = field.key_name_user || fieldLabels[key] || key;
            const fieldType = field.data_type || field.type || typeof field.value;
            const options = Array.isArray(field.data) ? field.data : [];
            const isRequired = field.required;

            if (key === 'lines' && Array.isArray(field)) {
                return (
                    <div className="invoice__overlay-group" key={newKeyPath.join('.')} style={{ marginLeft: '20px' }}>
                        <div className="invoice__overlay-label">
                            <h4>{label}</h4>
                        </div>
                        {field.map((item, index) => renderLine(item, index, newKeyPath))}
                    </div>
                );
            }

            if (key === 'vatitems' && Array.isArray(field.value)) {
                return (
                    <div className="invoice__overlay-group" key={newKeyPath.join('.')} style={{ marginLeft: '20px' }}>
                        <div className="invoice__overlay-label">
                            <h4>{label}</h4>
                        </div>
                        {field.value.map((vatItem, index) => (
                            <div key={index} className="invoice__overlay-group-item" style={{ marginLeft: '20px' }}>
                                {Object.entries(vatItem).map(([vatKey, vatValue]) => {
                                    const isPercentage = vatKey === 'percentage';
                                    const fieldType = isPercentage ? 'percentage' : (typeof vatValue === 'number' ? 'number' : 'string');
            
                                    return (
                                        <div key={vatKey} className='invoice__overlay-input' style={{ marginLeft: '20px' }}>
                                            <label>
                                                {fieldLabels[vatKey] || vatKey}
                                                {isPercentage && <span style={{ marginLeft: '5px' }}>( % )</span>}
                                            </label>
                                            {renderInputModify([...newKeyPath, index, vatKey], vatValue, fieldType)}
                                        </div>
                                    );
                                })}
                            </div>
                        ))}
                    </div>
                );
            }

            if (fieldType === 'object' && field !== null) {
                return renderFieldsModify(field, newKeyPath);
            }

            return (
                <div className="invoice__overlay-input" key={newKeyPath.join('.')} style={{ marginLeft: '20px' }}>
                    <label>
                        {label}
                        {isRequired && <span style={{ color: 'red', fontSize: "18px" }}> * </span>}
                    </label>
                    {renderInputModify(newKeyPath, field.value, fieldType, field.data, options)}
                </div>
            );
        });
    };

    return <>{renderFieldsModify(info, keyPath)}</>;
}

export default ModifyFieldsInvoice3;
