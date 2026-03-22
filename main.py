from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import math

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================
app = FastAPI(
    title="SmartCare Medical API",
    description="Smart Medical Appointment System with Priority Booking",
    version="1.0.0"
)

# ============================================================================
# DATA MODELS (Pydantic)
# ============================================================================

class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = Field(default="in-person")
    senior_citizen: bool = Field(default=False)


class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = Field(default=True)


# ============================================================================
# DATABASE (In-memory lists)
# ============================================================================

doctors = [
    {"id": 1, "name": "Dr. Ravi Kumar", "specialization": "Cardiologist", "fee": 800, "experience_years": 12, "is_available": True},
    {"id": 2, "name": "Dr. Anjali Mehta", "specialization": "Dermatologist", "fee": 500, "experience_years": 8, "is_available": True},
    {"id": 3, "name": "Dr. Suresh Reddy", "specialization": "Pediatrician", "fee": 600, "experience_years": 10, "is_available": False},
    {"id": 4, "name": "Dr. Priya Sharma", "specialization": "General", "fee": 300, "experience_years": 5, "is_available": True},
    {"id": 5, "name": "Dr. Vikram Singh", "specialization": "Cardiologist", "fee": 900, "experience_years": 15, "is_available": True},
    {"id": 6, "name": "Dr. Neha Gupta", "specialization": "General", "fee": 350, "experience_years": 6, "is_available": True}
]

appointments = []
appt_counter = 1
doctor_counter = 7

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_doctor(doctor_id: int):
    """Helper: Find doctor by ID"""
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    return None


def find_appointment(appointment_id: int):
    """Helper: Find appointment by ID"""
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            return appt
    return None


def calculate_fee(base_fee: int, appointment_type: str, senior_citizen: bool = False):
    """Helper: Calculate consultation fee based on type and senior citizen discount"""
    if appointment_type == "video":
        fee = base_fee * 0.8
    elif appointment_type == "emergency":
        fee = base_fee * 1.5
    else:  # in-person
        fee = base_fee
    
    # Apply senior citizen discount (15% extra discount after type calculation)
    if senior_citizen:
        discount = fee * 0.15
        fee = fee - discount
    
    return fee


def filter_doctors_logic(specialization: Optional[str] = None, max_fee: Optional[int] = None, 
                        min_experience: Optional[int] = None, is_available: Optional[bool] = None):
    """Helper: Filter doctors based on criteria"""
    result = doctors.copy()
    
    if specialization is not None:
        result = [d for d in result if d["specialization"].lower() == specialization.lower()]
    
    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]
    
    if min_experience is not None:
        result = [d for d in result if d["experience_years"] >= min_experience]
    
    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]
    
    return result


# ============================================================================
# Q1-Q2: BASIC GET ENDPOINTS
# ============================================================================

@app.get("/")
def home():
    """Q1: Home route"""
    return {
        "message": "Welcome to MediCare Clinic",
        "system": "Smart Medical Appointment System",
        "features": ["Smart Booking", "Priority System", "Doctor Matching"]
    }


@app.get("/doctors")
def get_doctors():
    """Q2: Get all doctors with stats"""
    available = [d for d in doctors if d["is_available"]]
    return {
        "total": len(doctors),
        "available_count": len(available),
        "doctors": doctors
    }


# ============================================================================
# Q5: SUMMARY (Must come BEFORE /{id} route)
# ============================================================================

@app.get("/doctors/summary")
def doctors_summary():
    """Q5: Get doctors summary with statistics"""
    available = [d for d in doctors if d["is_available"]]
    most_exp = max(doctors, key=lambda x: x["experience_years"])
    cheapest = min(doctors, key=lambda x: x["fee"])
    
    spec_count = {}
    for d in doctors:
        spec = d["specialization"]
        spec_count[spec] = spec_count.get(spec, 0) + 1
    
    return {
        "total_doctors": len(doctors),
        "available_doctors": len(available),
        "most_experienced": most_exp["name"],
        "most_experienced_years": most_exp["experience_years"],
        "cheapest_consultation_fee": cheapest["fee"],
        "specialization_count": spec_count
    }


