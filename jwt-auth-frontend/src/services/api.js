import axios from "axios";

export const API_URL = `http://${process.env.REACT_APP_SERVER_IP}/api`; //aws
// export const API_URL = 'http://localhost/api'; // local machine as nginx config 

console.log("API_URL", API_URL)

export const login = async (username, password) => {
    const result = await axios.post(`${API_URL}/token`,
        `username=${username}&password=${password}`,
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
    return result;
};

export const setFrontendDefines = async () => {
    try {
        const result = await axios.get(`${API_URL}/api/v1/frontend_defines`);
        if (result && result.data) {
            localStorage.setItem('frontendDefines', JSON.stringify(result.data));
        }
        return result.data;
    } catch (error) {
        console.error('Error fetching frontend defines:', error);
        return null;
    }
};

export const getFrontendDefines = () => {
    const data = localStorage.getItem('frontendDefines');
        return data ? JSON.parse(data).frontend_defines : null;
};

export const getInvoicesByUser = async (user_uuid, filterDate, filterType, currentPage, pageSize) => {
    const sortOrder = filterDate === "asc" ? "asc" : filterDate === "desc" ? "desc" : "";
    const invoiceType = filterType !== "" ? filterType : "";

    const result = await axios.get(`${API_URL}/api/v1/invoices?`, {
        params: {
            invoice_status: 'completed',
            created_by: user_uuid,
            created_at: sortOrder,
            invoice_type: invoiceType,
            page: currentPage,
            limit: pageSize
        }
    });
    return result;
};

export const getAllInvoices = async (filterDate, filterType, currentPage, pageSize) => {
    const sortOrder = filterDate === "asc" ? "asc" : filterDate === "desc" ? "desc" : "";
    const invoiceType = filterType !== "" ? filterType : "";

    const result = await axios.get(`${API_URL}/api/v1/invoices?`, {
        params: {
            invoice_status: 'completed',
            created_at: sortOrder,
            invoice_type: invoiceType,
            page: currentPage,
            limit: pageSize
        }
    });
    return result;
};

export const getInvoiceDetail = async (invoiceId) => {
    const result = await axios.get(`${API_URL}/api/v1/invoices?invoice_uuid=${invoiceId}`);
    return result;
};

export const createInvoice = async (newInvoice) => {
    const result = await axios.post(`${API_URL}/api/v1/invoices/upload`, newInvoice);
    return result;
};

export const updateInvoice = async (invoiceId, updatedInvoice, user_uuid) => {
    const payload = {
        user_uuid: user_uuid,
        invoice_info: updatedInvoice
    };
    const result = await axios.put(`${API_URL}/api/v1/invoices/${invoiceId}`, payload);
    return result;
};

export const deleteInvoice = async (invoiceId, user_uuid) => {
    const result = await axios.delete(`${API_URL}/api/v1/invoices/${invoiceId}?user_uuid=${user_uuid}`);
    return result;
};
