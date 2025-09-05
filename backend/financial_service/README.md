# Financial Management Microservice

A comprehensive financial management microservice for the Moroccan Tourist Transport ERP system, built with FastAPI, SQLModel, and PostgreSQL.

## Features

### 💰 Invoice Management
- **Automated Invoice Generation**: Create invoices from confirmed bookings automatically
- **Multi-currency Support**: Handle MAD, EUR, USD with real-time exchange rates
- **Tax Calculations**: Automatic VAT calculation with Morocco tax compliance
- **Payment Tracking**: Link payments to invoices with reconciliation
- **PDF Generation**: Professional invoice PDFs with company branding
- **Status Management**: Draft, Sent, Paid, Overdue, Cancelled, Refunded

### 💳 Payment Processing
- **Multiple Payment Methods**: Cash, cards, bank transfers, mobile payments
- **Payment Reconciliation**: Automatic and manual reconciliation workflows
- **Multi-currency Payments**: Handle payments in different currencies
- **Fee Tracking**: Processing and gateway fees management
- **Partial Payments**: Support for installment and partial payments
- **Audit Trail**: Complete payment history and status tracking

### 📊 Expense Management
- **Comprehensive Expense Tracking**: All business expenses by category and cost center
- **Receipt Management**: Upload and store expense receipts securely
- **Approval Workflows**: Multi-level expense approval process
- **Cost Center Allocation**: Track expenses across departments and projects
- **Tax Deductible Tracking**: Identify and track tax-deductible expenses
- **Recurring Expenses**: Handle monthly, quarterly, and yearly recurring costs

### 📋 Tax Reporting & Compliance
- **VAT Reports**: Automated VAT calculation and reporting for Morocco
- **Tax Declarations**: Generate tax declarations for government submission
- **Compliance Monitoring**: Track tax obligations and filing deadlines
- **Multi-period Reports**: Monthly, quarterly, and yearly tax reports
- **Audit Support**: Complete audit trails for tax compliance
- **Export Capabilities**: PDF and Excel exports for tax authorities

### 📈 Financial Analytics & KPIs
- **Real-time Dashboard**: Live financial metrics and performance indicators
- **Revenue Analytics**: Track revenue trends, sources, and forecasting
- **Expense Analysis**: Cost breakdowns by category, department, and time
- **Cash Flow Management**: Monitor cash inflows and outflows
- **Profitability Analysis**: Gross margins, net profit, and ROI calculations
- **Aging Reports**: Accounts receivable and payable aging analysis

## API Endpoints

### Invoice Management
- `POST /api/v1/invoices/` - Create new invoice
- `POST /api/v1/invoices/generate` - Generate invoice from booking
- `GET /api/v1/invoices/` - List invoices with search and filters
- `GET /api/v1/invoices/summary` - Get invoice summary statistics
- `GET /api/v1/invoices/{id}` - Get invoice details
- `PUT /api/v1/invoices/{id}` - Update invoice information
- `POST /api/v1/invoices/{id}/send` - Send invoice to customer
- `POST /api/v1/invoices/{id}/cancel` - Cancel invoice
- `GET /api/v1/invoices/{id}/pdf` - Download invoice PDF
- `GET /api/v1/invoices/overdue/list` - Get overdue invoices

### Payment Management
- `POST /api/v1/payments/` - Create new payment
- `GET /api/v1/payments/` - List payments with filters
- `GET /api/v1/payments/summary` - Get payment summary statistics
- `GET /api/v1/payments/{id}` - Get payment details
- `PUT /api/v1/payments/{id}` - Update payment information
- `POST /api/v1/payments/{id}/confirm` - Confirm pending payment
- `POST /api/v1/payments/reconcile` - Reconcile multiple payments
- `GET /api/v1/payments/unreconciled/list` - Get unreconciled payments

### Expense Management
- `POST /api/v1/expenses/` - Create new expense
- `POST /api/v1/expenses/upload` - Create expense with receipt upload
- `GET /api/v1/expenses/` - List expenses with filters
- `GET /api/v1/expenses/summary` - Get expense summary statistics
- `GET /api/v1/expenses/{id}` - Get expense details
- `PUT /api/v1/expenses/{id}` - Update expense information
- `POST /api/v1/expenses/{id}/approve` - Approve or reject expense
- `POST /api/v1/expenses/{id}/submit` - Submit expense for approval
- `GET /api/v1/expenses/pending/approval` - Get pending expenses

