import { useEffect, useState } from "react";
import fieldLabels from "../../config/fieldLabels";
import { BsX, BsPencilSquare, BsTrash3Fill } from "react-icons/bs";
import { MdOutlineSave, MdInfo } from "react-icons/md";
import "./InvoiceInfo.css";
import { message, Skeleton, Modal } from 'antd';
import { deleteInvoice, getInvoiceDetail, updateInvoice } from "../../services/api";
import ModifyFieldsInovice1 from "./components/RenderInputModify/Invoice1";
import ModifyFieldsInovice2 from "./components/RenderInputModify/Invoice2";
import ModifyFieldsInovice3 from "./components/RenderInputModify/Invoice3";
import renderFields from "./components/RenderInput";
import { formatDataInvoice } from "./components/FormatDataInvoice";

const { confirm } = Modal;

function InvoiceInfo({ userData, invoiceId, onClose, onInvoiceDeleted }) {
    const [invoiceDetails, setInvoiceDetails] = useState({});
    const [isInvoiceOpen, setInvoiceOpen] = useState(false);
    const [isModifyMode, setIsModifyMode] = useState(false);
    const [isClosing, setIsClosing] = useState(false);
    const [modifiedInvoice, setModifiedInvoice] = useState({});
    const [messageApi, contextHolder] = message.useMessage();
    const [validationErrors1, setValidationErrors1] = useState({});
    const [validationErrors23, setValidationErrors23] = useState({});

    const formatInvoiceInfo = formatDataInvoice(modifiedInvoice?.invoice_info)

    const validateFieldsInvoice1 = (info) => {
        const errors = {};

        const checkRequiredFields = (fields) => {
            Object.entries(fields).forEach(([key, field]) => {
                if (field?.required && (!field.value || field.value === '')) {
                    errors[key] = `${field.key_name_user || fieldLabels[key]} is required`;
                }
                if (typeof field === 'object' && field !== null && !Array.isArray(field)) {
                    checkRequiredFields(field);
                }
            });
        };

        checkRequiredFields(info);

        if (Array.isArray(info.lines)) {
            info.lines.forEach((line, index) => {
                const fields = [
                    { label: 'Date', key: 'date', required: true },
                    { label: 'Start Time', key: 'start_time', required: true },
                    { label: 'End Time', key: 'end_time', required: true },
                    { label: 'Break Time', key: 'break_time', required: true },
                    { label: 'Description', key: 'description', required: false },
                    { label: 'Has Customer Signature', key: 'has_customer_signature', required: false }
                ];

                fields.forEach(({ key, label, required }) => {
                    if (required && (!line[key] || line[key] === '')) {
                        errors[`lines[${index}].${key}`] = `${label} is required`;
                    }
                });
            });
        }

        setValidationErrors1(errors);
        return Object.keys(errors).length === 0;
    };

    const validateFieldsInvoice23 = (info) => {
        const errors = {};

        const checkRequiredFields = (fields) => {
            Object.entries(fields).forEach(([key, field]) => {
                if (field?.required && (!field.value || field.value === '')) {
                    errors[key] = `${field.key_name_user || fieldLabels[key]} is required`;
                }
                if (typeof field === 'object' && field !== null && !Array.isArray(field)) {
                    checkRequiredFields(field);
                }
            });
        };

        checkRequiredFields(info);
        setValidationErrors23(errors);
        return Object.keys(errors).length === 0;
    };

    const openModifyMode = () => {
        setIsModifyMode(true);
        setModifiedInvoice({ ...invoiceDetails });
    };

    const saveModifiedInvoice = async () => {
        const isValid = validateFieldsInvoice1(formatInvoiceInfo) || validateFieldsInvoice23(formatInvoiceInfo);

        if (!isValid) {
            messageApi.open({
                type: "error",
                content: "Please fill all required fields!",
                duration: 5,
            });
            return;
        }

        try {
            await updateInvoice(modifiedInvoice._id, modifiedInvoice);
            messageApi.open({
                type: "success",
                content: "Invoice updated successfully!",
                duration: 5,
            });
            setInvoiceDetails(modifiedInvoice);
            setIsModifyMode(false);
        } catch (error) {
            console.error('Error saving modified invoice:', error);
            messageApi.open({
                type: "error",
                content: "Invoice update failed!",
                duration: 6,
            });
        }
    };

    const showDeleteConfirm = () => {
        confirm({
            title: 'Are you sure to delete this invoice?',
            icon: <MdInfo />,
            content: 'This action cannot be undone.',
            okText: 'Yes',
            okType: 'danger',
            cancelText: 'No',
            onOk: async () => {
                try {
                    await deleteInvoice(invoiceDetails._id, userData);
                    setInvoiceOpen(false);
                    onClose();
                    onInvoiceDeleted(invoiceDetails._id);
                } catch (error) {
                    console.error('Error deleting invoice:', error);
                }
            },
            onCancel() {
                console.log('Cancel');
            },
        });
    };

    useEffect(() => {
        setInvoiceOpen(true);
        const fetchApi = async () => {
            const response = await getInvoiceDetail(invoiceId);
            setInvoiceDetails(response.data.invoices[0]);
            setModifiedInvoice({ ...response.data.invoices[0] });
        };
        fetchApi();
    }, [invoiceId]);

    const closeInvoice = () => {
        setIsClosing(true);
        setTimeout(() => {
            setInvoiceOpen(false);
            setIsClosing(false);
            onClose();
        }, 100);
    };

    const handleChange = (keyPath, value) => {
        const newModifiedInvoice = { ...modifiedInvoice };
        let current = newModifiedInvoice.invoice_info;

        for (let i = 0; i < keyPath.length - 1; i++) {
            current = current[keyPath[i]];
        }
        current[keyPath[keyPath.length - 1]] = value;

        setModifiedInvoice(newModifiedInvoice);
    };

    return (
        <>
            {contextHolder}
            <div className="invoice__info">
                <div className={`invoice__overlay ${isInvoiceOpen ? "active" : ""}`} onClick={closeInvoice}></div>
                <div className={`invoice__overlay-content ${isInvoiceOpen ? "active" : ""} ${isClosing ? "closing" : ""}`}>
                    <div className="invoice__overlay-header">
                        <h2>Invoice Information</h2>
                        <button className="close-btn" onClick={closeInvoice}>
                            <BsX />
                        </button>
                    </div>

                    {invoiceDetails ? (
                        <div className="invoice__overlay-detail">
                            {isModifyMode ? (
                                <>
                                    {invoiceDetails.invoice_type === 'invoice 1' ? (
                                        <ModifyFieldsInovice1
                                            info={formatInvoiceInfo || {}}
                                            onChange={handleChange}
                                            validationErrors={validationErrors1}
                                        />
                                    ) : invoiceDetails.invoice_type === 'invoice 2' ? (
                                        <ModifyFieldsInovice2
                                            info={formatInvoiceInfo || {}}
                                            onChange={handleChange}
                                            validationErrors={validationErrors23}
                                        />
                                    ) : (
                                        <ModifyFieldsInovice3
                                            info={formatInvoiceInfo || {}}
                                            onChange={handleChange}
                                            validationErrors={validationErrors23}
                                        />
                                    )}
                                </>
                            ) : (
                                renderFields(invoiceDetails.invoice_info || {})
                            )}
                        </div>
                    ) : (
                        <>
                            <Skeleton active={true} />
                            <br />
                            <Skeleton active={true} />
                        </>
                    )}

                    <div className="invoice__overlay-btn">
                        {isModifyMode ? (
                            <>
                                <button onClick={saveModifiedInvoice}><MdOutlineSave /> Save</button>
                            </>
                        ) : (
                            <>
                                <button onClick={openModifyMode}><BsPencilSquare /> Modify</button>
                                <button onClick={showDeleteConfirm}><BsTrash3Fill /> Delete</button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}

export default InvoiceInfo;
