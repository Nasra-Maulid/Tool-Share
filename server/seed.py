from config import app, db
from models import User, Tool, Booking, Review
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

def seed_data():
    with app.app_context():
        print("Deleting old data...")
        db.session.query(Review).delete()
        db.session.query(Booking).delete()
        db.session.query(Tool).delete()
        db.session.query(User).delete()
        
        print("Creating users...")
        users = []
        for i in range(10):
            user = User(
                username=fake.user_name(),
                email=fake.email(),
                phone=fake.phone_number(),
                address=fake.address(),
                is_admin=(i == 0)
            )
            user.password_hash = 'password'
            users.append(user)
            db.session.add(user)
        
        db.session.commit()

        print("Creating tools...")
        tool_images = [
            'drill.jpg', 'lawnmower.jpg', 'pressure_washer.jpg',
            'ladder.jpg', 'saw.jpg', 'hammer.jpg',
            'wrench.jpg', 'screwdriver.jpg', 'pliers.jpg', 'shovel.jpg'
        ]
        
        tools = []
        for i in range(20):
            tool = Tool(
                name=fake.word().capitalize() + ' ' + fake.word(),
                description=fake.sentence(),
                image_url=f'/images/tools/{tool_images[i % len(tool_images)]}',
                daily_rate=round(random.uniform(5, 50), 2),
                deposit=round(random.uniform(0, 100), 2),
                available=random.choice([True, False]),
                owner_id=random.choice(users).id
            )
            tools.append(tool)
            db.session.add(tool)
        
        db.session.commit()

        print("Creating bookings...")
        for i in range(15):
            start_date = fake.date_time_between(start_date='-30d', end_date='+30d')
            end_date = start_date + timedelta(days=random.randint(1, 7))
            booking = Booking(
                start_date=start_date,
                end_date=end_date,
                status=random.choice(['pending', 'approved', 'rejected', 'completed']),
                total_price=round(random.uniform(20, 200), 2),
                tool_id=random.choice(tools).id,
                borrower_id=random.choice(users).id
            )
            db.session.add(booking)
        
        db.session.commit()

        print("Creating reviews...")
        for i in range(25):
            review = Review(
                rating=random.randint(1, 5),
                comment=fake.paragraph(),
                tool_id=random.choice(tools).id,
                reviewer_id=random.choice(users).id
            )
            db.session.add(review)
        
        db.session.commit()
        print("✅ Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
