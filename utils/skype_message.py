from skpy import Skype, SkypeGroupChat
from django.conf import settings
def list_skype_contacts():
    try:
        skype = Skype(settings.SKYPE_USERNAME, settings.SKYPE_PASSWORD)

        print("Your Skype Contacts:")
        contacts = skype.contacts

        for contact in contacts:
            contact_id = contact.id
            contact_name = contact.name
            print(f"ID: {contact_id}, Name: {contact_name}")

        print("Your Skype Group Chats:")
        for chat_id, chat in skype.chats.recent().items():
            if isinstance(chat, SkypeGroupChat):
                print(f"Group ID: {chat_id}, Topic: {chat.topic or 'No Topic'}")
    except Exception as e:
        print(f"Failed to retrieve contacts: {e}")

def send_skype_message(recipient_ids=[], message=''):
    try:
        skype = Skype(settings.SKYPE_USERNAME, settings.SKYPE_PASSWORD)
        for ID in recipient_ids:

            if '@thread.skype' in ID:
                group_chat = skype.chats[ID]
                group_chat.sendMsg(message)
            else:
                chat = skype.contacts[ID].chat
                chat.sendMsg(message)

            print(f"Message sent to {ID}: {message}")
    except Exception as e:
        print(f"Failed to send message: {e}")

# Usage
if __name__ == "__main__":

    message = "Hello! The task has been successfully completed."

    # TODO Get Skype ID
    # recipient_skype_id = list_skype_contacts(skype_username, skype_password)

    recipient_skype_ids = ['19:5de2489a5bf14aa496f339212423c955@thread.skype']
    send_skype_message(recipient_skype_ids, message)

#utils.skype_message.list_skype_contacts