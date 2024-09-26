import React from 'react';
import fieldLabels from "../../../../../../config/fieldLabels";

function InvoiceModifyFields({ info, keyPath = [], onChange }) {

    const handleInputChange = (keyPath, value) => {
        onChange(keyPath, value);
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
                        <h4>{fieldLabels[key] || key}</h4>
                        {value.map((item, index) => (
                            <div className="invoice__overlay-group-item" key={`${newKeyPath.join('.')}.${index}`}>
                                {typeof item === 'object' && item !== null ? renderFieldsModify(item, [...newKeyPath, index]) : renderInputModify([...newKeyPath, index], item)}
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

export default InvoiceModifyFields;