# ============================================================================
# Q16: SEARCH (Fixed routes before variable routes)
# ============================================================================

@app.get("/doctors/search")
def search_doctors(keyword: str = Query(...)):
    """Q16: Search doctors by name and specialization (case-insensitive)"""
    keyword_lower = keyword.lower()
    results = [d for d in doctors if keyword_lower in d["name"].lower() or keyword_lower in d["specialization"].lower()]
    
    if not results:
        return {
            "keyword": keyword,
            "total_found": 0,
            "message": f"No doctors found matching '{keyword}'",
            "doctors": []
        }
    
    return {
        "keyword": keyword,
        "total_found": len(results),
        "doctors": results
    }


# ============================================================================
# Q17: SORTING
# ============================================================================

@app.get("/doctors/sort")
def sort_doctors(sort_by: str = Query("fee"), order: str = Query("asc")):
    """Q17: Sort doctors by fee, name, or experience"""
    # Validate sort_by
    valid_sort_fields = ["fee", "name", "experience_years"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_sort_fields}")
    
    # Validate order
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
    
    reverse = (order == "desc")
    sorted_doctors = sorted(doctors, key=lambda x: x[sort_by], reverse=reverse)
    
    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_doctors),
        "doctors": sorted_doctors
    }


# ============================================================================
# Q18: PAGINATION - DOCTORS
# ============================================================================

@app.get("/doctors/page")
def paginate_doctors(page: int = Query(1, gt=0), limit: int = Query(3, gt=0)):
    """Q18: Paginate doctors"""
    total_pages = math.ceil(len(doctors) / limit)
    
    if page > total_pages and len(doctors) > 0:
        raise HTTPException(status_code=400, detail=f"Page {page} exceeds total pages ({total_pages})")
    
    start = (page - 1) * limit
    end = start + limit
    paginated = doctors[start:end]
    
    return {
        "page": page,
        "limit": limit,
        "total_items": len(doctors),
        "total_pages": total_pages,
        "doctors": paginated
    }


# ============================================================================
# Q3: GET DOCTOR BY ID (Variable route - after fixed routes)
# ============================================================================

@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    """Q3: Get doctor by ID"""
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor with ID {doctor_id} not found")
    return doctor


# ============================================================================
# Q6-Q10: PYDANTIC + POST APPOINTMENTS
# ============================================================================

@app.get("/appointments")
def get_appointments():
    """Q4: Get all appointments"""
    return {
        "total": len(appointments),
        "appointments": appointments
    }


@app.post("/appointments", status_code=201)
def create_appointment(data: AppointmentRequest):
    """Q8: Create appointment with smart logic"""
    global appt_counter
    
    # Find doctor
    doctor = find_doctor(data.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor with ID {data.doctor_id} not found")
    
    # Check availability
    if not doctor["is_available"]:
        raise HTTPException(status_code=400, detail="Doctor is not available")
    
    # Calculate fee (Q9: with senior citizen discount)
    original_fee = calculate_fee(doctor["fee"], data.appointment_type, False)
    fee = calculate_fee(doctor["fee"], data.appointment_type, data.senior_citizen)
    discount_applied = original_fee - fee if data.senior_citizen else 0
    
    appointment = {
        "appointment_id": appt_counter,
        "patient_name": data.patient_name,
        "doctor_id": doctor["id"],
        "doctor_name": doctor["name"],
        "specialization": doctor["specialization"],
        "date": data.date,
        "reason": data.reason,
        "appointment_type": data.appointment_type,
        "is_senior_citizen": data.senior_citizen,
        "original_fee": original_fee,
        "fee": fee,
        "discount_applied": discount_applied,
        "status": "scheduled"
    }
    
    appointments.append(appointment)
    appt_counter += 1
    
    return {
        "message": "Appointment booked successfully",
        "appointment": appointment
    }


# ============================================================================
# Q10: FILTER DOCTORS
# ============================================================================

@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = Query(None),
    max_fee: Optional[int] = Query(None, gt=0),
    min_experience: Optional[int] = Query(None, ge=0),
    is_available: Optional[bool] = Query(None)
):
    """Q10: Filter doctors with optional parameters"""
    filtered = filter_doctors_logic(specialization, max_fee, min_experience, is_available)
    
    return {
        "filters": {
            "specialization": specialization,
            "max_fee": max_fee,
            "min_experience": min_experience,
            "is_available": is_available
        },
        "total_found": len(filtered),
        "doctors": filtered
    }


