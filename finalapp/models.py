from django.db import models
from django.contrib.auth.models import User
import json

# ตาราง Members
class Member(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="member")
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default_profile.png', blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    fullname = models.CharField(max_length=50, blank=True, null=True)  
    address = models.TextField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True, default=None)
    sex = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    room = models.OneToOneField('Room', on_delete=models.SET_NULL, null=True, blank=True, related_name="member")


    def __str__(self):
        return self.fullname
    
    def is_admin(self):
        return self.role == 'admin'
    
    def get_facilities_list(self):
        return [f.strip() for f in self.facilities.split(',') if f.strip()]

# ตาราง Rooms
class Room(models.Model):
    ROOM_TYPES = [
        ('standard', 'Standard'),
        ('deluxe', 'Deluxe'),
        ('suite', 'Suite'),
    ]

    STATUS_CHOICES = [
        ('available', 'ว่าง'),
        ('occupied', 'ไม่ว่าง'),
        ('reserved', 'ติดจอง'),
    ]

    room_number = models.CharField(max_length=10, unique=True)  # หมายเลขห้อง
    room_type = models.CharField(max_length=50, choices=[("Standard", "Standard"), ("Deluxe", "Deluxe")])
    size = models.FloatField(help_text="ขนาดห้อง (ตร.ม.)")  # ขนาดห้อง
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)  # รูปภาพห้อง
    rent_price = models.DecimalField(max_digits=8, decimal_places=2)  # ค่าเช่าต่อเดือน
    electricity_price = models.DecimalField(max_digits=8, decimal_places=2)  # ราคาค่าไฟต่อหน่วย
    water_price = models.DecimalField(max_digits=8, decimal_places=2)  # ราคาค่าน้ำต่อหน่วย
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')  # สถานะห้อง
    facilities = models.TextField(blank=True, default='[]')
    
    
    def __str__(self):
        return f"Room {self.room_number} - {self.get_room_type_display()} - {self.get_status_display()}"

    def get_facilities_list(self):
        """ ดึง facilities เป็น list """
        try:
            return json.loads(self.facilities)
        except json.JSONDecodeError:
            return []
        
# ตาราง Rentals
class Rental(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="rentals")
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name="rentals")
    meter_reading = models.DecimalField(max_digits=10, decimal_places=2)
    total_bill = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.room} - {self.month}"

# ตาราง Electricity Usage
class ElectricityUsage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    month_year = models.CharField(max_length=7)  # ฟิลด์นี้อาจเป็น CharField
    previous_meter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_meter = models.DecimalField(max_digits=10, decimal_places=2)
    consumption = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.previous_meter is not None:
            self.consumption = self.current_meter - self.previous_meter  # คำนวณหน่วยไฟ
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.room} - {self.month_year} - {self.consumption} kWh"


# ตาราง Complaints
class Complaint(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Complaint {self.id} - {self.room.room_number}"

# ตาราง Lease Agreements (ใหม่)
class LeaseAgreement(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name="lease_agreement")  
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name="lease_agreement")
    file = models.FileField(upload_to='lease_agreements/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lease Agreement - {self.member.fullname} - {self.room.room_number}"


# ตาราง Payment (ใหม่)
class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="payments")
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name="payments")
    month_year = models.CharField(max_length=7)  # (YYYY-MM)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    slip = models.ImageField(upload_to="payment_slips/", blank=True, null=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('member', 'room', 'month_year')  # ป้องกันซ้ำสำหรับการชำระเดือนเดียวกัน

    def __str__(self):
        return f"Payment {self.member.fullname} - {self.room.room_number} - {self.month_year} - {self.status}"



class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Notification(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # ตรวจสอบว่าอ่านแล้วหรือยัง

    def __str__(self):
        return f"Notification for {self.member.fullname}: {self.message}"
