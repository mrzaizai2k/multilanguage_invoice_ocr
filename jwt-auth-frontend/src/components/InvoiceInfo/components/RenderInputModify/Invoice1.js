import fieldLabels from "../../../../config/fieldLabels";
import { BsPlusSquare } from 'react-icons/bs';
import moment from 'moment';
import { Select } from "antd";

function ModifyFieldsInvoice1({ info, keyPath = [], onChange }) {
    const handleInputChange = (keyPath, value) => {
        onChange(keyPath, value);
    };

    const addNewLine = () => {
        const currentLines = Array.isArray(info?.lines) ? info.lines : [];
        const newItem = {
            date: '',
            start_time: '',
            end_time: '',
            break_time: '',
            description: '',
            has_customer_signature: false
        };
        const updatedLines = [newItem, ...currentLines];
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
                        placeholder="Select a person"
                        filterOption={(input, option) =>
                            (option?.props.children ?? '').toLowerCase().includes(input.toLowerCase())
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
            default:
                return null;
        }
    };

    const renderLineItem = (item, index, keyPath) => {
        const newKeyPath = [...keyPath, index];
        const fields = [
            { label: 'Date', key: 'date', type: 'date', required: true },
            { label: 'Start Time', key: 'start_time', type: 'time', required: true  },
            { label: 'End Time', key: 'end_time', type: 'time', required: true  },
            { label: 'Break Time', key: 'break_time', type: 'number', required: true  },
            { label: 'Description', key: 'description', type: 'string', required: false },
            { label: 'Has Customer Signature', key: 'has_customer_signature', type: 'boolean', required: true }
        ];

        return (
            <div className="invoice__overlay-group-item" key={`${newKeyPath.join('.')}.${index}`} style={{ marginLeft: '20px' }}>
                {fields.map(({ label, key, type, required }) => (
                    <div key={key} className='invoice__overlay-input' style={{ marginLeft: '20px' }}>
                        <label>
                            {label}
                            {required && <span style={{ color: 'red', fontSize: "18px" }}> * </span>}
                        </label>
                        {renderInputModify([...newKeyPath, key], item[key], type)}
                    </div>
                ))}
            </div>
        );
    };

    const renderFieldsModify = (info, keyPath = []) => {
        return Object.entries(info || {}).map(([key, field]) => {
            const newKeyPath = [...keyPath, key];

            if (key === 'lines' && Array.isArray(field)) {
                return (
                    <div className="invoice__overlay-group" key={newKeyPath.join('.')} style={{ marginLeft: '20px' }}>
                        <div className="invoice__overlay-label">
                            <h4>{fieldLabels[key] || key}</h4>
                            <button type="button" onClick={addNewLine}>
                                <BsPlusSquare />
                                Add Line Item
                            </button>
                        </div>
                        {field.map((item, index) => renderLineItem(item, index, newKeyPath))}
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

export default ModifyFieldsInvoice1;
