from pydantic import BaseModel, Field
from enum import StrEnum

class Notification_Pref(StrEnum):
    email='email'
    sms='sms'
    call='call'
    push_notification='push notification'


class Preference(BaseModel):
    notification_pref: Notification_Pref = Field(default=Notification_Pref.email,
                                            description='This is used to determine how to notify the account user')