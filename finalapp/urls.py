from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('admin-register/', views.admin_register, name='admin_register'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # 📌 Payment / Rent / Meter
    path('payment/', views.payment_page_view, name='payment'),
    path('payment/<str:month>/', views.payment_page_view, name='payment_with_month'),
    path('payment-success/', views.payment_success, name='payment-success'),
    path('rent-check/', views.rent_check_view, name='rent-check'),
    path('electricity-usage/', views.electricity_usage_view, name='electricity_usage'),

    # 📌 Complaint
    path('complaint/', views.complaint_view, name='complaint'),
    path('complaint_success/', views.complaint_success, name='complaint_success'),

    # 📌 Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),

    # 📌 Admin Dashboard
    path('manage/home/', views.admin_home, name='admin_home'),
    path('manage/rooms/', views.admin_room, name='admin_room'),
    path('manage/rooms/add/', views.add_room, name='admin_room_add'),
    path('manage/rooms/update_tenant/<int:room_id>/', views.update_member, name='update_member'),
    path('manage/rooms/move_tenant/', views.move_tenant, name='move_tenant'),
    path('manage/rooms/remove_tenant/<int:room_id>/', views.remove_member, name='remove_member'),
    path('manage/rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),

    path('manage/users/', views.admin_user_list, name='admin_user_list'),
    path('manage/users/add/', views.add_user, name='add_user'),
    path('manage/users/edit/', views.edit_user, name='edit_user'),
    path('manage/users/change-role/<int:user_id>/<str:new_role>/', views.change_user_role, name='change_user_role'),
    path('manage/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('manage/get-user-profile/<int:user_id>/', views.get_user_profile, name='get_user_profile'),

    # 📌 Meter
    path("manage/meter-list/", views.admin_meter_list, name="admin_meter_list"),
    path("manage/add-meter/", views.admin_add_meter, name="admin_add_meter"),
    path("manage/edit-meter/<int:meter_id>/", views.admin_edit_meter, name="admin_edit_meter"),
    path("manage/delete-meter/<int:meter_id>/", views.admin_delete_meter, name="admin_delete_meter"),

    path('manage/edit-room/<int:room_id>/', views.edit_room, name='edit_room'),

    # 📌 Payments
    path('manage/payments/', views.admin_payments_view, name='admin-payments'),
    path('manage/payment/<int:payment_id>/approve/', views.approve_payment, name='approve-payment'),
    path('manage/payment/<int:payment_id>/reject/', views.reject_payment, name='reject-payment'),

    # 📌 Complaints
    path('manage/complaints/', views.admin_complaint_view, name='admin_complaint'),
    path('manage/complaint/update/<int:complaint_id>/<str:status>/', views.update_complaint_status, name='update_complaint_status'),

    # 📌 Lease
    path('manage/leases/', views.admin_manage_leases, name='admin_manage_leases'),
    path('manage/leases/add/<int:tenant_id>/', views.admin_add_lease, name='admin_add_lease'),
    path('manage/leases/add/success/', views.admin_add_lease_success, name='admin_add_lease_success'),
    path('manage/leases/edit/<int:lease_id>/', views.admin_edit_lease, name='admin_edit_lease'),
    path('manage/leases/delete/<int:lease_id>/', views.admin_delete_lease, name='admin_delete_lease'),
    path('manage/leases/view/<int:lease_id>/', views.admin_view_lease, name='view_lease'),
    path('lease/', views.user_view_lease, name='user_view_lease'),

    # 📌 News
    path('news/', views.view_news, name='view_news'),
    path('manage/news/', views.admin_manage_news, name='admin_manage_news'),
    path('manage/news/add/', views.add_news, name='admin_add_news'),
    path('manage/news/edit/<int:news_id>/', views.edit_news, name='admin_edit_news'),
    path('manage/news/delete/<int:news_id>/', views.delete_news, name='delete_news'),

    # 📌 Check duplication
    path('check_email/', views.check_email, name='check_email'),
    path('check_phone/', views.check_phone, name='check_phone'),
]
