# 🏥 SmartCare Medical Appointment System

A production-ready FastAPI backend system for managing medical appointments with intelligent priority booking, doctor assignment, and advanced search/filtering capabilities.

## 📋 Project Overview

SmartCare is a comprehensive medical appointment management system built with FastAPI that includes:
- **Real-time doctor management** with availability tracking
- **Smart appointment booking** with priority levels and automatic fee calculations
- **Multi-step appointment workflow** (book → confirm → complete)
- **Advanced analytics** (search, sort, pagination)
- **Business rule enforcement** (no double bookings, active appointment protection)

## 🎯 Key Features

✅ **Smart Doctor Assignment** - Match patients with doctors based on specialization  
✅ **Priority-Based Booking** - Emergency appointments handled first  
✅ **Senior Citizen Discounts** - Automatic 15% discount calculation  
✅ **Fee Flexibility** - Video (80%), In-person (100%), Emergency (150%)  
✅ **Workflow Validation** - Ensures proper appointment status transitions  
✅ **Advanced Search** - Multi-field case-insensitive search  
✅ **Flexible Sorting** - Sort by fee, name, or experience  
✅ **Full Pagination** - Navigate large datasets efficiently  
✅ **Business Rules** - Prevents deleting doctors with active appointments  

## 📁 Project Structure

```
fastapi-medical-system/
├── main.py              # Main FastAPI application (20 endpoints)
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── screenshots/         # API testing screenshots
```

## 🧪 Complete API Endpoints (20 Tasks)

### **DAY 1-2: Basic GET APIs (Q1-Q5)**

| # | Endpoint | Method | Purpose |
|---|----------|--------|---------|
| Q1 | `/` | GET | Welcome message with system info |
| Q2 | `/doctors` | GET | List all doctors with availability stats |
| Q3 | `/doctors/{doctor_id}` | GET | Get single doctor details |
| Q4 | `/appointments` | GET | List all appointments |
| Q5 | `/doctors/summary` | GET | Statistics: total, available, most experienced, cheapest |

### **DAY 3: POST + Pydantic Validation (Q6-Q10)**

| # | Endpoint | Method | Purpose |
|---|----------|--------|---------|
| Q6 | `/appointments` | POST | Create appointment (validates patient_name, doctor_id, date, reason) |
| Q7 | - | - | Helper functions: `find_doctor()`, `calculate_fee()` |
| Q8 | `/appointments` | POST | Uses helper functions, checks doctor availability, calculates fee |
| Q9 | `/appointments` | POST | Senior citizen discount (15% off) with original & discounted fee |
| Q10 | `/doctors/filter` | GET | Filter by specialization, max_fee, min_experience, availability |

### **DAY 4: CRUD Operations (Q11-Q13)**

| # | Endpoint | Method | Purpose |
|---|----------|--------|---------|
| Q11 | `/doctors` | POST | Create doctor (status 201, duplicate name check) |
| Q12 | `/doctors/{doctor_id}` | PUT | Update doctor (only non-None fields) |
| Q13 | `/doctors/{doctor_id}` | DELETE | Delete doctor (prevents if active appointments exist) |

### **DAY 5: Multi-Step Workflows (Q14-Q15)**

| # | Endpoint | Method | Purpose |
|---|----------|--------|---------|
| Q14a | `/appointments/{appointment_id}/confirm` | POST | Change status: scheduled → confirmed |
| Q14b | `/appointments/{appointment_id}/cancel` | POST | Change status → cancelled, mark doctor available |
| Q15a | `/appointments/{appointment_id}/complete` | POST | Change status → completed |
| Q15b | `/appointments/active` | GET | Get appointments with status scheduled/confirmed |
| Q15c | `/appointments/by-doctor/{doctor_id}` | GET | Get all appointments for a specific doctor |

### **DAY 6: Advanced APIs - Search, Sort, Pagination (Q16-Q20)**

| # | Endpoint | Method | Purpose |
|---|----------|--------|---------|
| Q16 | `/doctors/search` | GET | Search doctors by name/specialization (keyword param) |
| Q17 | `/doctors/sort` | GET | Sort by fee/name/experience_years (sort_by, order params) |
| Q18 | `/doctors/page` | GET | Paginate doctors (page, limit params with total_pages) |
| Q19a | `/appointments/search` | GET | Search appointments by patient_name |
| Q19b | `/appointments/sort` | GET | Sort appointments by fee or date |
| Q19c | `/appointments/page` | GET | Paginate appointments |
| Q20 | `/doctors/browse` | GET | **COMBINED**: search → sort → paginate (all params optional) |

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- pip (Python package manager)

