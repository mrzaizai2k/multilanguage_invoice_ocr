import fieldLabels from "../../../../config/fieldLabels";
import { BsPlusSquare } from 'react-icons/bs';
import moment from 'moment';
import { Select } from "antd";

function ModifyFieldsInvoice2({ info, keyPath = [], onChange }) {
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

        onChange(keyPath, value);
    };

    const addNewLine = () => {
        const currentLines = Array.isArray(info?.lines) ? info.lines : [];
        const newItem = {
            title: '',
            amount: 0,
            payment_method: ''
        };
        const updatedLines = [newItem, ...currentLines];
        handleInputChange([...keyPath, 'lines'], updatedLines);
    };

    const renderInputModify = (keyPath, value, fieldType, options = [], disabled = false) => {
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
                        disabled={disabled}
                    />
                );
            case 'string':
                return (
                    <input
                        key={key}
                        type="text"
                        value={value || ''}
                        onChange={(e) => handleInputChange(keyPath, e.target.value)}
                        disabled={disabled}
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
                            (option?.props.children ?? '').toLowerCase().includes(input.toLowerCase())
                        }
                        disabled={disabled}
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
                        disabled={disabled}
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
                        disabled={disabled}
                    />
                );
            default:
                return null;
        }
    };

    const renderLineItem = (item, index, keyPath, fields) => {
        const newKeyPath = [...keyPath, index];

        return (
            <div className="invoice__overlay-group-item" key={`${newKeyPath.join('.')}.${index}`} style={{ marginLeft: '20px' }}>
                {fields.map(({ label, key, type, options = [] }) => {

                    if (key === 'payment_method') {
                        options = [
                            "Visa",
                            "Self Paid",
                            "Invoice to Company",
                            "None",
                        ];
                    }

                    return (
                        <div key={key} className='invoice__overlay-input' style={{ marginLeft: '20px' }}>
                            <label>{label}</label>
                            {renderInputModify([...newKeyPath, key], item[key], type, options)}
                        </div>
                    );
                })}
            </div>
        );
    };

    const renderFieldsModify = (info, keyPath = []) => {
        return Object.entries(info || {}).map(([key, field]) => {
            const newKeyPath = [...keyPath, key];

            if (key === 'fixed_lines' && Array.isArray(field.value)) {
                const fields = [
                    { label: 'Title', key: 'title', type: 'string', disabled: true },
                    { label: 'Amount', key: 'amount', type: 'number' },
                    {
                        label: 'Payment Method', key: 'payment_method', type: 'select', options: [
                            "Visa",
                            "Self Paid",
                            "Invoice to Company",
                            "None",
                        ]
                    }
                ];
            
                return (
                    <div className="invoice__overlay-group" key={newKeyPath.join('.')} style={{ marginLeft: '20px' }}>
                        <div className="invoice__overlay-label">
                            <h4>{fieldLabels[key] || field.key_name_user || key}</h4>
                        </div>
                        {field.value.map((item, index) => (
                            <div key={index} className="invoice__overlay-group-item">
                                {fields.map((f) => (
                                    <div key={f.key} className='invoice__overlay-input' style={{ marginLeft: '20px' }}>
                                        <label>{f.label}</label>
                                        {renderInputModify([...newKeyPath, index, f.key], item[f.key], f.type, f.options, f.key === 'title' ? true : false)}
                                    </div>
                                ))}
                                {item.with_breakfast !== undefined && (
                                    <div className='invoice__overlay-input' style={{ marginLeft: '20px' }}>
                                        <label>With Breakfast</label>
                                        {renderInputModify([...newKeyPath, index, 'with_breakfast'], item.with_breakfast, 'boolean')}
                                    </div>
                                )}
                                {item.can_book_again !== undefined && (
                                    <div className='invoice__overlay-input' style={{ marginLeft: '20px' }}>
                                        <label>Can Book Again</label>
                                        {renderInputModify([...newKeyPath, index, 'can_book_again'], item.can_book_again, 'boolean')}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                );
            }

            if (key === 'lines' && Array.isArray(field)) {
                const fields = [
                    { label: 'Title', key: 'title', type: 'string' },
                    { label: 'Amount', key: 'amount', type: 'number' },
                    { label: 'Payment Method', key: 'payment_method', type: 'select', options: [
                        "Visa",
                        "Self Paid",
                        "Invoice to Company",
                        "None",
                    ]}
                ];

                return (
                    <div className="invoice__overlay-group" key={newKeyPath.join('.')} style={{ marginLeft: '20px' }}>
                        <div className="invoice__overlay-label">
                            <h4>{fieldLabels[key] || key}</h4>
                            <button type="button" onClick={addNewLine}>
                                <BsPlusSquare />
                                Add Line Item
                            </button>
                        </div>
                        {field.map((item, index) => renderLineItem(item, index, newKeyPath, fields))}
                    </div>
                );
            }

            const fieldType = field.data_type || field.type || 'string';
            const options = field.type === 'select' ? field.data : [];
            const label = field.key_name_user || fieldLabels[key] || key;
            const isRequired = field.required;

            if (fieldType === 'checkbox' || fieldType === 'boolean') {
                return (
                    <div className="invoice__overlay-input" key={newKeyPath.join('.')} style={{ marginLeft: '20px' }}>
                        <label>{label}</label>
                        {renderInputModify(newKeyPath, field.value, 'boolean')}
                    </div>
                );
            }

            return (
                <div className="invoice__overlay-input" key={newKeyPath.join('.')} style={{ marginLeft: '20px' }}>
                    <label>
                        {label}
                        {isRequired && <span style={{ color: 'red', fontSize: "18px" }}> * </span>}
                    </label>
                    {renderInputModify(newKeyPath, field.value, fieldType, options)}
                </div>
            );
        });
    };

    return <>{renderFieldsModify(info, keyPath)}</>;
}

export default ModifyFieldsInvoice2;
