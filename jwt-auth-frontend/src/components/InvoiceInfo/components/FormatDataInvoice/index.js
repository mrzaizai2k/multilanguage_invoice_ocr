import { getFrontendDefines } from "../../../../services/api";

export const formatDataInvoice = (invoiceInfo) => {
    const transformed = getFrontendDefines().reduce((acc, item) => {
        const { key, ...rest } = item;
        acc[key] = rest;
        return acc;
    }, {});

    if (!invoiceInfo || !transformed) return invoiceInfo;

    let updatedInvoiceInfo = { ...invoiceInfo };

    // Format các trường bên ngoài mảng `lines`
    Object.keys(invoiceInfo).forEach(key => {
        if (key !== 'lines' && transformed[key]) { // Bỏ qua `lines`
            const { key_name_user, type, data_type, required, data } = transformed[key];
            updatedInvoiceInfo[key] = {
                value: invoiceInfo[key],
                key_name_user,
                type,
                data_type,
                required,
                ...(type === 'select' && data ? { data } : {})
            };
        }
    });

    return updatedInvoiceInfo;
};
