from datetime import datetime, date

def calculate_age(date_of_birth) -> int:
    """Calculate age dynamically from Date of Birth"""
    if not date_of_birth:
        return 30
        
    try:
        today = datetime.utcnow().date()
        if isinstance(date_of_birth, str):
            # Parse ISO date string
            dob_date = datetime.strptime(date_of_birth.split("T")[0], "%Y-%m-%d").date()
        elif isinstance(date_of_birth, datetime):
            dob_date = date_of_birth.date()
        elif isinstance(date_of_birth, date):
            dob_date = date_of_birth
        else:
            return 30
            
        return today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    except Exception:
        return 30