# ============================================================================
# Q11-Q13: CRUD OPERATIONS - DOCTORS
# ============================================================================

@app.post("/doctors", status_code=201)
def create_doctor(data: NewDoctor):
    """Q11: Create new doctor (with duplicate name check)"""
    global doctor_counter
    
    # Check for duplicate name
    for doc in doctors:
        if doc["name"].lower() == data.name.lower():
            raise HTTPException(status_code=400, detail=f"Doctor with name '{data.name}' already exists")
    
    new_doctor = {
        "id": doctor_counter,
        "name": data.name,
        "specialization": data.specialization,
        "fee": data.fee,
        "experience_years": data.experience_years,
        "is_available": data.is_available
    }
    
    doctors.append(new_doctor)
    doctor_counter += 1
    
    return {
        "message": "Doctor added successfully",
        "doctor": new_doctor
    }


@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: Optional[int] = Query(None), is_available: Optional[bool] = Query(None)):
    """Q12: Update doctor (only non-None fields)"""
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor with ID {doctor_id} not found")
    
    changes_made = False
    if fee is not None:
        doctor["fee"] = fee
        changes_made = True
    
    if is_available is not None:
        doctor["is_available"] = is_available
        changes_made = True
    
    if not changes_made:
        return {"message": "No updates provided", "doctor": doctor}
    
    return {
        "message": "Doctor updated successfully",
        "doctor": doctor
    }


@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    """Q13: Delete doctor (with business rule check)"""
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor with ID {doctor_id} not found")
    
    # Business rule: Can't delete if has scheduled appointments
    has_active = any(appt["doctor_id"] == doctor_id and appt["status"] == "scheduled" for appt in appointments)
    
    if has_active:
        raise HTTPException(status_code=400, detail="Cannot delete doctor with active appointments")
    
    doctors.remove(doctor)
    return {"message": f"Doctor {doctor['name']} deleted successfully"}


# ============================================================================
# Q14-Q15: MULTI-STEP WORKFLOW
# ============================================================================

@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    """Q14: Confirm appointment (change status to confirmed)"""
    appt = find_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    
    if appt["status"] != "scheduled":
        raise HTTPException(status_code=400, detail=f"Can only confirm 'scheduled' appointments, current status: {appt['status']}")
    
    appt["status"] = "confirmed"
    return {"message": "Appointment confirmed", "appointment": appt}


@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    """Q14: Cancel appointment (change status to cancelled, mark doctor available)"""
    appt = find_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    
    if appt["status"] == "cancelled":
        raise HTTPException(status_code=400, detail="Appointment is already cancelled")
    
    appt["status"] = "cancelled"
    
    # Mark doctor as available
    doctor = find_doctor(appt["doctor_id"])
    if doctor:
        doctor["is_available"] = True
    
    return {"message": "Appointment cancelled", "appointment": appt}


@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    """Q15: Complete appointment (change status to completed)"""
    appt = find_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    
    if appt["status"] not in ["confirmed", "scheduled"]:
        raise HTTPException(status_code=400, detail=f"Can only complete 'confirmed' or 'scheduled' appointments")
    
    appt["status"] = "completed"
    return {"message": "Appointment completed", "appointment": appt}


