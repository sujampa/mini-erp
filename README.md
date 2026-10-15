# Mini ERP — Full-Stack Enterprise Resource Planning System

Mini ERP is a full-stack business management application designed to manage products, inventory, suppliers, sales orders, and purchase orders through a centralized platform. It combines a FastAPI backend, PostgreSQL database, React frontend, and an AI Assistant powered by Ollama and Llama 3.2.

## Project Overview

The goal of this project is to simplify core business operations by bringing inventory management, purchasing, sales, and AI-assisted information retrieval into one application.

The AI Assistant combines deterministic Python tools with a local language model to answer supported business questions using ERP inventory data.

## Key Features

- Product management and inventory tracking
- Inventory adjustments and inventory history
- Supplier management
- Purchase order creation and receiving
- Sales order creation and stock validation
- Dashboard API for business information
- User registration and login APIs
- JWT-based authentication mechanisms
- AI Assistant for supported inventory queries
- Local language model integration using Ollama and Llama 3.2
- Basic guardrails against destructive AI requests
- Automated backend tests using pytest

## Technology Stack

### Backend
- Python
- FastAPI
- SQLModel
- Pydantic
- PostgreSQL
- JWT authentication

### Frontend
- React
- Vite
- JavaScript
- Axios
- CSS

### AI
- Ollama
- Llama 3.2
- Python-based inventory tools
- Rule-based request routing and guardrails

### Testing and Development
- Pytest
- Git
- GitHub

## Architecture

    User
      |
      v
    React Frontend
      |
      | HTTP Requests
      v
    FastAPI Backend
      |
      +---- Product Management
      |
      +---- Inventory Management
      |
      +---- Supplier Management
      |
      +---- Sales Orders
      |
      +---- Purchase Orders
      |
      +---- AI Assistant
                |
                +---- Python Inventory Tools
                |
                +---- Ollama / Llama 3.2
      |
      v
    PostgreSQL Database

## Project Structure

    mini_erp/
    |
    +-- backend/
    |   +-- app/
    |   |   +-- api/
    |   |   +-- auth/
    |   |   +-- core/
    |   |   +-- models/
    |   |   +-- schemas/
    |   |   +-- services/
    |   +-- tests/
    |
    +-- frontend/
    |   +-- public/
    |   +-- src/
    |   |   +-- assets/
    |   |   +-- services/
    |   |   +-- AIAssistantPage.jsx
    |   |   +-- PurchaseOrdersPage.jsx
    |   |   +-- SalesOrdersPage.jsx
    |   |   +-- App.jsx
    |   +-- package.json
    |   +-- README.md
    |
    +-- database/
    +-- documents/
    +-- scripts/
    +-- tests/
    +-- README.md

## Prerequisites

- Python 3.13 or a compatible Python version
- PostgreSQL
- Node.js and npm
- Ollama, if using the local AI Assistant
- Git

## Backend Setup

Open a terminal in the project root.

Navigate to the backend:

    cd backend

Create a virtual environment if one does not already exist:

    python -m venv .venv

Activate it in Windows PowerShell:

    .\.venv\Scripts\Activate.ps1

Install the backend dependencies using the project's dependency file.

Configure the required environment variables in the backend `.env` file. These include the database connection settings and JWT signing key.

Ensure PostgreSQL is running and the configured database exists.

Start the backend:

    python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

Backend API:

    http://127.0.0.1:8001/

Interactive API documentation:

    http://127.0.0.1:8001/docs

## Frontend Setup

Open another terminal:

    cd frontend

Install dependencies:

    npm install

Start the development server:

    npm run dev

Open the local URL displayed by Vite. The default address is:

    http://localhost:5173/

Ensure the backend is running before testing frontend features that require API access.

## AI Assistant Setup

The AI Assistant connects to the Mini ERP backend.

The configured local model is:

    llama3.2

The backend communicates with Ollama through its local API. Ollama must be running and the model must be available for language-model requests.

The AI Assistant also uses Python-based inventory tools for supported queries.

The current guardrails provide basic protection against destructive requests. They are not a replacement for comprehensive authorization, security controls, or human approval for sensitive operations.

## Testing

The backend has an automated test suite using pytest.

To run the tests, activate the backend virtual environment and execute:

    python -m pytest tests -v

Use the appropriate test database configuration and environment variables before running the suite.

## Current Development Status

The backend business modules, authentication mechanisms, React frontend, and AI Assistant have been developed.

The backend test suite has previously completed with 46 passing tests and one warning.

Further work includes comprehensive end-to-end testing, consistent authentication enforcement across protected APIs, stronger authorization controls, and additional concurrency and AI security testing.

## Security Notes

- Never commit `.env` files, database credentials, or JWT signing secrets.
- Keep development and test databases separate.
- Do not expose local development services publicly without appropriate security controls.
- AI-generated responses should be validated before being used for sensitive business decisions.

## Future Improvements

- Complete frontend authentication and authorization flows
- Strengthen API access controls
- Improve transaction safety for concurrent inventory operations
- Expand AI guardrail and adversarial tests
- Improve dashboard performance for larger datasets
- Add deployment configuration and production monitoring

## Author

Developed as a full-stack ERP and AI integration project.

## License

Add a license before distributing this project for reuse.
