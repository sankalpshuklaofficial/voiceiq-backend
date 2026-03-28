from app.db.database import Base, engine
from app.models.user import User
from app.models.business import Business, BusinessType
from app.models.call import Call
from app.models.appointment import Appointment
from app.models.subscription import Subscription

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")