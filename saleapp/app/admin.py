from app.models import Doctor, Medicine, MedicineUnit, MedicineBill, Administrator, ExaminationSchedule, TimeFrame, UserRole
from flask_admin import Admin, BaseView, expose
from app import app, db
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect, session
import dao


class AdminView(ModelView):
    def is_accessible(self):

        return current_user.is_authenticated and current_user.account_role.__eq__(UserRole.Admin)

# if isinstance(doctor1, Doctor):
#     print("doctor1 is an instance of Doctor")
# else:
#     print("doctor1 is not an instance of Doctor")
class DoctorView(AdminView):
    column_list = ['id','name','specialist']
    column_searchable_list = ['name']
    column_filters = ['name']
    column_editable_list = ['name']
    can_export = True


class MedicineView(AdminView):
    column_list = ['name','description']
class MedicineUnitView(AdminView):
    column_list = ['id','unit','medicines']



class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

class TimeFrameView(AdminView):
    column_list = ['id','time']

class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        total_fee_in_month = dao.revenue_stats_by_time2(time=12)
        records = dao.revenue_stats_by_time(time=12)
        print(records)
        tyle = []
        ngay = []
        for record in records:
            percentage = (float(record[2])/float(total_fee_in_month[0][1]))*100
            tyle.append(percentage)
            tmp = (record[0].strftime("%Y-%m-%d"))
            a = tmp.split('-')
            ngay.append(a[2])
        print(tyle)
        print(ngay)
        session['dem'] = 0
        return self.render('admin/stats.html', records= dao.revenue_stats_by_time(time=12), total = total_fee_in_month[0][1],tyle = tyle,ngay = ngay)


admin = Admin(app=app, name='eCommerce Admin', template_mode='bootstrap4')
admin.add_view(MedicineUnitView(MedicineUnit,db.session))
admin.add_view(MedicineView(Medicine,db.session))
admin.add_view(DoctorView(Doctor,db.session))


admin.add_view(TimeFrameView(TimeFrame,db.session))
admin.add_view(StatsView(name="Thong ke"))
admin.add_view(LogoutView(name="Logout"))