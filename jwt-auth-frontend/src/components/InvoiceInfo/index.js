import { useEffect, useState } from "react";
import { BsXCircle, BsX, BsPencilSquare, BsTrash3Fill } from "react-icons/bs";
import { MdOutlineSave, MdInfo } from "react-icons/md";
import "./InvoiceInfo.css";
import { message, Skeleton, Modal } from 'antd';
import { deleteInvoice, getInvoiceDetail, updateInvoice } from "../../services/api";
import ModifyFieldsInovice1 from "./components/RenderInputModify/Invoice1";
import ModifyFieldsInovice2 from "./components/RenderInputModify/Invoice2";
import ModifyFieldsInovice3 from "./components/RenderInputModify/Invoice3";
import renderFields from "./components/RenderInput";

const { confirm } = Modal;

function InvoiceInfo({ userData, invoiceId, onClose, onInvoiceDeleted }) {
    const [invoiceDetails, setInvoiceDetails] = useState(null);
    const [isInvoiceOpen, setInvoiceOpen] = useState(false);
    const [isModifyMode, setIsModifyMode] = useState(false);
    const [isClosing, setIsClosing] = useState(false);
    const [modifiedInvoice, setModifiedInvoice] = useState(null);
    const [messageApi, contextHolder] = message.useMessage();

    const openModifyMode = () => {
        setIsModifyMode(true);
        setModifiedInvoice({ ...invoiceDetails });
    };

    const closeModifyMode = () => {
        setIsModifyMode(false);
        setModifiedInvoice(null);
    };

    const saveModifiedInvoice = async () => {
        try {
            await updateInvoice(modifiedInvoice._id, modifiedInvoice)
            messageApi.open({
                type: "success",
                content: "Invoice updated successfully!",
                duration: 5,
            });
            setInvoiceDetails(modifiedInvoice);
            closeModifyMode();
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
                    await deleteInvoice(invoiceDetails._id, userData)

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
            const response = await getInvoiceDetail(invoiceId)
            setInvoiceDetails(response.data.invoices[0]);
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
                                            info={modifiedInvoice?.invoice_info || {}}
                                            onChange={handleChange} />
                                    ) : invoiceDetails.invoice_type === 'invoice 2' ? (
                                        <ModifyFieldsInovice2
                                            info={modifiedInvoice?.invoice_info || {}}
                                            onChange={handleChange} />
                                    ) : (
                                        <ModifyFieldsInovice3
                                            info={modifiedInvoice?.invoice_info || {}}
                                            onChange={handleChange} />
                                    )}
                                </>
                            ) : (
                                renderFields(invoiceDetails.invoice_info || { })
                            )}
                        </div>
                    ) : (
                        <>
                            <Skeleton active={true} />
                            <br/>
                            <Skeleton active={true} />
                        </>
                    )}

                    <div className="invoice__overlay-btn">
                        {isModifyMode ? (
                            <>
                                <button onClick={saveModifiedInvoice}><MdOutlineSave /> Save</button>
                                <button onClick={closeModifyMode}><BsXCircle /> Cancel</button>
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