### Tax Reporting
- `POST /api/v1/tax-reports/` - Create new tax report
- `POST /api/v1/tax-reports/generate` - Generate tax report for period
- `GET /api/v1/tax-reports/` - List tax reports
- `GET /api/v1/tax-reports/summary` - Get tax summary and compliance
- `GET /api/v1/tax-reports/{id}` - Get tax report details
- `PUT /api/v1/tax-reports/{id}` - Update tax report
- `POST /api/v1/tax-reports/{id}/submit` - Submit to authorities
- `GET /api/v1/tax-reports/{id}/pdf` - Download tax report PDF
- `GET /api/v1/tax-reports/vat/declaration` - Get VAT declaration

### Financial Analytics
- `GET /api/v1/analytics/dashboard` - Financial dashboard overview
- `GET /api/v1/analytics/revenue` - Revenue analytics
- `GET /api/v1/analytics/expenses` - Expense analytics
- `GET /api/v1/analytics/cash-flow` - Cash flow analytics
- `GET /api/v1/analytics/profitability` - Profitability analysis
- `GET /api/v1/analytics/kpis` - Key financial performance indicators
- `GET /api/v1/analytics/aging` - Aging reports
- `GET /api/v1/analytics/export/profit-loss` - Export P&L statement
- `GET /api/v1/analytics/export/balance-sheet` - Export balance sheet
- `GET /api/v1/analytics/export/cash-flow` - Export cash flow statement

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd financial_service

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8006/health
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Start PostgreSQL and Redis services
# Update .env with connection strings

# Run application
python -m financial_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5438/financial_db
REDIS_URL=redis://localhost:6385/6
AUTH_SERVICE_URL=http://auth_service:8000
BOOKING_SERVICE_URL=http://booking_app:8002
DEFAULT_CURRENCY=MAD
VAT_RATE=20.0
INVOICE_DUE_DAYS=30
```

## Data Models

### Invoice
- **Identification**: invoice_number, booking_id, customer references
- **Financial**: subtotal, tax_amount, discount_amount, total_amount, currency
- **Status**: status, payment_status, important dates
- **Customer**: cached customer information for performance
- **Items**: detailed line items with tax calculations

### Payment
- **Details**: amount, currency, payment_method, payment_date
- **Processing**: status, fees, exchange rates, reconciliation
- **References**: invoice_id, transaction_id, reference_number
- **Banking**: bank details, card information (masked)

### Expense
- **Classification**: category, cost_center, department
- **Financial**: amount, currency, tax information
- **Approval**: status, approval workflow, rejection reasons
- **Documentation**: receipts, invoices, supporting documents
- **Tracking**: vendor information, project/asset association

### TaxReport
- **Period**: tax_type, period_type, start/end dates
- **Calculations**: revenue, expenses, tax due, VAT breakdown
- **Compliance**: status, submission tracking, government references
- **Documentation**: supporting documents, audit trails

## Security & Integration

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **Data Encryption**: Sensitive financial data encryption
- **Audit Logging**: Complete audit trail for all financial operations
- **Service Integration**: Seamless communication with Booking, CRM, HR services

## Morocco Tax Compliance

- **VAT Handling**: 20% VAT rate with proper calculations
- **Tax Declarations**: Morocco-specific tax report formats
- **Currency Support**: Moroccan Dirham (MAD) as base currency
- **Compliance Monitoring**: Track filing deadlines and obligations
- **Government Integration**: Ready for electronic submission

## Multi-Currency Support

- **Supported Currencies**: MAD (Moroccan Dirham), EUR, USD
- **Exchange Rates**: Real-time rate fetching with caching
- **Conversion**: Automatic currency conversion for reporting
- **Rate History**: Historical exchange rate tracking
- **Base Currency**: All reporting in MAD for consistency

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=financial_service

# Run specific test file
pytest financial_service/tests/test_invoices.py -v
```

## Integration with ERP Ecosystem

The financial microservice integrates seamlessly with other ERP components:

- **Authentication Service**: User authentication and authorization
- **Booking Service**: Automatic invoice generation from bookings
- **CRM Service**: Customer information and billing details
- **HR Service**: Payroll and employee expense integration
- **Fleet Service**: Vehicle maintenance and fuel cost tracking
- **Business Intelligence**: Financial analytics and reporting

## Performance & Scalability

- **Database Optimization**: Indexed queries and efficient pagination
- **Redis Caching**: Exchange rates and session management
- **Async Operations**: Non-blocking I/O for better performance
- **Horizontal Scaling**: Stateless design for easy scaling
- **Connection Pooling**: Efficient database connection management

## Moroccan Market Considerations

- **Multi-language Support**: Arabic, French, English financial documents
- **Local Compliance**: Morocco tax laws and accounting standards
- **Currency Regulations**: Compliance with foreign exchange regulations
- **Banking Integration**: Ready for Moroccan banking system integration
- **Cultural Considerations**: Respect for local business practices

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure proper error handling and validation

## License

Private - Moroccan Tourist Transport ERP System