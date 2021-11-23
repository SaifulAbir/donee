from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api import DashboardDonorsAPIView, NgoUserCreateAPIView, NgoUserListAPIView, NgoUserRoleUpdateAPIView, NgoUserUpdateStatusAPIView, RoleListAPIView, UserUpdateAPIView, DoneeAndNgoProfileCreateAPIView, DoneeAndNgoProfileUpdateAPIView, CountryListAPI, \
    CustomTokenObtainPairView, DonorProfileAPIView, DoneeAndNGOProfileAPIView, UserFollowUserAPI, UserFollowProfileAPI, \
    SendInvitationLink, DashboardAppAPIView, inNgoDoneeInfoAPIView, inNgoDoneeListAPIView, DoneeStatusUpdateAPIView, \
    EndorsedGoalsInNgoAPIView, SocialSignupAPIView, UserSearchAPIView, DashboardMyWalletAPIView
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-user/', csrf_exempt(UserRegApi.as_view())),
    path('update-user/', UserUpdateAPIView.as_view()),
    path('user-detail/', UserUpdateAPIView.as_view()),
    path('donor-profile/<int:pk>/', DonorProfileAPIView.as_view()),
    path('donee-ngo-profile/<int:pk>/', DoneeAndNGOProfileAPIView.as_view()),
    path('create-profile/', DoneeAndNgoProfileCreateAPIView.as_view()),
    path('update-profile/', DoneeAndNgoProfileUpdateAPIView.as_view()),
    path('profile-detail/', DoneeAndNgoProfileUpdateAPIView.as_view()),
    path('country-list/', CountryListAPI.as_view()),
    path('verify-invitation/<str:invitation>',VerifyInvitationView.as_view()),
    path('user-follow/', UserFollowUserAPI.as_view()),
    path('profile-follow/', UserFollowProfileAPI.as_view()),
    path('dashboard/donee-count/', inNgoDoneeInfoAPIView.as_view()),
    path('dashboard/donee-list/', inNgoDoneeListAPIView.as_view()),
    path('donee-status/', DoneeStatusUpdateAPIView.as_view()),
    path('send-invitation-link/', SendInvitationLink.as_view()),
    path('dashboard/app/', DashboardAppAPIView.as_view()),
    path('ngo-endorsed-goals/', EndorsedGoalsInNgoAPIView.as_view()),
    path('social-signup/', SocialSignupAPIView.as_view()),
    path('search-user/', UserSearchAPIView.as_view()),
    path('role-list/',RoleListAPIView.as_view()),
    path('ngo-user-create/',NgoUserCreateAPIView.as_view()),
    path('ngo-user-list/',NgoUserListAPIView.as_view()),
    path('ngo-user-role-update/<int:pk>/',NgoUserRoleUpdateAPIView.as_view()),
    path('ngo-user-status-update/<int:pk>/', NgoUserUpdateStatusAPIView.as_view()),
    path('dashboard/my-wallet/', DashboardMyWalletAPIView.as_view()),
    path('dashboard/donors/',DashboardDonorsAPIView.as_view()),

]

