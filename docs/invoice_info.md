# Invoice Types Overview

We have three types of invoices, each with a unique structure in the database. Below are the details for each `invoice_type`.

---

## Sample Document for `invoice_type` == "invoice 3"

This is the sample document saved in MongoDB for `invoice_type` == "invoice 3".

```json
{
    "_id": "ObjectId",
    "invoice_uuid": "string", //uuid of the invoice/image
    "invoice_type": "string",  // E.g., "invoice 1", "invoice 2", "invoice 3"
    "created_at": "ISODate",  // Timestamp of creation
    "created_by": "string",  // user_uuid of creator
    "last_modified_at": "ISODate",  // Timestamp of last modification
    "last_modified_by": "string",  // user_uuid of last modifier
    "status": "string",  // E.g., "not extracted", "completed"
    "invoice_image_base64": "string",  // Base64 encoded image
    "ocr_info":{
        "ori_text": "string",
        "ori_language": "string",
        "text": "string",
        "language": "string"
    },
    "translator": "string",
    "ocr_detector": "string",
    "llm_extractor": "string",
    "post_processor": "string",
    "invoice_info": {
      "amount": "number",
      "amount_change": "number",
      "amount_shipping": "number",
      "vatamount": "number",
      "amountexvat": "number",
      "currency": "string",
      "date": "ISODate",
      "purchasedate": "ISODate",
      "purchasetime": "string", 
      "vatitems": [
        {
          "amount": "number",
          "amount_excl_vat": "number",
          "amount_incl_vat": "number",
          "amount_incl_excl_vat_estimated": "boolean",
          "percentage": "number",
          "code": "string"
        }
      ],
      "vat_context": "string",
      "lines": [
        {
          "description": "string",
          "lineitems": [
            {
              "title": "string",
              "description": "string",
              "amount": "number",
              "amount_each": "number",
              "amount_ex_vat": "number",
              "vat_amount": "number",
              "vat_percentage": "number",
              "quantity": "number",
              "unit_of_measurement": "string",
              "sku": "string",
              "vat_code": "string"
            }
          ]
        }
      ],
      "paymentmethod": "string",
      "payment_auth_code": "string",
      "payment_card_number": "string",
      "payment_card_account_number": "string",
      "payment_card_bank": "string",
      "payment_card_issuer": "string",
      "payment_due_date": "ISODate",
      "terminal_number": "string",
      "document_subject": "string",
      "package_number": "string",
      "invoice_number": "string",
      "invoice_type": "string",  
      "receipt_number": "string",
      "shop_number": "string",
      "transaction_number": "string",
      "transaction_reference": "string",
      "order_number": "string",
      "table_number": "string",
      "table_group": "string",
      "server": "string",
      "merchant_name": "string",
      "merchant_id": "string",
      "merchant_coc_number": "string",
      "merchant_vat_number": "string",
      "merchant_bank_account_number": "string",
      "merchant_bank_account_number_bic": "string",
      "merchant_chain_liability_bank_account_number": "string",
      "merchant_chain_liability_amount": "number",
      "merchant_bank_domestic_account_number": "string",
      "merchant_bank_domestic_bank_code": "string",
      "merchant_website": "string",
      "merchant_email": "string",
      "merchant_address": "string",
      "merchant_street_name": "string",
      "merchant_house_number": "string",
      "merchant_city": "string",
      "merchant_municipality": "string",
      "merchant_province": "string",
      "merchant_country": "string",
      "merchant_country_code": "string",
      "merchant_phone": "string",
      "merchant_main_activity_code": "string",
      "customer_name": "string",
      "customer_number": "string",
      "customer_reference": "string",
      "customer_address": "string",
      "customer_street_name": "string",
      "customer_house_number": "string",
      "customer_city": "string",
      "customer_municipality": "string",
      "customer_province": "string",
      "customer_country": "string",
      "customer_phone": "string",
      "customer_vat_number": "string",
      "customer_coc_number": "string",
      "customer_bank_account_number": "string",
      "customer_bank_account_number_bic": "string",
      "customer_website": "string",
      "customer_email": "string",
      "document_language": "string"
    }
  }
```

---

## Sample Document for `invoice_type` == "invoice 1"

This is the sample document saved in MongoDB for `invoice_type` == "invoice 1".

```json
{
  "invoice_info": {
    "name": "",
    "project_number": "",
    "customer": "",
    "city": "",
    "kw": "",
    "land": "",
    "lines": [
      {
        "date": "",
        "start_time": "",
        "end_time": "",
        "break_time": "",
        "description": "",
        "has_customer_signature": true //bolean true/false
      }
    ],
    "is_process_done": true,
    "is_commissioned_work": true,
    "is_without_measuring_technology": false,
    "sign_date": "",
    "has_employee_signature": true
  }
}
```

---

## Sample Document for `invoice_type` == "invoice 2"

This is the sample document saved in MongoDB for `invoice_type` == "invoice 2".

```json
{
  "invoice_info": {
    "name": "",
    "project_number": "",
    "is_in_egw": true,
    "currency": "",
    "has_employee_signature": true,
    "sign_date": "",
    "fixed_lines": [
      {
        "title": "Hotel",
        "with_breakfast": true,
        "can_book_again": true,
        "amount": "",
        "payment_method": ""
      },
      {
        "title": "Fuel",
        "amount": "",
        "payment_method": ""
      },
      {
        "title": "Parking fees",
        "amount": "",
        "payment_method": ""
      },
      {
        "title": "Rental car",
        "amount": "",
        "payment_method": ""
      },
      {
        "title": "Toll",
        "amount": "",
        "payment_method": ""
      }
    ],
    "lines": [
      {
        "title": "",
        "amount": "",
        "payment_method": ""
      }
    ]
  }
}
```

**Note:** 
- The `fixed_lines` field includes items that always appear in the invoice, such as "Hotel" which has additional fields `can_book_again` and `with_breakfast`.
- The `lines` field can be expanded to include more items.
- "payment_method" has 4 values "self paid", "visa", "invoice to the company", empty string "".
