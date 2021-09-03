from SQL_alchemy_classes import *
from datetime import date 
import random

from faker import Faker
fake = Faker()


def insert_users():
    with session as connection:
        for _i in range(1000):
            name = fake.first_name()+" "+fake.last_name()
            contact = Contact(name = name, birthday =
                              fake.date(), created_at=date.today())
            session.add(contact)
            session.commit()
            id = contact.contact_id
            try:
                email = Email_(email= fake.company_email(), contact_id = id)
                session.add(email)
                session.commit()
            except:
                session.rollback()
                print("scipped e-mail for user ID ", id )                          
            for i in range(random.randrange(0,3,1)):
                phone = Phone_(phone = fake.msisdn(), contact_id = id)
                session.add(phone)
                session.commit()
            country =  fake.country()
            if len(country)>50:
                country = country[:50]
            address = Address_(zip = fake.postcode(), city=
                                   fake.city(),
                                   country = country,
                                   street = fake.street_name(),
                                   region = "",
                                   house = fake.building_number(),
                                   apartment = random.randrange(1,100,1),
                                   contact_id = id)
            session.add(address)
            session.commit()

     
def insert_notes():
    with session as connection:
        for _i in range(1000):
            try:
                note = Note_(keywords = ",".join(fake.text(max_nb_chars=50).split(" ")), created_at =
                              fake.date())
                session.add(note)
                session.commit()
                id = note.note_id
            except:
                session.rollback()
                print("Skipped note" )    
                continue
            try:
                text = Text(text=fake.text(max_nb_chars=250), note_id = id)
                session.add(text)
                session.commit()
            except:
                session.rollback()
                print("Skipped text", id )                          
         
            
if __name__ == '__main__':
    from alembic.config import Config
    from alembic import command
    engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/contact_book")
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.bind = engine
    alembic_cfg = Config("./alembic.ini")
    command.upgrade(alembic_cfg, "head")
    insert_users()    
    insert_notes()
    engine.dispose()
