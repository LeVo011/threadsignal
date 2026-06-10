from database import SessionLocal, engine
from models import Base, Customer, Order
from datetime import datetime, timedelta
import random

Base.metadata.create_all(bind=engine)

customers_data = [
    ("Priya Sharma", "priya@gmail.com", "9811001001", "Delhi"),
    ("Rohan Mehta", "rohan@gmail.com", "9822002002", "Mumbai"),
    ("Ananya Singh", "ananya@gmail.com", "9833003003", "Bangalore"),
    ("Kabir Joshi", "kabir@gmail.com", "9844004004", "Delhi"),
    ("Sneha Kapoor", "sneha@gmail.com", "9855005005", "Chennai"),
    ("Arjun Nair", "arjun@gmail.com", "9866006006", "Hyderabad"),
    ("Divya Patel", "divya@gmail.com", "9877007007", "Ahmedabad"),
    ("Vikram Rao", "vikram@gmail.com", "9888008008", "Pune"),
    ("Meera Iyer", "meera@gmail.com", "9899009009", "Delhi"),
    ("Aditya Khanna", "aditya@gmail.com", "9800010010", "Mumbai"),
    ("Pooja Verma", "pooja@gmail.com", "9811011011", "Delhi"),
    ("Rahul Gupta", "rahul@gmail.com", "9822012012", "Kolkata"),
    ("Tara Malhotra", "tara@gmail.com", "9833013013", "Delhi"),
    ("Siddharth Roy", "siddharth@gmail.com", "9844014014", "Bangalore"),
    ("Nisha Bajaj", "nisha@gmail.com", "9855015015", "Mumbai"),
]

products = [
    "Oversized Linen Blazer", "Floral Wrap Dress", "Slim Fit Chinos",
    "Embroidered Kurta", "Leather Crossbody Bag", "High-Waist Denim",
    "Block Print Co-ord Set", "Relaxed Fit Joggers", "Ethnic Fusion Jacket",
    "Strappy Heels"
]

def seed():
    db = SessionLocal()
    existing = db.query(Customer).first()
    if existing:
        print("Already seeded.")
        db.close()
        return

    for name, email, phone, city in customers_data:
        num_orders = random.randint(1, 5)
        # some customers haven't ordered in 60+ days (win-back targets)
        if random.random() < 0.4:
            last_days_ago = random.randint(65, 120)
        else:
            last_days_ago = random.randint(5, 55)

        last_order_date = datetime.utcnow() - timedelta(days=last_days_ago)
        total_spent = 0

        customer = Customer(
            name=name, email=email, phone=phone, city=city,
            last_order_date=last_order_date
        )
        db.add(customer)
        db.flush()

        for i in range(num_orders):
            amount = random.choice([799, 1299, 1999, 2499, 3299, 4199])
            total_spent += amount
            order_date = last_order_date - timedelta(days=random.randint(0, 30) * i)
            order = Order(
                customer_id=customer.id,
                amount=amount,
                product_name=random.choice(products),
                created_at=order_date
            )
            db.add(order)

        customer.total_spent = total_spent

    db.commit()
    db.close()
    print("Seeded 15 fashion customers with orders.")

if __name__ == "__main__":
    seed()