
from app import create_app, db, bcrypt
from app.models.models import User

app = create_app()

def seed_doctors():
    with app.app_context():
        # Check if they already exist to avoid duplicates
        doctors_to_add = [
            ("Dr. Smith", "smith@medmining.com", "Cardiology", 15),
            ("Dr. Jones", "jones@medmining.com", "Dermatology", 8),
            ("Dr. Williams", "williams@medmining.com", "Neurology Specialist", 12),
            ("Dr. Brown", "brown@medmining.com", "General Physician", 20),
            ("Dr. Taylor", "taylor@medmining.com", "Pediatric Care", 10),
            ("Dr. Miller", "miller@medmining.com", "Orthopedic Surgeon", 14),
            ("Dr. Garcia", "garcia@medmining.com", "Gastroenterologist", 9),
            ("Dr. Wilson", "wilson@medmining.com", "Pulmonology", 11)
        ]

        for name, email, spec, exp in doctors_to_add:
            existing = User.query.filter_by(email=email).first()
            if not existing:
                hashed_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
                new_doc = User(
                    name=name,
                    email=email,
                    password=hashed_pw,
                    role='doctor',
                    specialization=spec,
                    years_experience=exp,
                    gender='Mixed',
                    age=40
                )
                db.session.add(new_doc)
                print(f"Added {name} ({spec})")
            else:
                print(f"{name} already exists.")
        
        db.session.commit()
        print("Doctor seeding complete!")

if __name__ == "__main__":
    seed_doctors()
