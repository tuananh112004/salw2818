import math
from sqlalchemy import text, func, result_tuple
from flask import render_template, request, redirect, jsonify, send_file, g, session
from pyexpat.errors import messages
from app.models import Patient, User, TimeFrame, ExaminationList, TimeFrame, ExaminationSchedule, Account,MedicineBill, Medicine
import json
import dao
import locale
locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
from app import app, login,db
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
import pandas as pd
from io import BytesIO

@app.route('/comments', methods=['post'])
@login_required
def addcomment():

    content = request.json.get('content')
    c = dao.add_comment(content=content)
    user = dao.get_info_user3(c.user_id)
    return jsonify({
        "content": c.content,
        "created_date": c.created_date,
            # "avatar": user.avatar,https://res.cloudinary.com/dxxwcby8l/image/upload/v1646729533/zuur9gzztcekmyfenkfr.jpg
        "avatar": user.avatar,
        "username": user.name

    })
@app.route("/", methods=['get', 'post'])
def index():

    if request.method.__eq__('POST'):
        appointment_date = request.form.get('appointment_date')

        if (appointment_date):
            pass
        else:
            appointment_date = '2024-12-12'
        date_obj = datetime.strptime(appointment_date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d-%m-%Y')
        count_schedule = dao.get_list_patient2(appointment_date)
        if(len(count_schedule) >=40):
            print(len(count_schedule))
            return jsonify({
                "status": 400,
                "messages": "Ngày này đã kín lịch"
                })
        print(len(count_schedule))
        name = request.form.get('name')
        sex = request.form.get('sex')
        birth = request.form.get('birth')
        address = request.form.get('address')
        time = request.form.get('time')
        note = request.form.get('note')
        date = request.form.get('date')
        a = dao.create_appointment(name = name, sex=sex, birth=birth, address=address, time = time, note = note,date_examination=date)
        return redirect(request.referrer or '/')
    else:
        time_frames = dao.get_list_time_frame()
        comments = dao.load_comments()
        for comment in comments:
            user_info = dao.get_info_user3(comment.user_id)
            comment.avatar = user_info.avatar
        return render_template('index.html',time_frames=time_frames, comments=comments)

   # return render_template('index.html', categories = cates, products = prods, page = math.ceil(total/page_size))

@app.route("/login", methods=['get', 'post'])
def login_procee():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = dao.auth_user(username, password)
        if u:
            user = dao.get_info_user_by_account_id(u.id)
            print("Doctor",user)
            session['user'] = user.id
            login_user(u)
            return redirect('/')



    return render_template('login.html')

@app.route("/history/<patient_id>")
def history_procee(patient_id):
    record = dao.get_history_patient(patient_id)

    return render_template('patientHistory.html',record=record)


@app.route("/register", methods=['get', 'post'])
def register_procee():
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        avatar = request.form.get('avatar')
        account = dao.create_account(username, password)
        user = dao.create_patient(name, avatar,account_id=account.id)
        return redirect('/login')
    else:
        return render_template("register.html")


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)

@app.route("/logout")
def logout_procees():
    logout_user()
    return redirect('/login')