@app.get("/appointments/active")
def get_active_appointments():
    """Q15: Get active appointments (scheduled or confirmed)"""
    active = [a for a in appointments if a["status"] in ["scheduled", "confirmed"]]
    return {
        "total_active": len(active),
        "appointments": active
    }


@app.get("/appointments/by-doctor/{doctor_id}")
def get_appointments_by_doctor(doctor_id: int):
    """Q15: Get appointments for a specific doctor"""
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor with ID {doctor_id} not found")
    
    doctor_appts = [a for a in appointments if a["doctor_id"] == doctor_id]
    return {
        "doctor_name": doctor["name"],
        "doctor_id": doctor_id,
        "total_appointments": len(doctor_appts),
        "appointments": doctor_appts
    }


# ============================================================================
# Q19: SEARCH & SORT APPOINTMENTS
# ============================================================================

@app.get("/appointments/search")
def search_appointments(patient_name: str = Query(...)):
    """Q19: Search appointments by patient name (case-insensitive)"""
    keyword_lower = patient_name.lower()
    results = [a for a in appointments if keyword_lower in a["patient_name"].lower()]
    
    return {
        "search_keyword": patient_name,
        "total_found": len(results),
        "appointments": results
    }


@app.get("/appointments/sort")
def sort_appointments(sort_by: str = Query("fee"), order: str = Query("asc")):
    """Q19: Sort appointments by fee or date"""
    valid_sort_fields = ["fee", "date"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_sort_fields}")
    
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
    
    reverse = (order == "desc")
    sorted_appts = sorted(appointments, key=lambda x: x[sort_by], reverse=reverse)
    
    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_appts),
        "appointments": sorted_appts
    }


# ============================================================================
# Q19: PAGINATION - APPOINTMENTS
# ============================================================================

@app.get("/appointments/page")
def paginate_appointments(page: int = Query(1, gt=0), limit: int = Query(5, gt=0)):
    """Q19: Paginate appointments"""
    total_pages = math.ceil(len(appointments) / limit) if appointments else 0
    
    if page > total_pages and len(appointments) > 0:
        raise HTTPException(status_code=400, detail=f"Page {page} exceeds total pages ({total_pages})")
    
    start = (page - 1) * limit
    end = start + limit
    paginated = appointments[start:end]
    
    return {
        "page": page,
        "limit": limit,
        "total_items": len(appointments),
        "total_pages": total_pages,
        "appointments": paginated
    }


# ============================================================================
# Q20: COMBINED BROWSE ENDPOINT (Search + Sort + Pagination)
# ============================================================================

@app.get("/doctors/browse")
def browse_doctors(
    keyword: Optional[str] = Query(None),
    sort_by: str = Query("fee"),
    order: str = Query("asc"),
    page: int = Query(1, gt=0),
    limit: int = Query(4, gt=0)
):
    """Q20: Combined browse - search, sort, and paginate doctors"""
    
    # Step 1: Filter (search)
    result = doctors.copy()
    if keyword:
        keyword_lower = keyword.lower()
        result = [d for d in result if keyword_lower in d["name"].lower() or keyword_lower in d["specialization"].lower()]
    
    # Step 2: Sort
    valid_sort_fields = ["fee", "name", "experience_years"]
    if sort_by not in valid_sort_fields:
        sort_by = "fee"
    
    if order not in ["asc", "desc"]:
        order = "asc"
    
    reverse = (order == "desc")
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)
    
    # Step 3: Paginate
    total_items = len(result)
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    
    if page > total_pages and total_items > 0:
        page = total_pages
    
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]
    
    return {
        "search": {
            "keyword": keyword,
            "matches": sum(1 for d in result) if keyword else len(result)
        },
        "sort": {
            "sort_by": sort_by,
            "order": order
        },
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages
        },
        "results": paginated
    }
