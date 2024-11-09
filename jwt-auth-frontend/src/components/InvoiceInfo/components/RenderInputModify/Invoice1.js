import fieldLabels from "../../../../config/fieldLabels";
import { BsPlusSquare, BsTrash } from 'react-icons/bs';
import moment from 'moment';
import { Button, Popconfirm, Select } from "antd";

function ModifyFieldsInvoice1({ info, keyPath = [], onChange, validationErrors }) {
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

    const deleteLine = (index) => {
        const currentLines = Array.isArray(info?.lines) ? info.lines : [];
        const updatedLines = currentLines.filter((_, i) => i !== index);
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
                            type="text" // Changed type to "text" to allow string input, we will handle conversion later
                            value={value === null ? '' : value.toString()} // Ensure value is a string
                            onChange={(e) => {
                                const newValue = e.target.value;
                                if (newValue === '' || /^\d*\.?\d*$/.test(newValue)) {
                                    // Ensure we're sending a string representation of the number, not the number itself
                                    const parsedValue = newValue === '' ? null : newValue; // Store as string
                                    handleInputChange(keyPath, parsedValue);
                                }
                            }}
                            onKeyDown={(e) => {
                                if (e.key === '.' && e.target.value.includes('.')) {
                                    e.preventDefault();
                                }
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
                            placeholder="Select a person"
                            filterOption={(input, option) =>
                                (option?.props.children ?? '').toLowerCase().includes(input.toLowerCase())
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
            default:
                return null;
        }
    };

    const renderLineItem = (item, index, keyPath) => {
        const newKeyPath = [...keyPath, index];
        const fields = [
            { label: 'Datum', key: 'date', type: 'date', required: true },
            { label: 'Start Uhrzeit', key: 'start_time', type: 'time', required: true },
            { label: 'Ende Uhrzeit', key: 'end_time', type: 'time', required: true },
            { label: 'Pausenzeit', key: 'break_time', type: 'number', required: true },
            { label: 'Beschreibung', key: 'description', type: 'string', required: false },
            { label: 'Ist die Unterschrift des Kunden vorhanden?', key: 'has_customer_signature', type: 'boolean', required: false }
        ];

        return (
            <div className="invoice__overlay-group-item" key={`${newKeyPath.join('.')}.${index}`} style={{ marginLeft: '20px' }}>
                <Popconfirm
                    title="Delete item"
                    description="Are you sure to delete item"
                    onConfirm={() => deleteLine(index)}
                    okText="Yes"
                    cancelText="No"
                >
                    <Button danger className="btn_delete-item"><BsTrash /></Button>
                </Popconfirm>
                {fields.map(({ label, key, type, required }) => (
                    <div key={key} className='invoice__overlay-input' style={{ marginLeft: '20px' }}>
                        <label>
                            {label}
                            {required && <span style={{ color: 'red', fontSize: "18px" }}> * </span>}
                        </label>
                        {renderInputModify([...newKeyPath, key], item[key], type, false, required)}
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
                        {renderInputModify(newKeyPath, field.value, 'boolean', isRequired)}
                    </div>
                );
            }

            return (
                <div className="invoice__overlay-input" key={newKeyPath.join('.')} style={{ marginLeft: '20px' }}>
                    <label>
                        {label}
                        {isRequired && <span style={{ color: 'red', fontSize: "18px" }}> * </span>}
                    </label>
                    {renderInputModify(newKeyPath, field.value, fieldType, options, isRequired)}
                </div>
            );
        });
    };

    return <>{renderFieldsModify(info, keyPath)}</>;
}

export default ModifyFieldsInvoice1;