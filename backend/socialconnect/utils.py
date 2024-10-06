from datetime import datetime, timedelta

def generate_facebook_expiry_date():
    return datetime.now() + timedelta(days=59)