### **Installation & Setup**

1. **Create Virtual Environment** (Windows):
```bash
python -m venv venv
venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run Server**:
```bash
uvicorn main:app --reload
```

4. **Open Swagger UI**:
```
http://127.0.0.1:8000/docs
```

## 📊 Sample API Usage

### **Create Doctor**
```bash
curl -X POST "http://127.0.0.1:8000/doctors" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Amit Reddy",
    "specialization": "Cardiologist",
    "fee": 1000,
    "experience_years": 8,
    "is_available": true
  }'
```

### **Book Appointment**
```bash
curl -X POST "http://127.0.0.1:8000/appointments" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Doe",
    "doctor_id": 1,
    "date": "2024-12-25",
    "reason": "Heart checkup",
    "appointment_type": "in-person",
    "senior_citizen": true
  }'
```

### **Search Doctors**
```bash
curl -X GET "http://127.0.0.1:8000/doctors/search?keyword=Cardio"
```

### **Browse with Sort & Pagination**
```bash
curl -X GET "http://127.0.0.1:8000/doctors/browse?keyword=cardio&sort_by=fee&order=asc&page=1&limit=3"
```

## 🏗️ Data Models

### **AppointmentRequest**
```python
{
  "patient_name": "string (min 2 chars)",
  "doctor_id": "integer (>0)",
  "date": "string (min 8 chars)",
  "reason": "string (min 5 chars)",
  "appointment_type": "in-person | video | emergency",
  "senior_citizen": "boolean"
}
```

### **Doctor**
```python
{
  "id": "integer",
  "name": "string",
  "specialization": "string",
  "fee": "integer",
  "experience_years": "integer",
  "is_available": "boolean"
}
```

### **Appointment**
```python
{
  "appointment_id": "integer",
  "patient_name": "string",
  "doctor_id": "integer",
  "doctor_name": "string",
  "date": "string",
  "reason": "string",
  "appointment_type": "string",
  "fee": "integer/float",
  "discount_applied": "float",
  "status": "scheduled | confirmed | completed | cancelled"
}
```

## 🧠 Smart Business Logic

### **Fee Calculation**
- **Video Consultation**: 80% of base fee
- **In-person Consultation**: 100% of base fee
- **Emergency Consultation**: 150% of base fee
- **Senior Citizen Discount**: Additional 15% off after type calculation

### **Appointment Workflow**
```
Patient Registration → Book Appointment → Confirm → Complete
                            ↓
                        (Check availability)
                        (Calculate fee)
```

### **Constraints**
- Cannot book with unavailable doctor
- Cannot delete doctor with active appointments
- Can only complete confirmed appointments
- Cannot confirm cancelled appointments

## 📸 Testing in Swagger UI

1. Navigate to `http://127.0.0.1:8000/docs`
2. Test each endpoint in order (Q1 → Q20)
3. Take screenshots as `Q1_home.png`, `Q2_get_doctors.png`, etc.
4. Save to `screenshots/` folder

## 🎯 Implementation Checklist

- ✅ Q1-Q5: Basic GET endpoints with statistics
- ✅ Q6-Q10: Pydantic models with validations, helper functions, POST endpoints
- ✅ Q11-Q13: CRUD operations with business rule checks
- ✅ Q14-Q15: Multi-step workflows (confirm, cancel, complete)
- ✅ Q16-Q20: Search, sort, pagination, combined browse
- ✅ All routes follow fixed-before-variable ordering
- ✅ Helper functions without @app decorators
- ✅ Proper status codes (201 for creation, 404 for not found)
- ✅ Error handling and validation

## 🔧 Technologies Used

- **FastAPI** 0.104.1 - Modern web framework for building APIs
- **Uvicorn** 0.24.0 - ASGI server for running FastAPI
- **Pydantic** 2.5.0 - Data validation using Python type hints
- **Python 3.8+** - Programming language

## 📝 Notes

- All data is in-memory (resets on server restart)
- IDs are auto-incremented
- Status codes follow REST standards
- Comprehensive error messages with HTTP status codes
- Fully compatible with OpenAPI/Swagger UI

## 👨‍💼 About This Project

Built as a FastAPI internship final project demonstrating:
- RESTful API design principles
- Pydantic data validation
- CRUD operations
- Complex workflow implementation
- Search, sort, and pagination
- Business logic and constraints
- Production-ready code structure

---

**Created by**: Thrupthi  
**Framework**: FastAPI  
**Status**: Ready for Testing & Submission  
**Internship**: Innomatics Research Labs
