import random
from django .utils import timezone

def generate_order_no():
    timestamp=timezone.now().strftime('Y%m%d%H%M%S')
    random_number=random.randint(1000,9999)
    return f"ORD{timestamp}{random_number}"