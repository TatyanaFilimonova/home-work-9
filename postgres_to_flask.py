from  flask import Flask, redirect, url_for
from jinja2 import Template
from flask import request
from datetime import datetime
from datetime import date
import time
import os
from sqlalchemy import create_engine, or_, update, delete
from sqlalchemy.orm import sessionmaker
from SQL_alchemy_classes import *
from flask_app import session

def find_note_query(key):
    res = session.query(
                    Note_.note_id, Note_.keywords, Text.text
                    ).join(Text).filter(
                        or_(func.lower(Note_.keywords).like(func.lower(f"%{key}%")
                        ), func.lower(Text.text).like(func.lower(f"%{key}%"))))
    return res

def find_note_query_id(id):
    result = session.query(
                    Note_.note_id, Note_.keywords, Text.text
                    ).join(Text).filter(Note_.note_id == id)
    return result

def find_note_query_all():
    return session.query(Note_.note_id, Note_.keywords, Text.text).join(Text)

def note_update(request):
    try:
        keywords = request.form.get('Keywords')
        text = request.form.get('Text of note')
        session.execute(update(Note_, values={Note_.keywords: keywords}).filter(Note_.note_id == id))
        session.execute(update(Text, values={Text.text: text}).filter(Text.note_id == id))
        session.commit()
        return 0
    except Exception as e:
        session.rollback()
        return e

def get_all_contacts():
    try:
        result =session.query(Contact.contact_id, Contact.name)
        return result
    except Exception as e:
        raise e
        
        
def get_contact_details(id):
     contact =session.query(Contact.contact_id, Contact.name, Contact.birthday).filter(Contact.contact_id == id)
     phone = session.query(Phone_.phone).filter(Phone_.contact_id == id)
     email = session.query(Email_.email).filter(Email_.contact_id == id)
     address = session.query(Address_).filter(Address_.contact_id == id)
     return (contact, phone, email, address)

def delete_contact_by_id (id):
    try:
        stmt = delete(Contact).where(Contact.contact_id == id)
        session.execute(stmt)    
        session.commit()
        return 0
    except Exception as e:
        session.rollback()
        return e

def insert_note(request):
    try:        
        keywords = request.form.get('Keywords')
        text = request.form.get('Text of note')
        note = Note_(keywords = keywords, created_at = date.today())
        session.add(note)
        session.commit()
        text=Text(note_id = note.note_id, text = text)
        session.add(text)
        session.commit()
        return 0
    except Exception as e:
        session.rollback()
        return e

def delete_note_id(id):
    try:
        stmt = delete(Note_).where(Note_.note_id == id)
        session.execute(stmt)    
        session.commit()
        return 0
    except Exception as e:
        session.rollback()
        return e

def update_contact_details(form_dict, id):
    try:
         session.execute(update(Contact, values={
             Contact.name: form_dict['Name']['value'],
             Contact.birthday:form_dict['Birthday']['value']}
                         ).filter(Contact.contact_id == id))
         session.commit()
         stmt = delete(Phone_).where(Phone_.contact_id == id)
         session.execute(stmt)    
         session.commit()
         for ph in [phone_.strip() for phone_ in form_dict['Phone']['value'].split(",")]:
             phone = Phone_(contact_id=id, phone = ph)
             session.add(phone)
         stmt = delete(Address_).where(Address_.contact_id == id)
         session.execute(stmt)
         address = Address_(zip = form_dict['ZIP']['value'],
                         country = form_dict['Country']['value'],
                         region = form_dict['Region']['value'],
                         city = form_dict['City']['value'],
                         street = form_dict['Street']['value'],
                         house = form_dict['House']['value'],
                         apartment =form_dict['Apartment']['value'], 
                         contact_id = id)
         email=Email_(email = form_dict['Email']['value'],
                      contact_id = id)
         session.add(address)
         stmt = delete(Email_).where(Email_.contact_id == id)
         session.execute(stmt)
         session.commit()
         session.add(email)
         session.commit()
         return 0     
    except Exception as e:
        return e
    finally:
        session.rollback()

def contact_query(k):
    result = session.query(
                    Contact.contact_id, Contact.name
                    ).join(Phone_).filter(
                        or_(func.lower(Contact.name).like(func.lower(f"%{k}%")
                        ), func.lower(Phone_.phone).like(func.lower(f"%{k}%"))))
    return result

def insert_contact(form_dict):
    try:
        contact= Contact(name = form_dict['Name']['value'],
                     created_at= date.today(),
                     birthday = form_dict['Birthday']['value'])
        session.add(contact)
        session.commit()
    except Exception as e:
        return e
    finally:
        session.rollback();
    try:    
        for ph in [phone_.strip() for phone_ in form_dict['Phone']['value'].split(",")]:
            phone = Phone_(contact_id=contact.contact_id, phone = ph)
            session.add(phone)
        address = Address_(zip = form_dict['ZIP']['value'],
                           country = form_dict['Country']['value'],
                           region = form_dict['Region']['value'],
                           city = form_dict['City']['value'],
                           street = form_dict['Street']['value'],
                           house = form_dict['House']['value'],
                           apartment =form_dict['Apartment']['value'], 
                           contact_id = contact.contact_id)
        email=Email_(email = form_dict['Email']['value'],
                     contact_id = contact.contact_id)
        session.add(address)
        session.add(email)
        session.commit()
    except Exception as e:
        return e
    finally:
        session.rollback()
    return 0    


def get_birthdays(request):
   period = request.form.get('Period')
   sql_text=f'''
                select contact_id, name,  date(birthday+(date_trunc('year', now()) - date_trunc('year', birthday)))  as celebrate from contact
                where 
                birthday+(date_trunc('year', now()) - date_trunc('year', birthday)) 
                between 
                date_trunc('day', now()) 
                and 
                date_trunc('day', now()+interval '{period} day');
                '''    
   result = session.execute(sql_text).fetchall()
   return result
