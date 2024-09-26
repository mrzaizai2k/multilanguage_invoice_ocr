import React from "react";
import fieldLabels from "../../../../../../config/fieldLabels";

const renderFieldInvoice3 = (info) => {
    const renderInput = (key, value) => {
        if (typeof value === 'string') {
            return <input key={key} type="text" defaultValue={value} disabled />;
        }
        if (typeof value === 'number') {
            return <input key={key} type="number" defaultValue={value} disabled />;
        }
        if (typeof value === 'boolean') {
            return (
                <input key={key} type="checkbox" defaultChecked={value} disabled />
            );
        }
        return null;
    };

    const renderVatItems = (vatItems) => {
        return vatItems.map((item, index) => (
            <div key={index} className="invoice__overlay-group-item" style={{ marginLeft: '20px' }}>
                <h4>{`VAT Item ${index + 1}`}</h4>
                {Object.entries(item).map(([itemKey, itemValue]) => (
                    <div key={itemKey} className="invoice__overlay-input" style={{ marginLeft: '20px' }}>
                        <label>{fieldLabels[itemKey] || itemKey}</label>
                        {renderInput(itemKey, itemValue)}
                    </div>
                ))}
            </div>
        ));
    };

    const renderLineItems = (lineItems) => {
        return lineItems.map((item, index) => (
            <div key={index} className="invoice__overlay-group-item" style={{ marginLeft: '20px' }}>
                <h4>{`Line Item ${index + 1}`}</h4>
                {Object.entries(item).map(([itemKey, itemValue]) => (
                    <div key={itemKey} className="invoice__overlay-input" style={{ marginLeft: '20px' }}>
                        <label>{fieldLabels[itemKey] || itemKey}</label>
                        {renderInput(itemKey, itemValue)}
                    </div>
                ))}
            </div>
        ));
    };

    const renderLines = (lines) => {
        return lines.map((line, index) => (
            <div key={index} className="invoice__overlay-group" style={{ marginLeft: '20px' }}>
                <h4>{`Line ${index + 1}`}</h4>
                {Object.entries(line).map(([lineKey, lineValue]) => (
                    <div key={lineKey}>
                        {lineKey === 'lineitems' ? renderLineItems(lineValue) : (
                            <div className="invoice__overlay-input" style={{ marginLeft: '20px' }}>
                                <label>{fieldLabels[lineKey] || lineKey}</label>
                                {renderInput(lineKey, lineValue)}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        ));
    };

    return (
        <div className="invoice__overlay">
            {Object.entries(info).map(([key, value]) => {
                if (key === 'vatitems') {
                    return (
                        <div className="invoice__overlay-group" key={key}>
                            <h4>{fieldLabels[key] || key}</h4>
                            {renderVatItems(value)}
                        </div>
                    );
                } else if (key === 'lines') {
                    return (
                        <div className="invoice__overlay-group" key={key}>
                            <h4>{fieldLabels[key] || key}</h4>
                            {renderLines(value)}
                        </div>
                    );
                } else if (typeof value === 'object' && !Array.isArray(value)) {
                    return (
                        <div className="invoice__overlay-detail" key={key}>
                            {renderFieldInvoice3(value)}
                        </div>
                    );
                } else {
                    return (
                        <div className="invoice__overlay-input" key={key} style={{ marginLeft: '20px' }}>
                            <label>{fieldLabels[key] || key}</label>
                            {renderInput(key, value)}
                        </div>
                    );
                }
            })}
        </div>
    );
};

export default renderFieldInvoice3;
