from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Member, ElectricityUsage, Room, Payment, Complaint, LeaseAgreement, News, Notification
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import MemberForm ,ComplaintForm, PaymentForm, LeaseAgreementForm, NewsForm
from datetime import datetime
from decimal import Decimal  
from django.apps import apps
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import force_str
from django.db.models import Sum
import json
from django.http import JsonResponse
import os

Room = apps.get_model('finalapp', 'Room')
Member = apps.get_model('finalapp', 'Member')

def check_email(request):
    email = request.GET.get('email', None)
    if email and User.objects.filter(email=email).exists():
        return JsonResponse({'exists': True})
    return JsonResponse({'exists': False})

def check_phone(request):
    phone = request.GET.get('phone', None)
    if phone and Member.objects.filter(phone=phone).exists():
        return JsonResponse({'exists': True})
    return JsonResponse({'exists': False})

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'member') and user.member.role == 'admin'

def index(request):
    create_admin_account_once()
    rooms = Room.objects.all()
    for room in rooms:
        room.room_type_display = room.get_room_type_display()  
    return render(request, "myapp/index.html", {"rooms": rooms})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            user = User.objects.get(email=email)  
            user = authenticate(request, username=user.username, password=password) 
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            member = Member.objects.get(user=user)

            if member.role == 'admin':
                return redirect('/manage/home/') 
            else:
                return redirect('home')  

    return render(request, 'myapp/login.html')

def register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if password == confirm_password:
            if not User.objects.filter(username=email).exists() and not Member.objects.filter(phone=phone).exists():
                user = User.objects.create_user(username=email, email=email, password=password)
                user.save()

                Member.objects.create(
                    user=user,
                    fullname=fullname,
                    email=email,
                    phone=phone
                )

                return redirect('login')  # ไปยังหน้าเข้าสู่ระบบหลังจากสมัครสมาชิกสำเร็จ
    return render(request, 'myapp/register.html')

def create_admin_account_once():
    email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    phone = os.getenv('ADMIN_PHONE', '0999999999')
    fullname = os.getenv('ADMIN_FULLNAME', 'Test Admin')
    password = os.getenv('ADMIN_PASSWORD', '1234')

    if not User.objects.filter(username=email).exists():
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        Member.objects.create(
            user=user,
            fullname=fullname,
            email=email,
            phone=phone,
            role='admin'
        )

def admin_register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if password == confirm_password:
            if not User.objects.filter(username=email).exists() and not Member.objects.filter(phone=phone).exists():
                user = User.objects.create_user(username=email, email=email, password=password)
                user.save()

                Member.objects.create(
                    user=user,
                    fullname=fullname,
                    email=email,
                    phone=phone,
                    role='admin'  # 👈 บังคับเป็น admin
                )

                return redirect('login')  # หรือไปหน้า admin login ก็ได้
    return render(request, 'myapp/admin_register.html')

@login_required(login_url='login')
def home(request):
    member = request.user.member
    user_room = member.room  # ดึง room โดยตรงผ่าน member.room
    return render(request, 'myapp/home.html', {'member': member, 'room': user_room})

@login_required(login_url='login')
def logout_view(request):
    logout(request)  
    return redirect('index')  

@login_required(login_url='login')  
def profile_view(request):
    member = Member.objects.get(user=request.user)
    return render(request, 'myapp/user/profile_member.html', {'member': member})

@login_required(login_url='login')  
def edit_profile_view(request):
    member = Member.objects.get(user=request.user)
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            return redirect('profile') 
    else:
        form = MemberForm(instance=member)
    return render(request, 'myapp/user/edit_profile.html', {'form': form})

