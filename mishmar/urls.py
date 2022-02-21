from django.contrib import admin
from django.urls import path
from . import views
from .views import ArmingAllMonthView, ArmingPersonalMonthView, EventCreateView, EventListView, EventUpdateView, GunListView, IpBanListView, OrganizationDetailView, PostCreateView, PostListView, PostUpdateView, ShifttableView, ValidationLogMonthView, data_usage_view, delete_events_data_view, delete_logs_data_view, delete_organization_data_view, organization_shift_view, staff_panel_view
from .views import ServedSumListView, ServedSumShiftDetailView, ServedSumReinforcementsDetailView
from .views import OrganizationSuggestionView, OrganizationCreateView, OrganizationListView
from .views import organization_update
from .views import ArmingDayView, ArmingLogUpdate, ArmingCreateView, Validation_Log_Signature, ArmingRequestView, ArmingRequestDetailView, ArmingRequestListView

urlpatterns = [
    path("", views.home, name="Home"),
    path("serve/", views.shift_view, name="Serve"),
    path("organization/", OrganizationListView.as_view(), name="Organization"),
    path("serve/sum", ServedSumListView.as_view(), name="Served-sum"),
    path("settings/", views.settings_view, name="Settings"),
    path("organization/<int:pk>/update", organization_update, name="organization-update"),
    path("shift/<int:pk>/update", views.shift_update_view, name="shift-update"),
    path('organization/<int:pk>/', OrganizationDetailView.as_view(), name='organization-detail'),
    path('serve/sum/shift/<int:pk>/', ServedSumShiftDetailView.as_view(), name='served-sum-shift'),
    path('serve/sum/reinforcement/<int:pk>/', ServedSumReinforcementsDetailView.as_view(), name='served-sum-reinforcement'),
    path('organization/table/shift/<int:pk>/', ShifttableView.as_view(), name='organization-table-shift'),
    path("organization/<int:pk>/suggestion", OrganizationSuggestionView.as_view(), name="organization-suggestion"),
    path("organization/new", OrganizationCreateView.as_view(), name="organization-new"),
    path('<int:year>/<str:month>/<int:day>/', ArmingDayView.as_view(), name="armingday"),
    path('<int:year>/<str:month>/',  ArmingPersonalMonthView.as_view(), name="armingmonth"),
    path('<int:year>/<str:month>/all',  ArmingAllMonthView.as_view(), name="armingmonth-all"),
    path('signature/<int:pk>/',  ArmingLogUpdate.as_view(), name="signature"),
    path('ArmingLog/new/',  ArmingCreateView.as_view(), name="arming-new"),
    path('validation/signature', Validation_Log_Signature, name="validation-signature"),
    path('arminglog/changerequest/new', ArmingRequestView.as_view(), name="arming-changerequest"),
    path('arminglog/request/<int:pk>/', ArmingRequestDetailView.as_view(), name="arming-request"),
    path('arminglog/requests/', ArmingRequestListView.as_view(), name="arming-requests-list"),
    path('staff/panel/', staff_panel_view, name="staff-panel"),
    path('organization/design/', organization_shift_view, name="organization-design"),
    path('post/new', PostCreateView.as_view(), name="post-new"),
    path('post/update/<int:pk>/', PostUpdateView.as_view(), name="post-update"),
    path('posts/', PostListView.as_view(), name="post-list"),
    path('event/new', EventCreateView.as_view(), name="event-new"),
    path('event/update/<int:pk>/', EventUpdateView.as_view(), name="event-update"),
    path('event/list', EventListView.as_view(), name="event-list"),
    path('ip/ban/list', IpBanListView.as_view(), name="ipban-list"),
    path('data/usage/', data_usage_view, name="data-usage"),
    path('data/organizations/delete', delete_organization_data_view, name="delete-organization-data"),
    path('data/logs/delete', delete_logs_data_view, name="delete-logs-data"),
    path('data/events/delete', delete_events_data_view, name="delete-events-data"),
    path('gun/list', GunListView.as_view(), name="gun-list"),
    path('<int:year>/<str:month>/validation/', ValidationLogMonthView.as_view(), name="validation-month"),
]