@app.route("/createList", methods =['get','post'])
def create_list_procee():
    appointment_date = request.form.get('appointment_date')

    if(appointment_date):
        pass
    else:
        appointment_date = '2024-12-12'
    date_obj = datetime.strptime(appointment_date, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%d-%m-%Y')
    if request.method.__eq__('POST'):


        record = dao.get_list_patient2(appointment_date)
        print(record)
        return render_template('list.html', records = record,date=formatted_date)

    return render_template('list.html',date=formatted_date)

@app.route("/info/<user_id>", methods=['get', 'post'])
def info_process(user_id):
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        address = request.form.get('address')
        sex = request.form.get('gender')
        birth = request.form.get('birth')
        avatar = request.form.get('avatar')
        print(name)
        print(address)
        print(sex)
        print(birth)
        print(avatar)
        dao.change_info_user(name=name, address=address, sex=sex, birth=birth, avatar=avatar, user_id=user_id)
        return redirect('/info/'+user_id)

    else:
        user = dao.get_info_user2(user_id)
        if(user.birthday):
            formatted_date = user.birthday.strftime('%Y-%m-%d')
        return render_template('infoUser.html',user=user,date=formatted_date)



@app.route('/api/patient/<patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    if patient_id:
        print(patient_id)
        dao.delete_patient(patient_id)
        return jsonify({"status": 200})
    print("Loi xoa")
    return jsonify({"statussss": 404})

@app.route('/bacSi', methods=['get'])
def bac():
    return render_template("QL.html")

@app.route("/login-admin",methods=['post'])
def login_admin_procees():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = dao.auth_user(username, password)
        if u:
            login_user(u)
            return redirect('/admin')
        return redirect('/admin')

@app.route("/api/timeframe", methods=['GET'])
def timeframe_procee():

    time_frames = dao.get_list_time_frame()
    data = []
    for time_frame in time_frames:
        data.append({'time': time_frame.time})

    print(time_frames)
    # Trả về dữ liệu dưới dạng JSON
    return jsonify(data)  # Đảm bảo trả về đối tượng jsonify để Flask trả về response JSON

@app.route("/export_excel")
def export_excel_procee():

    # [(2, 'aa', 'nam', datetime.datetime(2000, 2, 2, 0, 0), 'HCM'),
    #  (3, 'aa', 'nam', datetime.datetime(2000, 2, 2, 0, 0), 'HCM'),
    #  (4, 'aa', 'nam', datetime.datetime(2000, 2, 2, 0, 0), 'HCM'), (7, 'Nguyen Le Ngoc Anh', '0798536554', None, None)]
    data = [
        {'examination_id': 5, 'patient_name': 'aa', 'patient_id': 5, 'time': '3:00', 'examination_date': '2024-12-20'},
        {'examination_id': 5, 'patient_name': 'aa', 'patient_id': 5, 'time': '3:00', 'examination_date': '2024-12-20'}
    ]
    data2 = session.get('dataJson', None)
    print(data2)
    df = pd.DataFrame(data2)

    # Sử dụng BytesIO để lưu tạm file Excel trong bộ nhớ (không ghi vào disk)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Examination Data')

    # Đưa con trỏ về đầu file
    output.seek(0)

    # Gửi file Excel về phía người dùng
    return send_file(output, as_attachment=True, download_name="examination_data.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



@app.route("/taoDon/<patient_id>/<date>", methods=['GET','POST'])
def taoDon(patient_id,date):
    name = dao.get_patient_name_by_id(patient_id)
    # formatted_date = datetime.strptime(date, '%Y-%m-%d')
    if request.method.__eq__('POST'):
        trieu_chung = request.form.get('trieuChung')
        du_doan_benh = request.form.get('duDoanBenh')
        drug_data = request.form.get('drugCollector')
        doctor_id = session['user']

        print(doctor_id)
        print(du_doan_benh)
        print(drug_data)
        medicine_bill_id = dao.create_medicine_bill(diagnotic=du_doan_benh, symptoms=trieu_chung, examinationDate=datetime.now(), doctor_id=doctor_id, patient_id=patient_id)
        ans = json.loads(drug_data)
        print(ans)
        for medicine in ans:
            amount = medicine['drugQuantity']
            note = medicine['drugUsage']
            medicine_id = dao.get_medicine_by_name(medicine['drugName']).id
            unit_id = medicine['drugUnit']
            newprecription =  dao.create_precription(amount, note, medicine_id, medicineBill_id = medicine_bill_id, unit_id = unit_id)

        return redirect(request.referrer or '/')
        pass
    else:
        unit_medicine = dao.get_unit_medicine()
        print(unit_medicine)
        # medicines = dao.get_medicines()
        return render_template('taoDon.html',patient_id = patient_id,name=name,date=date,unit_medicine=unit_medicine)








@app.route('/api/search-drugs', methods=['GET'])
def search_drugs():
    query = request.args.get('q',' ').strip()  # Lấy tham số `q` từ URL

    if not query:
        return jsonify([])  # Trả về danh sách rỗng nếu không có từ khóa tìm kiếm

    print(query)
    # results = db.session.query(Medicine.name).filter(Medicine.name.__eq__(query)).limit(4).all()
    results = db.session.query(Medicine.name).filter(func.lower(Medicine.name).like(f"%{query.lower()}%")).limit(4).all()
    results_list = [{'name': result[0]} for result in results]

    return jsonify(results_list)


@app.route("/listPatient",methods=['GET','POST'])
def get_list_patient_procees():
    appointment_date = request.form.get('appointment_date')
    # appointment_date = datetime.today().strftime('%Y-%m-%d')
    if(appointment_date):
        pass
    else:
        appointment_date = '2024-12-12'
    date_obj = datetime.strptime(appointment_date, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%d-%m-%Y')
    if request.method.__eq__('POST'):


        record = dao.get_list_patient2(appointment_date)
        print(record)
        return render_template('patientList.html', records = record,date=formatted_date)

    return render_template('patientList.html',date=formatted_date)


@app.route("/QL",methods=['GET','POST'])
def get_QL():


    return render_template('quanLyIndex.html')


@app.route("/QL/thanhToan", methods=['GET', 'POST'])
def get_thanh_toan():

    medicine_bills = dao.get_medicine_bill()
    for medicine in medicine_bills:
        patient = dao.get_patient_name_by_id(medicine.patient_id)
        print(medicine)
        medicine.patient_name = patient.name
    return render_template('listMedicineBill.html',medicine_bills=medicine_bills)


from collections import OrderedDict
from decimal import Decimal
@app.route("/QL/thanhToan/<medicine_bill_id>", methods=['GET', 'POST'])
def get_thanh_toan_detail(medicine_bill_id):
    if request.method.__eq__('POST'):
        total = request.form.get('totalFeeB')
        serviceFee = request.form.get('serviceFee')
        medicineFee = int(total) - int(serviceFee)
        medicine_bill_id = medicine_bill_id
        cashier = dao.get_info_user_by_account_id(current_user.id)
        cashier_id = cashier.id
        medicineBill = dao.get_medicine_bill_by_id(medicine_bill_id)
        patient_id = medicineBill.patient_id
        bill = dao.create_bill(medicineMoney=medicineFee, serviceFee=serviceFee,totalFee= total,  cashier_id = cashier_id, patient_id = patient_id)
        updateBill = dao.update_medicine_bill(medicine_bill_id = medicine_bill_id, bill_id = bill.id)
        print(total)

        return redirect(request.referrer or '/')
    else:
        medicine_bill = dao.get_medicine_bill_by_id(medicine_bill_id)
        patient = dao.get_patient_name_by_id(medicine_bill.patient_id)
        medicines = dao.get_precription_by_medicine_bill_id(medicine_bill_id)
        result_tuple = ()
        for medicine in medicines:
            unit = dao.get_unit_by_id(medicine.unit_id)
            print(medicine)

            medicine = tuple(medicine)
            medicine = medicine + (unit.unit,)

            # Lấy các phần tử trong tuple
            name = medicine[0]
            amount = medicine[2]
            price = medicine[3]
            unit = medicine[4]
            # Chia số tiền (price) cho 1000 và làm tròn về 3 chữ số thập phân
            # formatted_price = locale.currency(price, grouping=True)

            # Tạo lại tuple với giá trị đã thay đổi
            new_tuple = (name, unit, amount, price)
            result_tuple = result_tuple + (new_tuple,)
        return render_template('thanhToan.html',patient=patient,medicine_bill=medicine_bill,medicines=result_tuple)


if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
