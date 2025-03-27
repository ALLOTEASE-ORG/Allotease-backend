from django.db import models


# This is the folder where profile images are stored
def upload_location(instance, filename):
    file_path = "profile_image/{user_id}/{image}".format(
        user_id=str(instance.id), image=filename
    )
    return file_path