@login_required(login_url='login')  
def rent_check_view(request):
    Member = apps.get_model('finalapp', 'Member')
    Room = apps.get_model('finalapp', 'Room')
    ElectricityUsage = apps.get_model('finalapp', 'ElectricityUsage')
    Payment = apps.get_model('finalapp', 'Payment')  # ✅ เพิ่มการดึง Payment
    user = request.user

    try:
        member = Member.objects.get(user=user)
    except Member.DoesNotExist:
        return render(request, "myapp/payment/rent_check.html", {
            "user_room": None,
            "room_not_found": True
        })

    user_room = member.room

    if not user_room:
        messages.warning(request, "คุณยังไม่มีห้องพักที่ลงทะเบียน")
        return render(request, "myapp/payment/rent_check.html", {
            "user_room": None,
            "room_not_found": True
        })

    selected_month = request.GET.get("month")
    available_months = ElectricityUsage.objects.filter(room=user_room).values_list("month_year", flat=True).distinct()

    if not selected_month:
        latest_usage = ElectricityUsage.objects.filter(room=user_room).order_by("-month_year").first()
        selected_month = latest_usage.month_year if latest_usage else None

    selected_usage = ElectricityUsage.objects.filter(room=user_room, month_year=selected_month).first()

    electricity_cost = selected_usage.consumption * user_room.electricity_price if selected_usage else 0
    total_cost = user_room.rent_price + electricity_cost + user_room.water_price

    # ✅ เพิ่มการดึง Payment มาด้วย
    payment = Payment.objects.filter(member=member, room=user_room, month_year=selected_month).first()

    return render(request, "myapp/payment/rent_check.html", {
        "user_room": user_room,
        "room_not_found": False,
        "rent_price": user_room.rent_price,
        "electricity_cost": electricity_cost,
        "water_price": user_room.water_price,
        "total_cost": total_cost,
        "selected_month": selected_month,
        "available_months": available_months,
        "selected_usage": selected_usage,
        "payment": payment  # ✅ ส่ง payment ไปหน้า template
    })


@login_required(login_url='login')
def electricity_usage_view(request):
    Member = apps.get_model('finalapp', 'Member')
    Room = apps.get_model('finalapp', 'Room')
    ElectricityUsage = apps.get_model('finalapp', 'ElectricityUsage')

    user = request.user 
    try:
        member = Member.objects.get(user=user)
    except Member.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลผู้ใช้")
        return render(request, "myapp/meter/electricity_usage.html", {
            "electricity_usages": [],
            "user_room": None,
            "room_not_found": True
        })
    
    user_room = member.room  # ✅ แก้ตรงนี้ ไม่ต้อง filter หา

    if not user_room:
        messages.warning(request, "คุณยังไม่มีห้องพักที่ลงทะเบียน")
        return render(request, "myapp/meter/electricity_usage.html", {
            "electricity_usages": [],
            "user_room": None,
            "room_not_found": True
        })

    electricity_usages = ElectricityUsage.objects.filter(room=user_room).order_by("month_year")

    return render(request, "myapp/meter/electricity_usage.html", {
        "electricity_usages": electricity_usages,
        "user_room": user_room.room_number,
        "room_not_found": False
    })

