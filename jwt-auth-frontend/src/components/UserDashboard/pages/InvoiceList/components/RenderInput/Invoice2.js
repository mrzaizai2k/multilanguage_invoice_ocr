import React from "react";
import fieldLabels from "../../../../../../config/fieldLabels";

const renderFieldInvoice2 = (info) => {
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

    const renderLines = (lines, key) => {
        return lines.map((line, index) => (
            <div key={index} className="invoice__overlay-group-item" style={{ marginLeft: `${20}px` }}>
                <h4>{fieldLabels[key] || key} {index + 1}</h4>
                {Object.entries(line).map(([lineKey, lineValue]) => (
                    <div key={lineKey} className="invoice__overlay-input" style={{ marginLeft: `${20}px` }}>
                        <label>{fieldLabels[lineKey] || lineKey}</label>
                        {renderInput(lineKey, lineValue)}
                    </div>
                ))}
            </div>
        ));
    };

    return (
        <div className="invoice__overlay">
            {Object.entries(info).map(([key, value]) => {
                if (key === 'fixed_lines' || key === 'lines') {
                    return (
                        <div className="invoice__overlay-group" key={key}>
                            <h4>{fieldLabels[key] || key}</h4>
                            {renderLines(value, key)}
                        </div>
                    );
                } else {
                    return (
                        <div className="invoice__overlay-input" key={key} style={{ marginLeft: `${20}px` }}>
                            <label>{fieldLabels[key] || key}</label>
                            {renderInput(key, value)}
                        </div>
                    );
                }
            })}
        </div>
    );
};

export default renderFieldInvoice2;
