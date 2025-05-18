from data.doctors import doctors_data  # Make sure this file exists and is accessible

def get_doctor_list(location, language, session):
    # Always show the list, no matter if shown before
    if location in doctors_data:
        if language in doctors_data[location]:
            # Optional: store location in session
            session['last_location'] = location
            return doctors_data[location][language]
        else:
            return "Doctor data not available in your language."
    else:
        return "Sorry, we don't have doctor data for that location."
