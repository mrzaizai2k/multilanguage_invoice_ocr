import React from "react";
import fieldLabels from "../../../../config/fieldLabels";
import moment from "moment";

const renderFields = (info) => {
const renderInput = (key, value) => {
    if (typeof value === 'string' && moment(value, moment.ISO_8601, true).isValid()) {
        return <div><input key={key} type="date" defaultValue={moment(value).format('YYYY-MM-DD')} disabled/></div>
    }
    if (typeof value === 'string' && moment(value, 'HH:mm', true).isValid()) {
        return <div><input key={key} type="time" defaultValue={moment(value, 'HH:mm').format('HH:mm')} disabled/></div>
    }
    if (typeof value === 'string') {
        return <div><input key={key} type="text" defaultValue={value} disabled/></div>
    }
    if (typeof value === 'number') {
        return <div><input key={key} type="number" defaultValue={value} disabled/></div>;
    }
    if (typeof value === 'boolean') {
        return <div><input key={key} type="checkbox" defaultChecked={value} disabled/></div>
    }
    return null;
};

    const isEmptyObject = (obj) => {
        return Object.values(obj).every(value => value === null || value === '' || (Array.isArray(value) && value.length === 0));
    };

    const isEmptyVatItem = (vatItems) => {
        return vatItems.every(item => {
            return Object.values(item).every(value => value === null || value === '');
        });
    };

    return Object.entries(info)
        .filter(([key, value]) => {
            return value !== null && value !== undefined && value !== '' && !(Array.isArray(value) && value.length === 0);
        })
        .map(([key, value]) => {
            if (typeof value === 'object' && !Array.isArray(value)) {
                if (isEmptyObject(value)) return null;
                return (
                    <div className="invoice__overlay-detail" key={key}>
                        {renderFields(value)}
                    </div>
                );
            } else if (Array.isArray(value)) {
                if (key === 'vatitems' && isEmptyVatItem(value)) return null;
                return (
                    <div className="invoice__overlay-group" key={key} style={{ marginLeft: `${20}px` }}>
                        <h4>{fieldLabels[key] || key}</h4>
                        {value.map((item, index) => {
                            if (isEmptyObject(item)) return null;
                            return (
                                <div className="invoice__overlay-group-item" key={index}>
                                    {typeof item === 'object' ? renderFields(item) : renderInput(key, item)}
                                </div>
                            );
                        })}
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
        });
};

export default renderFields;
