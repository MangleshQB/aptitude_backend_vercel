# from app.models import CustomUser
# import requests
#
# def update_log():
#     emails = list(CustomUser.objects.values_list('email', flat=True))
#     start_date = '01/11/2024'
#     end_date = '12/12/2024'
#     for email in emails:
#         if 'admin@gmail.com' in email:continue
#         print(email)
#         try:
#             headers = {
#                 'Accept': 'application/json, text/plain, */*',
#                 'Accept-Language': 'en-US,en;q=0.9',
#                 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkZW50aWZpZXIiOiJhZG1pbiIsImV4cCI6MTczNDg0OTYwMywiaWF0IjoxNzMzOTg1NjAzLjc4MDkzNywicHJvZmlsZV9wayI6MSwiZW1haWwiOiJhZG1pbkBnbWFpbC5jb20iLCJwaG9uZV9udW1iZXIiOm51bGwsInVzZXJuYW1lIjoiYWRtaW4ifQ.Jvy2NfkG-v4zGCPypOmabqXTuUFingpkcbZEKDakCaI',
#                 'Connection': 'keep-alive',
#                 'Origin': 'http://192.168.1.106:3000',
#                 'Referer': 'http://192.168.1.106:3000/',
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
#             }
#
#             response = requests.get(
#                 f'http://192.168.1.73:8000/api/working_hours/?start_date={start_date}&end_date={end_date}&email={email}&re_calculate=true',
#                 headers=headers,
#                 verify=False,
#             )
#             print(response.status_code)
#         except Exception as e:
#             print(e)
#             continue
#
#
# if __name__ == '__main__':
#     update_log()