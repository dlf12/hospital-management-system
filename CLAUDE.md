# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hospital Medical Records Management System - A full-stack web application for managing patient records across different hospital departments. Built with Flask (backend) and Vue 3 (frontend).

## Common Commands

### Backend (Flask + MySQL)

```bash
# Navigate to backend directory
cd backend

# Start the backend server (runs on http://127.0.0.1:5000)
python app.py

# Database migrations
python -m flask db upgrade    # Apply migrations
python -m flask db migrate -m "description"  # Create new migration

# Install dependencies
pip install flask flask-sqlalchemy flask-cors flask-migrate flask-jwt-extended pymysql
```

### Frontend (Vue 3 + Vite)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server (runs on http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Manual Database Migration (if flask db upgrade fails)

```sql
USE hospital_db;

ALTER TABLE medical_records
ADD COLUMN medical_history TEXT NULL AFTER treatment_plan,
ADD COLUMN allergy_history TEXT NULL AFTER medical_history;
```

## Architecture

### Backend Structure (Flask)

- **Main file**: `backend/app.py` - Contains all models, routes, and configurations
- **Database**: MySQL (default connection: `mysql+pymysql://root:123456@127.0.0.1/hospital_db`)
- **Authentication**: JWT-based with Flask-JWT-Extended
- **Migrations**: Flask-Migrate manages database schema changes in `backend/migrations/`

**Data Models**:
- `User` (users table) - System users with hashed passwords
- `Patient` (patients table) - Patient records with department assignment
- `MedicalRecord` (medical_records table) - Medical records linked to patients
- `Template` (templates table) - Reusable medical record templates

**Key Backend Patterns**:
- All protected routes use `@jwt_required()` decorator
- Patient queries support pagination, search (name/ID card/phone), and department filtering
- Templates can be shared between users (`is_shared` flag) or private to owner
- Medical records support both creation from scratch and from templates

### Frontend Structure (Vue 3)

**Entry point**: `frontend/src/main.js` → `frontend/src/App.vue`

**Key Components**:
- `Login.vue` - Handles user authentication (login/register)
- `DepartmentView.vue` - Main department view with patient table and medical record management
  - Table layout with search, add, edit, delete functionality
  - Modal for medical record editing with history on left, form on right
  - Supports template import/export for medical records
- `TemplateManager.vue` - Template CRUD interface (create, edit, delete, share templates)
- `PatientManager.vue` - Legacy component (not currently used)

**API Layer**: `frontend/src/api/apiClient.js`
- Axios instance with base URL `http://127.0.0.1:5000/api`
- Request interceptor automatically adds JWT token from localStorage to Authorization header

**Routing & State**:
- App.vue manages view state: `departments`, `department`, `templates`
- No Vue Router - uses conditional rendering based on view state
- JWT token stored in localStorage as `accessToken`

### Department System

The system supports 4 departments (科室):
- 内科 (Internal Medicine)
- 外科 (Surgery)
- 妇产科 (Obstetrics & Gynecology)
- 儿科 (Pediatrics)

Patients are assigned to departments and can only be viewed/edited within their department context.

## API Endpoints

### Authentication (No Auth Required)
- `POST /api/register` - Register new user
- `POST /api/login` - Login and get JWT token

### Patients (JWT Required)
- `GET /api/patients?search=&department=&page=&per_page=` - List patients with filters
- `POST /api/patients` - Create new patient
- `PUT /api/patients/<patient_id>` - Update patient info
- `DELETE /api/patients/<patient_id>` - Delete patient (cascades to records)

### Medical Records (JWT Required)
- `GET /api/patients/<patient_id>/records` - Get all records for a patient
- `POST /api/patients/<patient_id>/records` - Create new record
- `PUT /api/patients/<patient_id>/records/<record_id>` - Update existing record (added in recent update)

### Templates (JWT Required)
- `GET /api/templates` - Get all templates (user's own + shared)
- `POST /api/templates` - Create new template
- `GET /api/templates/<tpl_id>` - Get template details
- `PUT /api/templates/<tpl_id>` - Update template
- `DELETE /api/templates/<tpl_id>` - Delete template
- `POST /api/patients/<patient_id>/records/<record_id>/save_as_template` - Export record as template
- `POST /api/patients/<patient_id>/records/from_template/<tpl_id>` - Create record from template

### Statistics (JWT Required)
- `GET /api/departments/stats` - Get department statistics

## Recent Updates (2025-10-20)

1. **Database Schema**: Added `medical_history` and `allergy_history` TEXT fields to `medical_records` table
2. **DepartmentView Refactor**: Complete UI overhaul to table-based layout with modal for record editing
3. **Record Editing**: Left panel shows history, right panel shows form (diagnosis, treatment plan, medical history, allergy history)
4. **Template Enhancement**: Templates now support the new medical_history and allergy_history fields
5. **Styling**: Unified input styles - white backgrounds (#ffffff), dark text (#2d3748), consistent borders

## Development Notes

### Medical Record Fields
- **Required**: `diagnosis`, `treatment_plan`
- **Optional**: `medical_history`, `allergy_history`
- Old records are compatible (optional fields default to NULL)

### Template Content Format
Templates store content as JSON string:
```json
{
  "diagnosis": "...",
  "treatment_plan": "...",
  "medical_history": "...",
  "allergy_history": "..."
}
```

### Authentication Flow
1. User logs in via Login.vue
2. Backend returns JWT token
3. Frontend stores token in localStorage
4. apiClient automatically includes token in all subsequent requests
5. Backend validates token via @jwt_required() decorator

### Component Communication
- App.vue manages global state (login status, current view, selected department)
- Components use props for data down (e.g., department prop to DepartmentView)
- Components emit events up (e.g., @login-success from Login)
- No Vuex/Pinia - simple ref-based state management

## Configuration

### Backend Configuration (app.py)
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1/hospital_db'
JWT_SECRET_KEY = "1943860229"
```

### Frontend Configuration (apiClient.js)
```javascript
baseURL: 'http://127.0.0.1:5000/api'
```

## Database Initialization

First time setup requires:
1. Create MySQL database named `hospital_db`
2. Run `python -m flask db upgrade` to create tables
3. Register at least one user through the frontend

## Testing Workflow

When testing features:
1. Start backend: `cd backend && python app.py`
2. Start frontend: `cd frontend && npm run dev`
3. Login with test credentials or register new user
4. Select a department to test patient/record management
5. Use template manager to test template functionality
- 在我的这个项目中，启动前端是切换到frontend目录下后运行npx vite, 不要使用npm run dev