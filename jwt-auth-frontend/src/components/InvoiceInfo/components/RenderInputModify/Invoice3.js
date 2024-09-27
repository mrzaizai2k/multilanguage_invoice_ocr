import React from 'react';
import fieldLabels from "../../../../config/fieldLabels";
import { BsPlusSquare } from 'react-icons/bs';

function ModifyFieldsInovice3({ info, keyPath = [], onChange }) {

    const handleInputChange = (keyPath, value) => {
        onChange(keyPath, value);
    };

    const addNewLineItem = (lineIndex) => {
        const currentLines = Array.isArray(info?.lines) ? info.lines : [];
        const line = currentLines[lineIndex];

        // Create a new line item based on the structure of lineitems
        const newItem = {
            title: '',
            description: '',
            amount: 0,
            amount_each: 0,
            amount_ex_vat: 0,
            vat_amount: 0,
            vat_percentage: 0,
            quantity: 1,
            unit_of_measurement: '',
            sku: '',
            vat_code: ''
        };

        // Ensure the current line has a valid lineitems array
        const updatedLine = {
            ...line,
            lineitems: [...(line.lineitems || []), newItem]
        };

        // Update the lines array with the new item in the specified line
        const updatedLines = [
            ...currentLines.slice(0, lineIndex),
            updatedLine,
            ...currentLines.slice(lineIndex + 1)
        ];

        handleInputChange([...keyPath, 'lines'], updatedLines);
    };

    const renderInputModify = (keyPath, value) => {
        const key = keyPath.join('.');

        if (typeof value === 'number' || value === null) {
            return (
                <input
                    key={key}
                    type="number"
                    value={value === null ? '' : value}
                    placeholder="Enter number"
                    onChange={(e) => {
                        const newValue = e.target.value === '' ? null : Number(e.target.value);
                        handleInputChange(keyPath, newValue);
                    }}
                />
            );
        }
        if (typeof value === 'string') {
            return (
                <input
                    key={key}
                    type="text"
                    value={value || ''}
                    onChange={(e) => handleInputChange(keyPath, e.target.value)}
                />
            );
        }
        if (typeof value === 'boolean') {
            return (
                <input
                    key={key}
                    type="checkbox"
                    checked={value || false}
                    onChange={(e) => handleInputChange(keyPath, e.target.checked)}
                />
            );
        }
        return null;
    };

    const renderFieldsModify = (info, keyPath = []) => {
        return Object.entries(info || {}).map(([key, value]) => {
            const newKeyPath = [...keyPath, key];

            if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                return (
                    <div className="invoice__overlay-detail" key={newKeyPath.join('.')}>
                        {renderFieldsModify(value, newKeyPath)}
                    </div>
                );
            } else if (Array.isArray(value)) {
                return (
                    <div className="invoice__overlay-group" key={newKeyPath.join('.')} style={{ marginLeft: `${20}px` }}>
                        <div className='invoice__overlay-label'>
                            <h4>{fieldLabels[key] || key}</h4>
                            {key === 'lineitems' && (
                                <button type="button" onClick={() => addNewLineItem(keyPath[keyPath.length - 1])}>
                                    <BsPlusSquare />
                                    Add Line Item
                                </button>
                            )}
                        </div>
                        {value.slice().reverse().map((item, index) => (
                            <div className="invoice__overlay-group-item" key={`${newKeyPath.join('.')}.${index}`}>
                                {typeof item === 'object' && item !== null
                                    ? renderFieldsModify(item, [...newKeyPath, index])
                                    : renderInputModify([...newKeyPath, index], item)}
                            </div>
                        ))}
                    </div>
                );
            } else {
                return (
                    <div className="invoice__overlay-input" key={newKeyPath.join('.')} style={{ marginLeft: `${20}px` }}>
                        <label>{fieldLabels[key] || key}</label>
                        {renderInputModify(newKeyPath, value)}
                    </div>
                );
            }
        });
    };

    return <>{renderFieldsModify(info, keyPath)}</>;
}

export default ModifyFieldsInovice3;
