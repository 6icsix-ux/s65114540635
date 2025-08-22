from .models import Member

def user_member(request):
    if request.user.is_authenticated:
        try:
            member = Member.objects.get(user=request.user)
        except Member.DoesNotExist:
            member = None
    else:
        member = None
    return {"member": member}