@login_required(login_url='login')
def complaint_view(request):
    user = request.user 
    try:
        member = Member.objects.get(user=user)  
    except Member.DoesNotExist:
        messages.error(request, "ไม่พบสมาชิก")
        return redirect('home')

    room = member.room  # ✅ ดึงห้องตรงจาก member

    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            room_from_form = form.cleaned_data.get('room')  # กรณีมีเลือกห้องเอง
            description = form.cleaned_data.get('description')

            if room_from_form and description:
                complaint = form.save(commit=False)
                complaint.member = member
                complaint.room = room_from_form
                try:
                    complaint.save()
                    messages.success(request, "การร้องเรียนถูกส่งแล้ว")
                    return redirect('complaint_success')
                except Exception as e:
                    messages.error(request, f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")
            else:
                messages.error(request, "กรุณากรอกข้อมูลให้ครบถ้วน")
        else:
            messages.error(request, "ข้อมูลที่กรอกไม่ถูกต้อง")
    else:
        form = ComplaintForm(initial={'room': room})  # Pre-fill ห้องให้เลย

    context = {
        'form': form,
        'room': room,
    }
    return render(request, "myapp/complaint/complaint.html", context)


@login_required(login_url='login')
def complaint_success(request):
    return render(request, 'myapp/complaint/complaint_success.html')

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_home(request):
    total_monthly_rent = Payment.objects.filter(status="approved", month_year__isnull=False) \
        .aggregate(total=Sum("amount"))["total"] or 0

    total_monthly_rent = float(total_monthly_rent)  

    total_tenants = Member.objects.filter(role="user").count()
    total_rooms = Room.objects.count()


    monthly_data = Payment.objects.filter(status="approved", month_year__isnull=False) \
        .values("month_year").annotate(total=Sum("amount")).order_by("month_year")
    
    monthly_labels = [entry["month_year"] for entry in monthly_data]
    monthly_values = [float(entry["total"]) for entry in monthly_data]  


    yearly_data = Payment.objects.filter(status="approved", month_year__isnull=False) \
        .values("month_year").annotate(total=Sum("amount"))

    yearly_revenue = {}
    for entry in yearly_data:
        year = entry["month_year"].split("-")[0] 
        if year not in yearly_revenue:
            yearly_revenue[year] = 0
        yearly_revenue[year] += float(entry["total"])

    yearly_labels = list(yearly_revenue.keys())
    yearly_values = list(yearly_revenue.values())

    context = {
        "total_monthly_rent": total_monthly_rent,
        "total_tenants": total_tenants,
        "total_rooms": total_rooms,
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_data": json.dumps(monthly_values),
        "yearly_labels": json.dumps(yearly_labels), 
        "yearly_data": json.dumps(yearly_values),
    }
    return render(request, "myapp/admin_home.html", context)

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_user_list(request):
    users = Member.objects.all()
    admins_count = users.filter(role="admin").count()
    users_count = users.filter(role="user").count()

    context = {
        'users': users,
        'admins_count': admins_count,
        'users_count': users_count
    }

    return render(request, 'myapp/user/admin_user_list.html', context)

@login_required(login_url='login')
@user_passes_test(is_admin)
def get_user_profile(request, user_id):
    try:
        user = Member.objects.get(id=user_id)
        data = {
            "fullname": user.fullname,
            "email": user.email,
            "phone": user.phone,
            "address": user.address or "-",
            "sex": user.sex or "-",
            "birthday": user.birthday.strftime("%d/%m/%Y") if user.birthday else "-",
            "profile": user.profile_picture.url if user.profile_picture else "/static/images/default_profile.png",
            "role": user.role
        }
        return JsonResponse(data)
    except Member.DoesNotExist:
        return JsonResponse({"error": "ไม่พบผู้ใช้"}, status=404)


### ✅ ฟังก์ชันเปลี่ยน Role ของผู้ใช้
@login_required(login_url='login')
@user_passes_test(is_admin)
def change_user_role(request, user_id, new_role):
    member = get_object_or_404(Member, id=user_id)
    if new_role in ['admin', 'user']:
        member.role = new_role
        member.save()
        messages.success(request, f"Updated {member.fullname} to {new_role}")
    else:
        messages.error(request, "Invalid role")
    return redirect('admin_user_list')

### ✅ ฟังก์ชันลบ User
@login_required(login_url='login')
@user_passes_test(is_admin)
def delete_user(request, user_id):
    member = get_object_or_404(Member, id=user_id)
    member.delete()
    messages.success(request, f"Deleted {member.fullname}")
    return redirect('admin_user_list')

@login_required(login_url='login')
@user_passes_test(is_admin)
def add_user(request):
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        Member.objects.create(fullname=fullname, email=email, phone=phone, role="user")
        messages.success(request, "เพิ่มผู้ใช้สำเร็จ!")
        return redirect('admin_home')
    
@login_required(login_url='login')
@user_passes_test(is_admin)
def edit_user(request):
    if request.method == "POST":
        user = get_object_or_404(Member, id=request.POST.get('user_id'))
        user.fullname = request.POST.get('fullname')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.save()
        messages.success(request, "แก้ไขข้อมูลสำเร็จ!")
    return redirect('admin_home')

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_room(request):
    rooms = Room.objects.all().order_by('room_number')
    members = Member.objects.filter(role='user', room__isnull=True)
    room_members = {member.room_id: member for member in Member.objects.filter(role='user', room__isnull=False)}

    return render(request, 'myapp/room/admin_room.html', {
        'rooms': rooms,
        'members': members,
        'room_members': room_members
    })

@login_required(login_url='login')
@user_passes_test(is_admin)
def add_room(request):
    if request.method == "POST":
        room_number = request.POST.get('room_number')
        room_type = request.POST.get('room_type')
        size = request.POST.get('size')
        status = request.POST.get('status', 'available')
        rent_price = request.POST.get('rent_price', 0)
        electricity_price = request.POST.get('electricity_price', 0)
        water_price = request.POST.get('water_price', 0)

        # ✅ รับค่าจาก checkbox สิ่งอำนวยความสะดวก
        facilities = request.POST.getlist('facilities')

        # ✅ รับไฟล์รูปที่อัปโหลด
        image = request.FILES.get('image')

        if not room_number or not room_type or not size:
            messages.error(request, "❌ กรุณากรอกหมายเลขห้อง, ประเภทห้อง และขนาดห้องให้ครบถ้วน")
            return redirect('admin_room_add')

        try:
            size = float(size)
            rent_price = float(rent_price)
            electricity_price = float(electricity_price)
            water_price = float(water_price)
        except ValueError:
            messages.error(request, "❌ กรุณากรอกตัวเลขที่ถูกต้อง")
            return redirect('admin_room_add')

        # ✅ ถ้าไม่มีการอัปโหลด ให้เลือก Default ตามประเภทห้อง
        if not image:
            if room_type == "Standard":
                image = "room_images/default_standard.png"
            elif room_type == "Deluxe":
                image = "room_images/default_deluxe.png"
            else:
                image = "room_images/default_room.png"

        facilities = request.POST.getlist('facilities')

        Room.objects.create(
            room_number=room_number,
            room_type=room_type,
            size=size,
            status=status,
            rent_price=rent_price,
            electricity_price=electricity_price,
            water_price=water_price,
            facilities=json.dumps(facilities),  # ✅ แปลง list เป็น JSON แล้วบันทึก
            image=image
        )

        messages.success(request, "✅ เพิ่มห้องสำเร็จ!")
        return redirect('admin_room')

    return render(request, "myapp/room/admin_room_add.html")


@login_required(login_url='login')
@user_passes_test(is_admin)
def update_member(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        member_id = request.POST.get('member_id')

        # ✅ ล้างค่าเดิมก่อน (เผื่อมีการเปลี่ยนผู้เช่า)
        previous_member = Member.objects.filter(room=room).first()
        if previous_member:
            previous_member.room = None
            previous_member.save()

        if member_id:
            tenant = get_object_or_404(Member, id=member_id)

            tenant.room = room  # ✅ ให้ Member คนใหม่ไปเช่า Room นี้
            tenant.save()

            room.status = "occupied"
        else:
            room.status = "available"

        room.save()

        messages.success(request, f"อัปเดตผู้เช่าสำเร็จ: {tenant.fullname if member_id else 'ไม่มีผู้เช่า'}")
        return redirect('admin_room')


@login_required(login_url='login')
@user_passes_test(is_admin)
def move_tenant(request):
    if request.method == "POST":
        old_room = get_object_or_404(Room, id=request.POST.get('old_room_id'))
        new_room = get_object_or_404(Room, id=request.POST.get('new_room_id'))

        if old_room.tenant:
            tenant = old_room.tenant
            tenant.room = new_room  # ✅ อัปเดต `Member.room`
            tenant.save()

            new_room.tenant = tenant
            old_room.tenant = None
            old_room.save()
            new_room.save()

            messages.success(request, "✅ ย้ายผู้เช่าสำเร็จ!")
    return redirect('admin_room')

@login_required(login_url='login')
@user_passes_test(is_admin)
def remove_member(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # ✅ ต้องลบความสัมพันธ์ที่ Member ชี้ไปยัง Room
    member = Member.objects.filter(room=room).first()
    if member:
        member.room = None
        member.save()

    room.status = "available"
    room.save()

    return redirect('admin_room')



@login_required(login_url='login')
@user_passes_test(is_admin)
def delete_room(request, room_id):
    """ ลบห้องออกจากระบบ """
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    return redirect('admin_room')

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_meter_list(request):
    """ ฟังก์ชันให้ Admin กรองข้อมูลเลขมิเตอร์ตามปี, ห้อง และเดือน """
    user = request.user
    try:
        member = Member.objects.get(user=user)
    except Member.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลผู้ใช้")
        return redirect('home')

    if member.role != 'admin':
        messages.error(request, "คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        return redirect('home')

    # ✅ ดึงค่าปี, ห้อง, และเดือนจาก GET parameter
    selected_year = request.GET.get('year', str(datetime.now().year))  # ปีปัจจุบันเป็นค่าเริ่มต้น
    selected_room = request.GET.get('room', '')  # ค่าห้อง
    selected_month = request.GET.get('month', '')  # ค่าเดือน

    # ✅ ดึงข้อมูลห้องทั้งหมด
    rooms = Room.objects.all()

    # ✅ ดึงรายการปีที่มีข้อมูล
    current_year = datetime.now().year
    years = [str(current_year)]  # ✅ ส่งแค่ปีปัจจุบัน



    # ✅ ดึงรายการเดือนที่มีข้อมูล
    months = sorted(set(y.split('-')[1] for y in ElectricityUsage.objects.values_list('month_year', flat=True).distinct()))

    # ✅ กรองข้อมูลตามปี, ห้อง และเดือนที่เลือก
    meter_records = ElectricityUsage.objects.filter(month_year__startswith=selected_year)
    if selected_room:
        meter_records = meter_records.filter(room__room_number=selected_room)
    if selected_month:
        meter_records = meter_records.filter(month_year__endswith=f"-{selected_month}")

    return render(request, "myapp/meter/admin_meter_list.html", {
        "rooms": rooms,
        "years": years,
        "months": months,
        "meter_records": meter_records,
        "selected_year": selected_year,
        "selected_room": selected_room,
        "selected_month": selected_month
    })

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_add_meter(request):
    if request.method == "POST":
        room_number = request.POST.get("room_id")
        year = request.POST.get("year")
        month = request.POST.get("month")
        current_reading = request.POST.get("current_meter_reading")

        if not (room_number and year and month and current_reading):
            messages.error(request, "กรุณากรอกข้อมูลให้ครบถ้วน")
            return redirect('admin_meter_list')

        month_year = f"{year}-{month}"

        try:
            room = Room.objects.get(room_number=room_number)

            previous_month = int(month) - 1
            previous_year = int(year)
            if previous_month == 0:
                previous_month = 12
                previous_year -= 1
            previous_month_year = f"{previous_year}-{previous_month:02d}"

            last_usage = ElectricityUsage.objects.filter(room=room, month_year=previous_month_year).first()
            previous_meter = last_usage.current_meter if last_usage else Decimal(0)

            current_reading_decimal = Decimal(current_reading)

            if current_reading_decimal < previous_meter:
                messages.error(request, "เลขมิเตอร์ใหม่ต้องมากกว่าค่าก่อนหน้า!")
                return redirect('admin_meter_list')

            if ElectricityUsage.objects.filter(room=room, month_year=month_year).exists():
                messages.error(request, f"มีข้อมูลมิเตอร์ของห้อง {room.room_number} สำหรับ {month_year} แล้ว!")
                return redirect('admin_meter_list')

            ElectricityUsage.objects.create(
                room=room,
                month_year=month_year,
                previous_meter=previous_meter,
                current_meter=current_reading_decimal,
                consumption=current_reading_decimal - previous_meter
            )

            messages.success(request, f"เพิ่มเลขมิเตอร์ห้อง {room.room_number} สำหรับ {month_year} สำเร็จแล้ว")
        except Room.DoesNotExist:
            messages.error(request, f"ไม่พบห้อง: {room_number}")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")

        return redirect('admin_meter_list')

    # ✅ เพิ่มปีไว้ใน GET เพื่อแสดงปีในฟอร์ม (ถ้าถูกเรียกแบบ GET ตรงๆ)
    current_year = datetime.now().year
    years = list(range(2023, current_year + 1))
    return render(request, 'room/admin_add_meter.html', {
        'years': years
    })



@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_edit_meter(request, meter_id):
    """ ฟังก์ชันให้ Admin แก้ไขเลขมิเตอร์ """
    
    meter = get_object_or_404(ElectricityUsage, id=meter_id)

    if request.method == "POST":
        new_reading = request.POST.get("current_meter_reading")

        meter.current_meter = Decimal(new_reading)  # ✅ แปลงเป็น Decimal
        meter.consumption = meter.current_meter - (meter.previous_meter or Decimal(0))
        meter.save()

        messages.success(request, "อัปเดตข้อมูลมิเตอร์สำเร็จ!")
        return redirect('admin_meter_list')

    return render(request, "myapp/admin_edit_meter.html", {"meter": meter})

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_delete_meter(request, meter_id):
    """ ฟังก์ชันให้ Admin ลบเลขมิเตอร์ """
    
    meter = get_object_or_404(ElectricityUsage, id=meter_id)
    meter.delete()
    messages.success(request, "ลบเลขมิเตอร์สำเร็จ!")
    return redirect('admin_meter_list')

@login_required(login_url='login')
@user_passes_test(is_admin)
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        room.description = request.POST.get("description")
        room.rent_price = request.POST.get("rent_price")
        room.electricity_price = request.POST.get("electricity_price")
        room.water_price = request.POST.get("water_price")
        room.save()
        messages.success(request, f"✅ อัปเดตรายละเอียดห้อง {room.room_number} สำเร็จ!")
        return redirect('index')

    return render(request, "edit_room.html", {"room": room})


@login_required(login_url='login')
@user_passes_test(is_admin)
def approve_payment(request, payment_id):
    try:
        payment = get_object_or_404(Payment, id=payment_id)

        if payment.status != 'approved':
            payment.status = 'approved'
            payment.save()

            # ✅ แจ้งเตือน ใช้ payment.member ได้ตรงๆ
            Notification.objects.create(
                member=payment.member,
                message=f"✅ การชำระเงินสำหรับ {payment.month_year} ได้รับการอนุมัติแล้ว"
            )

            messages.success(request, "✅ การชำระเงินได้รับการอนุมัติแล้ว")
    except Payment.DoesNotExist:
        messages.error(request, "❌ ไม่พบข้อมูลการชำระเงิน")

    return redirect('admin-payments')



@login_required(login_url='login')
def payment_page_view(request):
    user = request.user
    try:
        member = Member.objects.get(user=user)
        room = member.room
    except Member.DoesNotExist:
        messages.error(request, "ไม่พบสมาชิก")
        return redirect('rent-check')

    # ✅ รับเดือนที่เลือก
    selected_month = request.GET.get('month')
    if not selected_month:
        selected_month = ElectricityUsage.objects.filter(room=room).order_by("-month_year").values_list("month_year", flat=True).first()

    selected_usage = ElectricityUsage.objects.filter(room=room, month_year=selected_month).first()

    rent_price = room.rent_price
    electricity_price = room.electricity_price
    water_price = room.water_price
    electricity_cost = (selected_usage.consumption * electricity_price) if selected_usage else 0
    total_cost = rent_price + electricity_cost + water_price

    # ✅ ดึง Payment (แต่ **ไม่สร้าง**)
    payment = Payment.objects.filter(
        member=member,
        room=room,
        month_year=selected_month
    ).first()

    if request.method == 'POST' and 'slip' in request.FILES:
        if not payment:
            # ถ้ายังไม่มี Payment ให้สร้างตอนนี้
            payment = Payment.objects.create(
                member=member,
                room=room,
                month_year=selected_month,
                amount=total_cost,
                status='pending'
            )
        
        form = PaymentForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            payment.slip = form.cleaned_data['slip']
            payment.status = 'pending'
            payment.amount = total_cost
            payment.save()
            return redirect('payment-success')
        else:
            messages.error(request, "ไม่สามารถอัปโหลดสลิปได้ โปรดลองใหม่อีกครั้ง")
    else:
        form = PaymentForm()

    context = {
        'form': form,
        'payment': payment,
        'selected_month': selected_month,
        'total_cost': total_cost
    }

    return render(request, "myapp/payment/payment_page.html", context)

@login_required(login_url='login')
def payment_success(request):
    return render(request, "myapp/payment/payment_success.html")

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_payments_view(request):
    """ ตรวจสอบข้อมูลการชำระเงิน """
    status_filter = request.GET.get("status", "all")  # รับค่าจาก Dropdown
    if status_filter == "pending":
        payments = Payment.objects.filter(status="pending")
    elif status_filter == "approved":
        payments = Payment.objects.filter(status="approved")
    elif status_filter == "rejected":
        payments = Payment.objects.filter(status="rejected")
    else:
        payments = Payment.objects.all()  # แสดงทั้งหมด

    return render(request, "myapp/payment/admin_payments.html", {"payments": payments, "selected_status": status_filter})

@login_required(login_url='login')
@user_passes_test(is_admin)
def reject_payment(request, payment_id):
    """ ปฏิเสธการชำระเงินและแจ้งเตือนผู้ใช้ โดยไม่ลบข้อมูล """
    try:
        payment = get_object_or_404(Payment, id=payment_id)

        # ✅ เปลี่ยนสถานะเป็นไม่อนุมัติ
        payment.status = 'rejected'  # <-- สมมติว่า model มี field ชื่อ 'status'
        payment.save()

        # ✅ แจ้งเตือนสมาชิก
        Notification.objects.create(
            member=payment.member,
            message=f"❌ การชำระเงินสำหรับ {payment.month_year} ถูกปฏิเสธ โปรดตรวจสอบและอัปโหลดใหม่"
        )

        messages.success(request, "❌ การชำระเงินถูกปฏิเสธแล้ว (ข้อมูลยังเก็บไว้)")
    except Payment.DoesNotExist:
        messages.error(request, "❌ ไม่พบข้อมูลการชำระเงิน")

    return redirect('admin-payments')



@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_complaint_view(request):
    # ดึงข้อมูลคำร้องทั้งหมด
    complaints = Complaint.objects.all()

    # ตรวจสอบว่าเป็นการส่ง POST เพื่ออัปเดตสถานะหรือไม่
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        status = request.POST.get('status')

        if complaint_id and status:
            try:
                complaint = Complaint.objects.get(id=complaint_id)
                complaint.status = status
                complaint.save()
                messages.success(request, "อัปเดตสถานะคำร้องเรียนแล้ว")
            except Complaint.DoesNotExist:
                messages.error(request, "ไม่พบคำร้องเรียนที่ต้องการอัปเดต")
        else:
            messages.error(request, "ข้อมูลไม่ครบถ้วน")

    # ส่งคำร้องทั้งหมดไปยัง template
    context = {
        'complaints': complaints,
    }

    return render(request, "myapp/complaint/admin_complaint.html", context)


@login_required(login_url='login')
@user_passes_test(is_admin)
def update_complaint_status(request, complaint_id, status):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.status = status
    complaint.save()

    # ✅ เชื่อมด้วยห้อง ไม่ใช่ member ตรง
    member = Member.objects.filter(room=complaint.room).first()

    if member:
        if status == 'approved':
            # ถ้าอนุมัติ
            Notification.objects.create(
                member=member,
                message=f"✅ เรื่องร้องเรียนของห้อง {complaint.room.room_number} ได้รับการอนุมัติแล้ว",
            )
        elif status == 'rejected':
            # ถ้าไม่อนุมัติ
            Notification.objects.create(
                member=member,
                message=f"❌ เรื่องร้องเรียนของห้อง {complaint.room.room_number} ถูกปฏิเสธ โปรดติดต่อเจ้าหน้าที่",
            )


    return redirect('admin_complaint')


@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_add_lease(request, tenant_id):
    member = get_object_or_404(Member, id=tenant_id)

    if request.method == "POST":
        form = LeaseAgreementForm(request.POST, request.FILES)
        if form.is_valid():
            lease = form.save(commit=False)
            lease.member = member
            lease.room = member.room  # ✅ เพิ่มบรรทัดนี้เพื่อบอกว่าห้องไหน
            lease.save()
            return redirect('admin_add_lease_success')
    else:
        form = LeaseAgreementForm()

    return render(request, 'myapp/lease/admin_add_lease.html', {'form': form, 'member': member})

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_add_lease_success(request):
    return render(request, 'myapp/lease/admin_add_lease_success.html')


@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_manage_leases(request):
    members = Member.objects.filter(role='user')  
    leases = {lease.member.id: lease for lease in LeaseAgreement.objects.all()}  # ✅ แก้จาก tenant เป็น member

    for member in members:
        member.lease = leases.get(member.id, None)

    return render(request, 'myapp/lease/admin_manage_lease.html', {
        'members': members,
    })


@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_edit_lease(request, lease_id):
    lease = get_object_or_404(LeaseAgreement, id=lease_id)
    
    if request.method == "POST":
        form = LeaseAgreementForm(request.POST, request.FILES, instance=lease)
        if form.is_valid():
            form.save()
            return redirect('admin_add_lease_success')  # ✅ เปลี่ยนให้ redirect ได้ถูกต้อง
    else:
        form = LeaseAgreementForm(instance=lease)
    
    return render(request, 'myapp/lease/admin_edit_lease.html', {'form': form, 'lease': lease})


@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_delete_lease(request, lease_id):
    lease = get_object_or_404(LeaseAgreement, id=lease_id)
    lease.delete()
    return redirect('admin_manage_leases')

    
@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_view_lease(request):
    member = request.user.member  # ดึงข้อมูลสมาชิกของผู้ใช้ที่เข้าสู่ระบบ
    lease = LeaseAgreement.objects.filter(tenant=member).first()  # ค้นหาสัญญาเช่าของสมาชิก

    return render(request, 'myapp/user/view_lease.html', {'lease': lease, 'member': member})

@login_required(login_url='login')
def user_view_lease(request):
    member = request.user.member 
    lease = LeaseAgreement.objects.filter(member=member).first()  
    return render(request, 'myapp/lease/view_lease.html', {'lease': lease, 'member': member})



@login_required(login_url='login')
def view_news(request):
    news_list = News.objects.all().order_by("-created_at")
    notifications = Notification.objects.filter(
        member=request.user.member,
        message__startswith="📰"  
    ).order_by("-created_at")

    return render(request, 'myapp/news/view_news.html', {
        'news_list': news_list,
        'notifications': notifications  
    })


@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_manage_news(request):
    news_list = News.objects.all().order_by("-created_at")
    return render(request, 'myapp/news/admin_manage_news.html', {'news_list': news_list})

@login_required(login_url='login')
@user_passes_test(is_admin)
def add_news(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        news = News.objects.create(title=title, content=content, image=image)

        # ✅ แจ้งเตือนสมาชิกโดยใช้ `force_str` เพื่อบันทึกเป็น `utf8mb4`
        members = Member.objects.all()
        for member in members:
            Notification.objects.create(
                member=member,
                message=force_str(f"📰 ข่าวใหม่: {news.title}")
            )

        messages.success(request, "เพิ่มข่าวและแจ้งเตือนสมาชิกเรียบร้อยแล้ว!")
        return redirect('admin_manage_news')

    return render(request, 'myapp/news/admin_add_news.html')

@login_required(login_url='login')
@user_passes_test(is_admin)
def edit_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, "อัปเดตข่าวเรียบร้อยแล้ว!")
            return redirect('admin_manage_news')
    else:
        form = NewsForm(instance=news)
    return render(request, 'myapp/news/admin_edit_news.html', {'form': form})



@login_required(login_url='login')
@user_passes_test(is_admin)
def delete_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    news.delete()
    messages.success(request, "ลบข่าวสำเร็จ!")
    return redirect('admin_manage_news')

@login_required(login_url='login')
def notifications_view(request):
    member = request.user.member
    notifications = member.notifications.all().order_by('-created_at')  
    return render(request, 'myapp/notifications.html', {'notifications': notifications})


@login_required(login_url='login')
def mark_notifications_as_read(request):
    if request.method == "POST":
        print("✅ DEBUG: Marking notifications as read...")  # << เพิ่ม Debug ตรงนี้
        
        member = request.user.member
        unread_notifications = member.notifications.filter(is_read=False)
        
        print(f"🔹 DEBUG: พบ {unread_notifications.count()} รายการที่ยังไม่ได้อ่าน")  # << Debug จำนวนรายการ
        
        unread_notifications.update(is_read=True)  # ✅ อัปเดตให้เป็นอ่านแล้ว
        
        messages.success(request, "✅ ทำเครื่องหมายแจ้งเตือนทั้งหมดว่าอ่านแล้ว")
        return redirect('notifications')

    print("❌ DEBUG: ไม่ใช่ POST Request")  # Debug กรณีไม่ได้กดปุ่ม
    return redirect('notifications')

