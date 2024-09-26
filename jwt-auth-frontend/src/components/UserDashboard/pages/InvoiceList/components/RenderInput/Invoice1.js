import React from "react";
import fieldLabels from "../../../../../../config/fieldLabels";

// Hàm render input cho các loại dữ liệu khác nhau
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

// Hàm kiểm tra xem đối tượng có trống hay không
const isEmptyObject = (obj) => {
    return Object.values(obj).every(value => value === null || value === '' || (Array.isArray(value) && value.length === 0));
};

// Hàm render chính dựa trên cấu trúc `invoice_info`
const renderFieldInvoice1 = (info) => {
    if (!info || typeof info !== 'object') {
        return <div>No information available</div>;
    }

    return (
        <div className="invoice__overlay">
            {Object.entries(info)
                .filter(([key, value]) => {
                    return value !== null && value !== undefined && value !== '' && !(Array.isArray(value) && value.length === 0);
                })
                .map(([key, value]) => {
                    // Xử lý đối tượng
                    if (typeof value === 'object' && !Array.isArray(value)) {
                        if (isEmptyObject(value)) return null;
                        return (
                            <div className="invoice__overlay-detail" key={key}>
                                {renderFieldInvoice1(value)} {/* Đệ quy cho object lồng nhau */}
                            </div>
                        );
                    }
                    // Xử lý mảng cho phần `lines`
                    else if (Array.isArray(value)) {
                        return (
                            <div className="invoice__overlay-group" key={key} style={{ marginLeft: `${20}px` }}>
                                <h4>{fieldLabels[key] || key}</h4>
                                {value.map((item, index) => {
                                    if (isEmptyObject(item)) return null;
                                    return (
                                        <div className="invoice__overlay-group-item" key={index}>
                                            {Object.entries(item).map(([itemKey, itemValue]) => (
                                                <div className="invoice__overlay-input" key={itemKey}>
                                                    <label>{fieldLabels[itemKey] || itemKey}</label>
                                                    {renderInput(itemKey, itemValue)}
                                                </div>
                                            ))}
                                        </div>
                                    );
                                })}
                            </div>
                        );
                    }
                    // Xử lý các giá trị khác
                    else {
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

export default renderFieldInvoice1;
