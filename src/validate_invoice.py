import sys
sys.path.append("") 
import re
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Any, Union
from datetime import date, time, datetime


def strip_strings(value):
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            return {k: strip_strings(v) for k, v in value.items()}
        if isinstance(value, list):
            return [strip_strings(v) for v in value]
        return value

# Normalize date by converting it from string to date object
def normalize_date(value):
    try:
        return datetime.strptime(value, '%d/%m/%Y').date()
    except ValueError:
        return None

# Normalize time by converting it from string to time object
def normalize_time(value):
    try:
        return datetime.strptime(value, '%H:%M:%S').time()
    except ValueError:
        return None
        
 # Normalize currency to uppercase three-letter code
def normalize_currency(value):
    if isinstance(value, str) and len(value.strip()) == 3:
        return value.strip().upper()
    return None

def validate_invoice_3(invoice_data: dict) -> dict:

    # Normalize payment card number by removing all non-digit characters
    def normalize_payment_card_number(value):
        return re.sub(r'\D', '', value)

    # Normalize percentage to float value
    def normalize_percentage(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    # Normalize phone number by removing all non-digit characters
    def normalize_phone_number(value):
        return re.sub(r'\D', '', value)


    # Recursive function to apply normalizations and validations to the data
    def validate_and_normalize(data):
        if isinstance(data, dict):
            for key, value in data.items():
                # Strip all string values
                data[key] = strip_strings(value)
                
                # Normalize specific fields
                if 'payment_card_number' in key:
                    data[key] = normalize_payment_card_number(data[key])
                
                if 'date' in key:
                    data[key] = normalize_date(data[key])

                if 'time' in key:
                    data[key] = normalize_time(data[key])
                
                if 'percentage' in key:
                    data[key] = normalize_percentage(data[key])
                
                if 'phone' in key:
                    data[key] = normalize_phone_number(data[key])
                
                if 'currency' in key:
                    data[key] = normalize_currency(data[key])
                
                # Recursively normalize nested dictionaries or lists
                if isinstance(value, dict) or isinstance(value, list):
                    data[key] = validate_and_normalize(value)
        
        elif isinstance(data, list):
            data = [validate_and_normalize(item) for item in data]
        
        return data

    # Call the validation and normalization function
    return validate_and_normalize(invoice_data)

# Normalize break_time to float
def normalize_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
    
def validate_invoice_1(invoice_data: dict) -> dict:

    # Recursive function to apply normalizations and validations to the data
    def validate_and_normalize(data: Any, reference_year=None):
        if isinstance(data, dict):
            for key, value in data.items():
                # Strip all string values
                data[key] = strip_strings(value)
                
                if 'date' in key:
                    data[key] = normalize_date(data[key])

                if 'time' in key:
                    data[key] = normalize_time(data[key])

                if 'break_time' in key:
                    data[key] = normalize_float(data[key])
                
                # Recursively normalize nested dictionaries or lists
                if isinstance(value, dict) or isinstance(value, list):
                    data[key] = validate_and_normalize(value, reference_year)
        
        elif isinstance(data, list):
            data = [validate_and_normalize(item, reference_year) for item in data]
        
        return data

    # Call the validation and normalization function
    return validate_and_normalize(invoice_data)

def validate_invoice_2(invoice_data: dict) -> dict:
    
    # Function to normalize titles in fixed lines
    def normalize_title(title: str) -> str:
        title_lower = title.lower()
        if 'hotel' in title_lower:
            return "Hotel"
        elif 'fuel' in title_lower or 'tank' in title_lower:
            return "Fuel"
        elif 'car' in title_lower or 'mietwagen' in title_lower:
            return "Rental car"
        elif 'toll' in title_lower or 'maut' in title_lower:
            return "Toll"
        elif 'park' in title_lower:
            return "Parking fees"
        return title
    
    # Function to normalize payment methods
    def normalize_payment_method(payment_method: str) -> str:
        payment_method_lower = payment_method.lower()
        if 'visa' in payment_method_lower or 'credit' in payment_method_lower:
            return "visa"
        elif 'invoice' in payment_method_lower:
            return "invoice"
        elif 'self' in payment_method_lower:
            return "self paid"
        return ""
    
    # Function to apply normalizations and validations to the data
    def validate_and_normalize(data: Any, reference_year=None):
        if isinstance(data, dict):
            for key, value in data.items():
                # Strip all string values
                data[key] = strip_strings(value)

                # Normalize date fields
                if 'date' in key:
                    data[key] = normalize_date(data[key])

                # Normalize amount fields
                if 'amount' in key:
                    data[key] = normalize_float(data[key])

                # If the key is 'fixed_lines', normalize the title and payment_method
                if key == 'fixed_lines':
                    for line in data[key]:
                        line['title'] = normalize_title(line['title'])
                        if 'payment_method' in line:
                            line['payment_method'] = normalize_payment_method(line['payment_method'])
                
                # Recursively normalize nested dictionaries or lists
                if isinstance(value, dict) or isinstance(value, list):
                    data[key] = validate_and_normalize(value, reference_year)
        
        elif isinstance(data, list):
            data = [validate_and_normalize(item, reference_year) for item in data]

        return data

    # Call the validation and normalization function
    return validate_and_normalize(invoice_data)


################################################################################

class Line1(BaseModel):
    date: Optional[datetime] = None  # Can be a date or string in your case
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_time: Optional[float] = None
    description: Optional[str] = ""
    has_customer_signature: Optional[bool] = False

class InvoiceInfo1(BaseModel):
    name: Optional[str] = ""
    project_number: Optional[str] = ""
    customer: Optional[str] = ""
    city: Optional[str] = ""
    kw: Optional[str] = ""
    land: Optional[str] = ""
    lines: List[Line1] = Field(default_factory=lambda: [Line1()])
    is_process_done: Optional[bool] = False
    is_commissioned_work: Optional[bool] = False
    is_without_measuring_technology: Optional[bool] = False
    sign_date: Optional[datetime] = None
    has_employee_signature: Optional[bool] = False

class Invoice1(BaseModel):
    invoice_info: InvoiceInfo1

################################################################################

class FixedLine2(BaseModel):
    title: str
    amount: Optional[float] = 0.0
    payment_method: Optional[str] = ""

class HotelLine2(FixedLine2):
    with_breakfast: Optional[bool] = False
    can_book_again: Optional[bool] = False

class InvoiceInfo2(BaseModel):
    name: Optional[str] = ""
    project_number: Optional[str] = ""
    is_in_egw: Optional[bool] = True
    currency: Optional[str] = ""
    has_employee_signature: Optional[bool] = True
    sign_date: Optional[datetime] = None
    
    fixed_lines: List[Union[FixedLine2, HotelLine2]] = Field(default_factory=lambda: [
        HotelLine2(title="Hotel", with_breakfast=False, can_book_again=False, amount=0.0, payment_method=""),
        FixedLine2(title="Fuel", amount=0.0, payment_method=""),
        FixedLine2(title="Parking fees", amount=0.0, payment_method=""),
        FixedLine2(title="Rental car", amount=0.0, payment_method=""),
        FixedLine2(title="Toll", amount=0.0, payment_method="")
    ])

    lines: List[FixedLine2] = Field(default_factory=lambda: [FixedLine2(title="", amount=0.0, payment_method="")])

    @model_validator(mode='before')
    @classmethod
    def ensure_fixed_lines(cls, values):
        fixed_lines_defaults = [
            HotelLine2(title="Hotel", with_breakfast=False, can_book_again=False, amount=0.0, payment_method=""),
            FixedLine2(title="Fuel", amount=0.0, payment_method=""),
            FixedLine2(title="Parking fees", amount=0.0, payment_method=""),
            FixedLine2(title="Rental car", amount=0.0, payment_method=""),
            FixedLine2(title="Toll", amount=0.0, payment_method="")
        ]

        if 'fixed_lines' in values:
            fixed_lines = []
            for line in values['fixed_lines']:
                if isinstance(line, dict):
                    if line.get('title') == 'Hotel':
                        fixed_lines.append(HotelLine2(**line))
                    else:
                        fixed_lines.append(FixedLine2(**line))
                elif isinstance(line, (FixedLine2, HotelLine2)):
                    fixed_lines.append(line)
                else:
                    raise ValueError(f"Unexpected type for fixed_line: {type(line)}")

            values['fixed_lines'] = fixed_lines
        else:
            values['fixed_lines'] = fixed_lines_defaults

        existing_titles = {line.title for line in values['fixed_lines']}
        for default_line in fixed_lines_defaults:
            if default_line.title not in existing_titles:
                values['fixed_lines'].append(default_line)

        return values

    class Config:
        populate_by_name = True

class Invoice2(BaseModel):
    invoice_info: InvoiceInfo2

    class Config:
        populate_by_name = True


################################################################################
class LineItem3(BaseModel):
    title: Optional[str] = ""
    description: Optional[str] = ""
    amount: Optional[float] = None
    amount_each: Optional[float] = None
    amount_ex_vat: Optional[float] = None
    vat_amount: Optional[float] = None
    vat_percentage: Optional[float] = None
    quantity: Optional[float] = None
    unit_of_measurement: Optional[str] = ""
    sku: Optional[str] = ""
    vat_code: Optional[str] = ""

class Line3(BaseModel):
    description: Optional[str] = ""
    lineitems: List[LineItem3] = Field(default_factory=lambda: [LineItem3()])

class VatItem3(BaseModel):
    amount: Optional[float] = None
    amount_excl_vat: Optional[float] = None
    amount_incl_vat: Optional[float] = None
    amount_incl_excl_vat_estimated: Optional[bool] = None
    percentage: Optional[float] = None
    code: Optional[str] = ""

class InvoiceInfo3(BaseModel):
    amount: Optional[float] = None
    amount_change: Optional[float] = None
    amount_shipping: Optional[float] = None
    vatamount: Optional[float] = None
    amountexvat: Optional[float] = None
    currency: Optional[str] = ""
    date: Optional[datetime] = None
    purchasedate: Optional[datetime] = None
    purchasetime: Optional[time] = None
    vatitems: List[VatItem3] = Field(default_factory=lambda: [VatItem3()])
    vat_context: Optional[str] = ""
    lines: List[Line3] = Field(default_factory=lambda: [Line3()])
    paymentmethod: Optional[str] = ""
    payment_auth_code: Optional[str] = ""
    payment_card_number: Optional[str] = ""
    payment_card_account_number: Optional[str] = ""
    payment_card_bank: Optional[str] = ""
    payment_card_issuer: Optional[str] = ""
    payment_due_date: Optional[datetime] = None
    terminal_number: Optional[str] = ""
    document_subject: Optional[str] = ""
    package_number: Optional[str] = ""
    invoice_number: Optional[str] = ""
    receipt_number: Optional[str] = ""
    shop_number: Optional[str] = ""
    transaction_number: Optional[str] = ""
    transaction_reference: Optional[str] = ""
    order_number: Optional[str] = ""
    table_number: Optional[str] = ""
    table_group: Optional[str] = ""
    server: Optional[str] = ""
    merchant_name: Optional[str] = ""
    merchant_id: Optional[str] = ""
    merchant_coc_number: Optional[str] = ""
    merchant_vat_number: Optional[str] = ""
    merchant_bank_account_number: Optional[str] = ""
    merchant_bank_account_number_bic: Optional[str] = ""
    merchant_chain_liability_bank_account_number: Optional[str] = ""
    merchant_chain_liability_amount: Optional[float] = None
    merchant_bank_domestic_account_number: Optional[str] = ""
    merchant_bank_domestic_bank_code: Optional[str] = ""
    merchant_website: Optional[str] = ""
    merchant_email: Optional[str] = ""
    merchant_address: Optional[str] = ""
    merchant_phone: Optional[str] = ""
    customer_name: Optional[str] = ""
    customer_number: Optional[str] = ""
    customer_reference: Optional[str] = ""
    customer_address: Optional[str] = ""
    customer_phone: Optional[str] = ""
    customer_vat_number: Optional[str] = ""
    customer_coc_number: Optional[str] = ""
    customer_bank_account_number: Optional[str] = ""
    customer_bank_account_number_bic: Optional[str] = ""
    customer_website: Optional[str] = ""
    customer_email: Optional[str] = ""
    document_language: Optional[str] = ""

class Invoice3(BaseModel):
    invoice_info: InvoiceInfo3

#######################################################################

if __name__ == "__main__":

    # Example usage
    json_3 = {
        'invoice_info': {
            'amount': 32.27832,
            'currency': 'EUR',
            'date': date(2008, 6, 28),
            'purchasetime': time(17, 46, 26),
            'purchasedate': date(2008, 6, 28),
            'lines': [
                {
                    'description': 'Items purchased',
                    'lineitems': [
                        {
                            'title': 'Glasses',
                            'amount': 22,
                            'amount_each': 22,
                            'quantity': 1,
                            'unit_of_measurement': 'pcs'
                        },
                        {
                            'title': 'Hat',
                            'amount': 10,
                            'amount_each': 10,
                            'quantity': 1,
                            'unit_of_measurement': 'pcs'
                        }
                    ]
                }
            ],
            'paymentmethod': 'Credit card',
            'receipt_number': '000130',
            'terminal_number': '000148'
        }
    }
    json_1 = {
        "invoice_info": {
            "name": "Tümmler, Dirk",
            "project_number": "V240045",
            "customer": "Magua",
            "city": "Salzgitter",
            "kw": "",
            "land": "DE",
            "lines": [
                {
                    "date": date(2008, 6, 28),
                    "start_time": time(17, 46, 26),
                    "end_time": time(17, 46, 26),
                    "break_time": 0.5,
                    "description": "support",
                    "has_customer_signature": True
                },
                {
                    "date":  date(2008, 6, 28),
                    "start_time": time(17, 46, 26),
                    "end_time": time(17, 46, 26),
                    "break_time": 0.0,
                    "description": "Supports",
                    "has_customer_signature": True
                }
            ],
            "is_process_done": True,
            "is_commissioned_work": True,
            "is_without_measuring_technology": False,
            "sign_date": date(2008, 6, 28),
            "has_employee_signature": True
        }
    }
    json_2 = {
        "invoice_info": {
            "name": "Schmidt, Timo",
            "project_number": "V123023",
            "is_in_egw": True,
            "currency": "EUR",
            "sign_date": date(2008, 6, 28),
            "has_employee_signature": True,
            "fixed_lines": [
                {
                    "title": "Hotel",
                    "with_breakfast": True,
                    "can_book_again": False,
                    "amount": 504.0,
                    "payment_method": "visa"
                },
                {
                    "title": "Fuel",
                    "amount": 40.0,
                    "payment_method": "invoice"
                }
            ],
            "lines": [
                {
                    "title": "Train ticket",
                    "amount": 24.50,
                    "payment_method": "self paid"
                }
            ]
        }
    }


    invoice = Invoice2(invoice_info=json_2['invoice_info'])
    invoice_dict = invoice.model_dump(exclude_unset=False)
    print("\ninvoice 2", invoice_dict)

    
    invoice = Invoice3(invoice_info=json_3['invoice_info'])
    invoice_dict = invoice.model_dump(exclude_unset=False)
    print("\ninvoice 3",invoice_dict)

    invoice = Invoice1(invoice_info=json_1['invoice_info'])
    invoice_dict = invoice.model_dump(exclude_unset=False)
    print("\ninvoice 1",invoice_dict)

    data1 = {
        'invoice_info': {
            'name': 'Tümmler Dirk',
            'project_number': 'V240045',
            'customer': 'Magua',
            'city': 'Salzgitter',
            'land': 'DE',
            'lines': [
                {
                    'date': '07/08/2024',
                    'start_time': '06:45:00',
                    'end_time': '07:30:00',
                    'break_time': '0.0',
                    'description': 'BS-SZ-Support',
                    'has_customer_signature': True
                },
                {
                    'date': '07/08/2024',
                    'start_time': '07:30:00',
                    'end_time': '16:00:00',
                    'break_time': '0.5',
                    'description': '',
                    'has_customer_signature': True
                }
            ],
            'is_process_done': True,
            'is_commissioned_work': True,
            'is_without_measuring_technology': False,
            'sign_date': '13/08/2024',
            'has_employee_signature': True
        }
    }
    data2 = {
        'invoice_info': {
            'name': 'Schmidt, Timo',
            'project_number': 'V123023',
            'is_in_egw': True,
            'currency': 'EUR',
            'lines': [
                {'title': 'Hotel', 'amount': 504.0},
                {'title': 'Fuel', 'amount': 24.6},
                {'title': 'Parking fees', 'amount': 20.0},
                {'title': 'Rental car', 'amount': 156.2},
                {'title': 'Toll', 'amount': 20.0}
            ],
            'has_employee_signature': True
        }
    }

    data = validate_invoice_1(data1)
    print("\ndata1", data)
