from rest_framework.throttling import UserRateThrottle

# Here lay the throttle/rate limit policy for the API views
# Those can be considered at the moment like global throttle policy to use
class AdminRateThrottle(UserRateThrottle):
    scope = 'admin'
    
    def allow_request(self, request, view):
        # exclude non-authenticated users and regular users from this throttle
        if not request.user.is_authenticated or not request.user.is_staff:  
            return True

        # only applies if user is admin
        if request.user.is_staff:
            self.scope = 'admin'
        # else:
        #     self.scope = 'user'
        return super().allow_request(request, view)


class UserBurstThrottle(UserRateThrottle):
    """Burst protection - short-term rate limiting"""
    scope = 'user_burst'
    
    def allow_request(self, request, view):
        # Only apply to regular users, not admins
        if not request.user.is_authenticated or request.user.is_staff:
            return True
        return super().allow_request(request, view)


class UserSustainThrottle(UserRateThrottle):
    """Burst protection - short-term rate limiting"""
    scope = 'user_sustain'
    
    def allow_request(self, request, view):
        # Only apply to regular users, not admins
        if not request.user.is_authenticated or request.user.is_staff:
            return True
        return super().allow_request(request, view)


class UserDayThrottle(UserRateThrottle):
    """Burst protection - short-term rate limiting"""
    scope = 'user_day'
    
    def allow_request(self, request, view):
        # Only apply to regular users, not admins
        if not request.user.is_authenticated or request.user.is_staff:
            return True
        return super().allow_request(request, view)