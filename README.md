# Warehouse Management System 2.0 (WMS 2.0)

A comprehensive warehouse management solution featuring an intelligent AI assistant, role-based access control, real-time inventory tracking, and streamlined receiving, shipping, and reconciliation operations.

## 📋 Features

- **AI-Powered Assistant**: GenAI chatbot integration for intelligent warehouse operations support
- **Role-Based Access Control (RBAC)**: Fine-grained permission management with multiple user roles
- **Barcode Scanning**: Fast and efficient item tracking via barcode input
- **Inventory Management**: Real-time inventory tracking and reconciliation
- **Receiving & Shipping**: Streamlined workflows for receiving shipments and fulfilling orders
- **Audit Logging**: Comprehensive audit trail for compliance and operations monitoring
- **Dashboard**: Real-time operational metrics and insights
- **Responsive UI**: Modern React-based frontend with TypeScript for type safety

## 🏗️ Project Structure

```
wms2.0/
├── backend/                          # Python FastAPI backend
│   ├── main.py                      # Application entry point
│   ├── requirements.txt             # Python dependencies
│   ├── seed.py                      # Database seeding script
│   ├── commons/                     # Shared utilities
│   │   ├── auth.py                 # Authentication logic
│   │   ├── logger.py               # Logging configuration
│   │   └── rbac.py                 # Role-based access control
│   ├── core/                        # Core application logic
│   │   ├── apis/                   # API endpoints
│   │   │   ├── routes/             # API route definitions
│   │   │   │   ├── assistant_routes.py
│   │   │   │   ├── auth_routes.py
│   │   │   │   ├── inventory_routes.py
│   │   │   │   ├── receiving_routes.py
│   │   │   │   ├── shipping_routes.py
│   │   │   │   ├── audit_routes.py
│   │   │   │   └── migration_routes.py
│   │   │   └── schemas/            # Request/response schemas
│   │   ├── audit/                  # Audit logging
│   │   ├── controllers/            # Business logic controllers
│   │   ├── cruds/                  # Database CRUD operations
│   │   ├── database/               # Database configuration
│   │   ├── models/                 # SQLAlchemy models
│   │   └── services/               # Business services
│   │       └── genai_chatbot/      # AI assistant service
│   ├── logs/                        # Application logs
│   └── tests/                       # Backend tests
│       ├── conftest.py
│       ├── test_core_operations.py
│       └── test_rbac_*.py
│
├── frontend/                        # React TypeScript frontend
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── public/                      # Static assets
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── api/                     # API client
│       ├── components/              # React components
│       │   ├── app/                 # App-specific components
│       │   ├── marketing/           # Marketing components
│       │   └── shared/              # Shared UI components
│       ├── context/                 # React context (state management)
│       ├── hooks/                   # Custom React hooks
│       ├── layouts/                 # Page layouts
│       ├── pages/                   # Page components
│       ├── styles/                  # CSS stylesheets
│       └── types/                   # TypeScript type definitions
│
└── README.md                        # This file
```

## 🚀 Getting Started

### Prerequisites

**Backend:**
- Python 3.8 or higher
- pip (Python package manager)

**Frontend:**
- Node.js 16 or higher
- npm or yarn package manager

### Installation

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the backend directory with required configurations:
```env
DATABASE_URL=sqlite:///./warehouse.db
SECRET_KEY=your-secret-key-here
```

4. Initialize the database:
```bash
python seed.py
```

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment configuration (if needed):
Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
```

## 🏃 Running the Application

### Start Backend Server

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`
API documentation (Swagger UI) will be at `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend application will be available at `http://localhost:3000`
Login screen: `http://localhost:3000/login`

## 🧪 Testing

### Backend Tests

Run all tests:
```bash
cd backend
pytest
```

Run specific test file:
```bash
pytest tests/test_rbac_manager.py
```

Run with coverage:
```bash
pytest --cov=core tests/
```

## 📝 API Routes

### Authentication
- `POST /v1/auth/login` - User login with username or email
- `GET /v1/auth/me` - Fetch the current authenticated user
- `GET /v1/auth/users` - List accessible user accounts
- `POST /v1/auth/users` - Create a new user account
- `PATCH /v1/auth/users/{user_id}/status` - Update user status
- `PATCH /v1/auth/users/{user_id}/password` - Reset user password

### Inventory
- `GET /inventory` - List inventory items
- `GET /inventory/{item_id}` - Get item details
- `PUT /inventory/{item_id}` - Update inventory item

### Receiving
- `POST /receiving/shipment` - Create receiving shipment
- `GET /receiving/shipment/{shipment_id}` - Get shipment details
- `PUT /receiving/shipment/{shipment_id}` - Update shipment status

### Shipping
- `POST /shipping/order` - Create shipping order
- `GET /shipping/order/{order_id}` - Get order details
- `PUT /shipping/order/{order_id}` - Update order status

### Assistant
- `POST /assistant/chat` - Chat with AI assistant
- `GET /assistant/history` - Get chat history

### Audit
- `GET /audit/logs` - View audit logs
- `GET /audit/logs/{entity_id}` - Get entity audit trail

## 🔐 Authentication & Authorization

The system uses JWT-based authentication with role-based access control (RBAC):

**Roles:**
- **Owner**: Full system access
- **Manager**: Manage inventory, users, and operations
- **Staff**: Perform warehouse operations (receiving, shipping)
- **NewHire**: Limited read-only access

Role permissions are enforced at the API route level via the `@require_permission` decorator.

## 🔄 Key Components

### Backend Services

- **Authentication Service**: Handles user authentication and JWT token management
- **RBAC Manager**: Manages roles, permissions, and access control
- **Inventory Service**: Manages warehouse inventory
- **GenAI Assistant Service**: Provides AI-powered chatbot functionality
- **Audit Logger**: Tracks all system operations for compliance

### Frontend Features

- **AuthContext**: Global authentication state management
- **RequireRole Component**: Route/component-level authorization
- **usePermissions Hook**: Permission checking in components
- **API Client**: Centralized HTTP client for backend communication
- **Toast Notifications**: User feedback system

## 📚 Additional Resources

- **Backend Standards**: See `backend/` folder for code organization patterns
- **Frontend Standards**: See `frontend/src/` folder for component structure
- **Agent Configuration**: See `AGENT.md` for development guidelines

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes following project conventions
3. Write tests for new functionality
4. Ensure all tests pass before submitting
5. Create a pull request with detailed description

## 📄 License

[Add appropriate license information here]

## 👥 Support

For questions or issues, please [add contact information or issue tracker link]
```

Keep skill instructions concise. Put detailed repeatable guidance in `SKILL.md` and only add reference files when the extra context should be loaded on demand.

## Test Credentials

The application is seeded with a 7-account roster for testing different roles and facility scopes. The password for all accounts is `password123`.

The owner demo account is also accepted using the Dan Whitfield email alias:
- Email: `dan.whitfield@whitfieldfulfillment.com`
- Username: `dan_owner` or `owner`
- Password: `password123`

| Username / Email | Password | Role | Facility Scope |
| --- | --- | --- | --- |
| `owner` / `dan.whitfield@whitfieldfulfillment.com` | `password123` | Owner | *None (All)* |
| `manager.reno` | `password123` | Manager | Reno |
| `manager.columbus` | `password123` | Manager | Columbus |
| `staff.reno` | `password123` | Trusted Staff | Reno |
| `staff.columbus` | `password123` | Trusted Staff | Columbus |
| `newhire.reno` | `password123` | New Hire | Reno |
| `newhire.columbus` | `password123` | New Hire | Columbus |
