import React from 'react';
import fieldLabels from "../../../../config/fieldLabels";
import { BsPlusSquare, BsTrash } from 'react-icons/bs';
import moment from 'moment';
import { Button, Popconfirm, Select } from "antd";

function ModifyFieldsInvoice3({ info, keyPath = [], onChange, validationErrors }) {
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

    const deleteLineItem = (lineIndex, itemIndex) => {
        const currentLines = Array.isArray(info?.lines) ? info.lines : [];
        const line = currentLines[lineIndex];
        const updatedLineItems = line.lineitems.filter((_, index) => index !== itemIndex);
        const updatedLine = {
            ...line,
            lineitems: updatedLineItems
        };
        const updatedLines = [
            ...currentLines.slice(0, lineIndex),
            updatedLine,
            ...currentLines.slice(lineIndex + 1)
        ];
        handleInputChange([...keyPath, 'lines'], updatedLines);
    };

    const renderInputModify = (keyPath, value, fieldType, options, isRequired = false) => {
        const key = keyPath.join('.');
        const error = validationErrors[key];

        switch (fieldType) {
            case 'number':
                return (
                    <div>
                        <input
                            key={key}
                            type="number"
                            value={value === null ? '' : value}
                            onChange={(e) => {
                                const newValue = e.target.value;
                                if (newValue === '' || /^\d+$/.test(newValue)) {
                                    handleInputChange(keyPath, newValue === '' ? null : Number(newValue));
                                }
                            }}
                            onKeyDown={(e) => {
                                if (['e', 'E', '+', '-'].includes(e.key)) {
                                    e.preventDefault();
                                }
                            }}
                            required={isRequired}
                        />
                        {error && <span className="error-message" style={{ color: 'red' }}>{error}</span>}
                    </div>
                );
            case 'string':
                return (
                    <div>
                        <input
                            key={key}
                            type="text"
                            value={value || ''}
                            onChange={(e) => handleInputChange(keyPath, e.target.value)}
                            required={isRequired}
                        />
                        {error && <span className="error-message" style={{ color: 'red' }}>{error}</span>}
                    </div>
                );
            case 'boolean':
                return (
                    <div>
                        <input
                            key={key}
                            type="checkbox"
                            checked={value || false}
                            onChange={(e) => handleInputChange(keyPath, e.target.checked)}
                            required={isRequired}
                        />
                        {error && <span className="error-message" style={{ color: 'red' }}>{error}</span>}
                    </div>
                );
            case 'select':
                return (
                    <div>
                        <Select
                            key={key}
                            value={value}
                            onChange={(value) => handleInputChange(keyPath, value)}
                            style={{ width: '100%', height: '38px' }}
                            showSearch
                            placeholder="Select an option"
                            filterOption={(input, option) =>
                                (option?.children ?? '').toLowerCase().includes(input.toLowerCase())
                            }
                            required={isRequired}
                        >
                            {options.map((option, idx) => (
                                <Select.Option key={idx} value={option}>
                                    {option}
                                </Select.Option>
                            ))}
                        </Select>
                        {error && <span className="error-message" style={{ color: 'red' }}>{error}</span>}
                    </div>
                );
            case 'date':
                const formattedDate = value ? moment(value).format('YYYY-MM-DD') : '';
                return (
                    <div>
                        <input
                            key={key}
                            type="date"
                            value={formattedDate}
                            onChange={(e) => handleInputChange(keyPath, e.target.value)}
                            required={isRequired}
                        />
                        {error && <span className="error-message" style={{ color: 'red' }}>{error}</span>}
                    </div>
                );
            case 'time':
                const formattedTime = value ? moment(value, 'HH:mm:ss').format('HH:mm') : '';
                return (
                    <div>
                        <input
                            key={key}
                            type="time"
                            value={formattedTime}
                            onChange={(e) => handleInputChange(keyPath, e.target.value)}
                            required={isRequired}
                        />
                        {error && <span className="error-message" style={{ color: 'red' }}>{error}</span>}
                    </div>
                );
            case 'percentage':
                return (
                    <div>
                        <input
                            key={key}
                            type="number"
                            value={value === null ? '' : value}
                            placeholder="Enter percentage ( % )"
                            onChange={(e) => {
                                const newValue = e.target.value === '' ? null : Number(e.target.value);
                                handleInputChange(keyPath, newValue);
                            }}
                            required={isRequired}
                        />
                        {error && <span className="error-message" style={{ color: 'red' }}>{error}</span>}
                    </div>
                );
            default:
                return null;
        }
    };

    const renderLineItem = (item, lineIndex, itemIndex, keyPath) => {
        const newKeyPath = [...keyPath, lineIndex, 'lineitems', itemIndex];
        const fields = [
            { label: 'Bezeichnung', key: 'title', type: 'string' },
            { label: 'Beschreibung', key: 'description', type: 'string' },
            { label: 'Betrag', key: 'amount', type: 'number' },
            { label: 'Amount / Item', key: 'amount_each', type: 'number' },
            { label: 'Betrag ohne MwSt', key: 'amount_ex_vat', type: 'number' },
            { label: 'Betrag MwSt', key: 'vat_amount', type: 'number' },
            { label: 'Prozent MwSt', key: 'vat_percentage', type: 'percentage' },
            { label: 'Quantity', key: 'quantity', type: 'number' },
            { label: 'Messeinheit', key: 'unit_of_measurement', type: 'string' },
            { label: 'SKU', key: 'sku', type: 'string' },
            { label: 'MwSt. Code', key: 'vat_code', type: 'string' }
        ];

        return (
            <div className="invoice__overlay-group-item" key={`${newKeyPath.join('.')}`} style={{ marginLeft: '40px' }}>
                <Popconfirm
                    title="Delete item"
                    description="Are you sure to delete item"
                    onConfirm={() => deleteLineItem(lineIndex, itemIndex)}
                    okText="Yes"
                    cancelText="No"
                >
                    <Button danger className="btn_delete-item-2"><BsTrash /></Button>
                </Popconfirm>
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
                    {renderInputModify(newKeyPath, field.value, fieldType, field.data, options, isRequired)}
                </div>
            );
        });
    };

    return <>{renderFieldsModify(info, keyPath)}</>;
}

export default ModifyFieldsInvoice3;
