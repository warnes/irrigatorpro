###
# Some utility functions to control handling of authorized users in the forms
# and fields page.
#
###

from farms.models import Farm, InvitedUser

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

import re

class AuthUserException(Exception): pass
    

###
## Update the list of authorized users for the given farm.
## For each added user we first check if there is a user with this email.
## If not use an invited user, or create an invitation.
## 

def update_authorized_users(farm_pk, added_users, deleted_existing_users, deleted_invited_users):

    farm = Farm.objects.get(pk = farm_pk)
    add_users(farm, added_users)
#    delete_existing_users(farm, deleted_existing_users)
#    delete_invited_users(farm, deleted_invited_users)


###
## Add users. Only have emails. 
def add_users(farm, added_users):
    
    for u in added_users:
        email = extract_email(u)
        try:
            user = User.objects.get(email = email)
            farm.users.add(user)

        except ObjectDoesNotExist:
            try:
                invited_user = InvitedUser.objects.get(email=email)
            except ObjectDoesNotExist:
                invited_user = InvitedUser(email=email)
                ## TODO Add invitation

            invited_user.save()
            invited_user.farms.add(farm)
            invited_user.save()


##
## Extract user email from string generated from user info.
## It is the maximal sequence on each side of the '@' sign 
## that contains only alpha-numerics and and the '.' 

def extract_email(user_info):
    u = str(user_info)
    if u.count('@') != 1: raise AuthUserException()

    ## TODO Make prog a static, compiling it only once.
    prog = re.compile("[\w.]+@[\w.]+\.\w+")
    result = prog.search(u)
    
    if result is None: raise AuthUserException()
    return result.group(0)

    
    
    
    
    

    

