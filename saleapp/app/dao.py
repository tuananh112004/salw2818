from itertools import count

from sqlalchemy import text, func
from app.models import Patient, User, TimeFrame, ExaminationList, TimeFrame, ExaminationSchedule, Account, Nurse, \
    MedicineUnit, Medicine, Precription, MedicineBill, Doctor
import hashlib
from flask import Flask, g, render_template, session
from app import app,db
from datetime import datetime
from flask_login  import logout_user,current_user

from flask import render_template, request, redirect
# def load_categories():
#
#     return Category.query.order_by('id').all()
#
#
# def load_products(cate_id=None, kw = None, page =1):
#     query = Product.query
#     if kw:
#         query = query.filter(Product.name.contains(kw))
#     if cate_id:
#         query = query.filter(Product.category_id == cate_id)
#
#     page_size = app.config.get('PAGE_SIZE')
#     start = (page - 1) * page_size
#     query = query.slice(start, start+page_size)
#
#
#     return query.all()
# def count_products():
#     return Product.query.count()
# db.session.query(Patient.id,Patient.name, Patient.sex, Patient.birthday, Patient.address)\
#                 .join(ExaminationSchedule, ExaminationSchedule.patient_id==User.id) \
#                 .group_by(Patient.id) \
#                 .filter(func.date(ExaminationSchedule.date_examination).__eq__(appointment_date)).all()


def get_unit_by_id(id):
    return MedicineUnit.query.get(id)

def get_precription_by_medicine_bill_id(id):
    return db.session.query(Medicine.name ,Medicine.unit_id,func.sum(Precription.amount), func.sum(Medicine.price))\
            .join(Medicine,Medicine.id == Precription.medicine_id)\
            .group_by(Medicine.name,Medicine.unit_id).all()


def get_medicine_bill_by_id(id):
    return MedicineBill.query.filter_by(id=id).first()

def get_medicine_bill():
    return db.session.query(MedicineBill).all()

def get_medcine_bill_by_patient_id(patient_id):
    return db.session.query(MedicineBill).filter(MedicineBill.patient_id == patient_id).all()


def auth_user(username, password):
    # password2 =  str(hashlib.md5('123'.encode('utf-8')).hexdigest())
    return Account.query.filter(Account.username.__eq__(username),
                             Account.password.__eq__(password)).first()

def get_user_by_id(id):
    return Account.query.get(id)

def get_info_user_by_account_id(id):
    return db.session.query(User).filter(User.account_id==id).first()

def get_patient_name_by_id(id):
    return db.session.query(Patient).filter(Patient.id==id).first()

def get_list_patient():
    return Patient.query.all()

def get_info_user2(id):
    return db.session.query(Patient).join(User, User.id==Patient.id).filter(Patient.id==id).first()

def get_info_user3(id):
    return db.session.query(User).filter(User.id==id).first()
#
# name = request.form.get('name')
#         address = request.form.get('address')
#         sex = request.form.get('gender')
#         birth = request.form.get('birth')
#         avatar = request.form.get('avatar')

def change_info_user(name,address,sex, birth, avatar, user_id):
    user = db.session.query(User).filter(User.id==user_id).first()
    print(user)
    user.name = name
    user.address = address
    user.birthday = birth
    user.avatar = avatar
    user.sex = sex
    db.session.commit()
    return user
def get_list_time_frame():
    return TimeFrame.query.all()

def get_nurse_by_current_id(id):
    return Nurse.query.filter(Nurse.account_id == id).first()


def delete_patient(patient_id):
    patient = Patient.query.get(patient_id)
    return db.session.delete(patient)


def dateTrans(data):

    if isinstance(data, datetime):
        return data.strftime('%d-%m-%Y')

    return data
