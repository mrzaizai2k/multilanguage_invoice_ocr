/* eslint-disable no-unused-vars */
import { useEffect, useState } from "react";
import { PhotoProvider, PhotoView } from "react-photo-view";
import 'react-photo-view/dist/react-photo-view.css';
import { MdInfo, MdOutlineZoomOutMap } from "react-icons/md";
import { BsTrash3Fill, BsEye } from "react-icons/bs";
import "./InvoiceList.css";
import { message, Modal, Pagination, Skeleton } from 'antd';
import { Helmet } from 'react-helmet';
import { getAllInvoices, deleteInvoice } from "../../../services/api";
import InvoiceInfo from "../../../components/InvoiceInfo";
const { confirm } = Modal;

function InvoiceList({ userData }) {
    const [invoices, setInvoices] = useState([]);
    const [selectedInvoiceId, setSelectedInvoiceId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filterDate, setFilterDate] = useState('');
    const [filterType, setFilterType] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalItems, setTotalItems] = useState(0);
    const [pageSize, setPageSize] = useState(10);
    const [messageApi, contextHolder] = message.useMessage();

    useEffect(() => {
        const fetchApi = async () => {
            setLoading(true);
            const response = await getAllInvoices(filterDate, filterType, currentPage, pageSize);
            setInvoices(response.data.invoices);
            setTotalItems(response.data.total);
            setLoading(false);
        };
        fetchApi();
    }, [filterDate, filterType, currentPage, pageSize]);

    const handleViewClick = (id) => setSelectedInvoiceId(id);
    const handleCloseInvoice = () => setSelectedInvoiceId(null);

    const handleInvoiceDeleted = (deletedInvoiceId) => {
        setInvoices((prevInvoices) => prevInvoices.filter(invoice => invoice._id !== deletedInvoiceId));
        messageApi.success("Invoice deleted successfully!");
    };

    const handleDeleteInvoice = (invoiceId) => {
        confirm({
            title: 'Are you sure to delete this invoice?',
            icon: <MdInfo />,
            content: 'This action cannot be undone.',
            okText: 'Yes',
            okType: 'danger',
            cancelText: 'No',
            onOk: async () => {
                try {
                    await deleteInvoice(invoiceId, userData);
                    handleInvoiceDeleted(invoiceId);
                } catch (error) {
                    messageApi.error("Failed to delete invoice!");
                }
            },
        });
    };

    const handlePageChange = (page) => setCurrentPage(page);

    const Base64Image = ({ base64String, alt }) => (
        <img src={`data:image/jpeg;base64,${base64String}`} alt={alt} />
    );

    return (
        <>
            {contextHolder}
            <Helmet>
                <title>Invoice List</title>
            </Helmet>

            <div className="invoice__header">
                <h2 className="invoice__title">Invoice List</h2>
                <div className="invoice__filter">
                    <select
                        className="invoice__filter-date"
                        title="Sort by Date"
                        value={filterDate}
                        onChange={(e) => setFilterDate(e.target.value)}
                    >
                        <option value="">All</option>
                        <option value="desc">Newest First</option>
                        <option value="asc">Oldest First</option>
                    </select>
                    <select
                        className="invoice__filter-type"
                        title="Invoice Type"
                        value={filterType}
                        onChange={(e) => setFilterType(e.target.value)}
                    >
                        <option value="">All</option>
                        <option value="invoice 1">Invoice 1</option>
                        <option value="invoice 2">Invoice 2</option>
                        <option value="invoice 3">Invoice 3</option>
                    </select>
                </div>
            </div>

            <div className="invoice__list">
                {loading ? (
                    Array.from({ length: 7 }).map((_, index) => (
                        <Skeleton.Image key={index} active={true} style={{ width: "180px", height: "230px", margin: "15px" }} />
                    ))
                ) : (
                    <PhotoProvider
                        toolbarRender={({ rotate, onRotate }) => {
                            return (
                                <svg
                                    className="PhotoView-Slider__toolbarIcon"
                                    onClick={() => onRotate(rotate + 90)}
                                    width="44"
                                    height="44"
                                    viewBox="0 0 768 768"
                                    fill="white"
                                >
                                    <path d="M565.5 202.5l75-75v225h-225l103.5-103.5c-34.5-34.5-82.5-57-135-57-106.5 0-192 85.5-192 192s85.5 192 192 192c84 0 156-52.5 181.5-127.5h66c-28.5 111-127.5 192-247.5 192-141 0-255-114-255-255s114-255 255-255c70.5 0 135 28.5 181.5 72z" />
                                </svg>
                            );
                        }}>
                        {invoices.map((item, index) => (
                            <div className="invoice__item" key={index}>
                                {item.invoice_image_base64 &&
                                    <Base64Image base64String={item.invoice_image_base64} alt={`Invoice ${index + 1}`} />
                                }
                                <div className="invoice__item-overlay">
                                    <PhotoView src={`data:image/jpeg;base64,${item.invoice_image_base64}`}>
                                        <button className="zoom-btn"><MdOutlineZoomOutMap /></button>
                                    </PhotoView>
                                    <button className="delete-btn" onClick={() => handleDeleteInvoice(item._id)}>
                                        <BsTrash3Fill />
                                    </button>
                                    <button className="view-btn" onClick={() => handleViewClick(item._id)}>
                                        <BsEye /> <b>View</b>
                                    </button>
                                </div>
                            </div>
                        ))}
                    </PhotoProvider>
                )}
            </div>

            <Pagination
                align="center"
                current={currentPage}
                total={totalItems}
                pageSize={pageSize}
                onChange={handlePageChange}
            />

            {selectedInvoiceId && (
                <InvoiceInfo
                    invoiceId={selectedInvoiceId}
                    onClose={handleCloseInvoice}
                    onInvoiceDeleted={handleInvoiceDeleted}
                    userData={userData}
                />
            )}
        </>
    );
}

export default InvoiceList;