def get_list_patient2(appointment_date):
    # target_date = datetime(2024, 12, 19).date()  # Ngày bạn muốn tìm kiếm

    target_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
    # return db.session.query(Product.id, Product.name, func.sum(ReceiptDetails.quantity * ReceiptDetails.unit_price)) \
    #     .join(ReceiptDetails, ReceiptDetails.product_id.__eq__(Product.id)).group_by(Product.id).all()
    print(target_date)
    dataTest = db.session.query(Patient.id,Patient.name, Patient.sex, Patient.birthday, Patient.address)\
                .join(ExaminationSchedule, ExaminationSchedule.patient_id==User.id) \
                .group_by(Patient.id) \
                .filter(func.date(ExaminationSchedule.date_examination).__eq__(appointment_date)).all()


    dataJson = []
    for data in dataTest:

        tmp = dateTrans(data[3])

        data_dict = {
            "id": data[0],
            "name": data[1],
            "sex": data[2],
            "date": tmp,  # Định dạng lại ngày
            "address": data[4]
        }
        dataJson.append(data_dict)

    session['dataJson'] = dataJson


    return dataTest


def create_appointment(date_examination, note, name, birth, sex, time,address):
    examination_schedules = db.session.query(ExaminationSchedule).filter(func.date(ExaminationSchedule.date_examination).__eq__(date_examination)).all()
    time_frame = TimeFrame.query.filter(TimeFrame.time == time).first()
    print(time_frame)
    time_frame_id = time_frame.id
    patient = Patient(name,sex=sex,birthday=birth, address=address, avatar=None)
    db.session.add(patient)
    db.session.commit()


    u = ExaminationSchedule(note=note,time_frame_id=time_frame_id,patient_id=patient.id, date_examination = date_examination,examination_list_id=None)
    db.session.add(u)
    db.session.commit()
    return True


#   amount = Column(Integer, default=0)
#     note = Column(String(50))
#     medicine_id = Column(Integer, ForeignKey(Medicine.id), nullable=False)
#     medicineBill_id = Column(Integer, ForeignKey(MedicineBill.id), nullable=False)

def get_unit_medicine():
    return db.session.query(MedicineUnit).all()
def get_medicine_by_name(name):
    return db.session.query(Medicine).filter(Medicine.name==name).first()

def get_medicine():
    return db.session.query(Medicine).all()

#
# diagnotic = Column(String(50))
#     symptoms = Column(String(50))
#     examinationDate = Column(DATETIME)
#     doctor_id = Column(Integer, ForeignKey(Doctor.id), nullable=False)
#     patient_id = Column(Integer, ForeignKey(Patient.id), nullable=False)
#     bill_id = Column(Integer, ForeignKey(Bill.id), nullable=True)
def create_medicine_bill(diagnotic, symptoms,examinationDate,doctor_id,patient_id):
    medicineBill = MedicineBill(diagnotic=diagnotic, symptoms=symptoms, examinationDate = examinationDate, doctor_id=doctor_id, patient_id=patient_id)
    print("create_medicine_bill",diagnotic, symptoms,examinationDate,doctor_id,patient_id)
    db.session.add(medicineBill)
    db.session.commit()
    return medicineBill.id

def create_precription(amount,note, medicine_id,medicineBill_id, unit_id):
    print("create_precription",amount,note, medicine_id,medicineBill_id, unit_id)
    precription = Precription(amount = amount, note = note, medicine_id = medicine_id, medicineBill_id = medicineBill_id, unit_id = unit_id)
    db.session.add(precription)
    db.session.commit()

def get_doctor_id_by_account_id(account_id):
    return db.session.query(Doctor).filter(Doctor.account_id==account_id).first()



def get_history_patient(id):
    return db.session.query(MedicineBill).filter(MedicineBill.patient_id==id).all()


def create_account(username,password):
    account = Account(username=username, password=password)
    db.session.add(account)
    db.session.commit()
    return account
def create_patient(name,avatar,account_id):
    patient = User(name=name,avatar=avatar, account_id=account_id)
    db.session.add(patient)
    db.session.commit()
    return patient
if __name__ == '__main__':
    with app.app_context():
        print(get_precription_by_medicine_bill_id(1))

