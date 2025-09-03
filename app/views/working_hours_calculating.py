import pytz
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta, time, date
from utils.common import ResponseFormat, get_all_reporting_users
from django.utils import timezone
from django.http import JsonResponse
from app.models import CustomUser, PersonnelEmployee, IclockTransaction
from tracking.models import UserMouseTracking, EmployeeTimeSheet, IdleTimeApproval
from django.db.models import Sum
from copy import deepcopy


def format_seconds_to_hms(total_seconds):
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"


def calculate_time(data_list, email, user, req_user, re_calculate):
    previous_dict, separate_dict, Temp_list, actual_work_hours = {}, {}, [], 8.5
    for index, data in enumerate(data_list):
        current_date = data['punch_time'].strftime('%Y-%m-%d')
        if previous_dict and previous_dict != current_date:
            separate_dict[previous_dict] = Temp_list
            Temp_list = []

        Temp_list.append(data)
        previous_dict = current_date

        if index == len(data_list) - 1:
            separate_dict[previous_dict] = Temp_list
            Temp_list = []

    final_output_dict = {}
    for key, value in separate_dict.items():
        key_date = datetime.strptime(key, '%Y-%m-%d').date()
        today_date = date.today()
        if not re_calculate and (key_date != today_date):
            timesheet_data = EmployeeTimeSheet.objects.filter(user__email=email, date=key_date).values().first()
            if timesheet_data:
                final_output_dict[key] = {
                    'total_effective_hours': timesheet_data['total_effective_hours'],
                    'total_working_hours': timesheet_data['total_working_hours'],
                    'total_over_time': timesheet_data['total_over_time'],
                    'total_break_time': timesheet_data['total_break_time'],
                    'total_idle_time': timesheet_data['total_idle_time'],
                    'total_approved_idle_time': timesheet_data['total_approved_idle_time'],
                    'first_punch_in': timesheet_data['first_punch_in'],
                    'last_punch_out': timesheet_data['last_punch_out'],
                    'is_late_coming': timesheet_data['is_late_coming'],
                    'missing_punch_in': timesheet_data['missing_punch_in'],
                    'missing_punch_out': timesheet_data['missing_punch_out'],
                    'required_hours': '0'
                }
                continue

        (missing_punch_in, missing_punch_out, late_coming_status, last_punch_out, first_punch_in, total_idle_time,
         total_approved_idle_time, required_hours, temp_working_hours, effective_hours, total_diff_idle_time ) = False, False, False, '', '', 0.0, 0.0, 0, 0, '', 0.0
        try:
            try:
                idle_time_data = UserMouseTracking.objects.filter(user__email=email,
                                                                  idle_start_time__date=datetime.strptime(key, "%Y-%m-%d"))
                if idle_time_data:
                    for itd in idle_time_data:
                        total_idle_time += float(itd.idle_time)
                        approve_idle_time = IdleTimeApproval.objects.filter(ref_idle_time=itd,
                                                                            status=IdleTimeApproval.approved).values('idle_time').first()
                        if approve_idle_time:
                            total_approved_idle_time += float(approve_idle_time['idle_time'])

                if not total_idle_time: raise Exception
            except:
                total_idle_time, total_approved_idle_time = 0.0, 0.0

            if total_idle_time and total_approved_idle_time:
                total_diff_idle_time = (total_idle_time - total_approved_idle_time) * 60
            elif total_idle_time and not total_approved_idle_time:
                total_diff_idle_time = total_idle_time * 60
            else:
                total_diff_idle_time = 0.0

            if total_idle_time:
                total_idle_time = format_seconds_to_hms(total_idle_time * 60)
            else:
                total_idle_time = format_seconds_to_hms(0)

            if total_approved_idle_time:
                total_approved_idle_time = format_seconds_to_hms(total_approved_idle_time * 60)
            else:
                total_approved_idle_time = format_seconds_to_hms(0)

            if value[0]['punch_state'] != '0':
                for i in value.copy():
                    if i['punch_state'] != '0':
                        value.remove(i)
                        missing_punch_in = True
                    else:
                        break

            first_punch_in = value[0]['punch_time'].strftime("%H:%M:%S")
            if value[0]['punch_time'].time() > time(10, 0, 0):
                late_coming_status = True

            first_temp_time = value[0]['punch_time']

            temp_time, temp_state, temp_last_punch_out = '', '', ''
            for val in value[::-1]:
                if val['punch_state'] == '0':
                    temp_time = val['punch_time']
                    temp_state = val['punch_state']
                elif val['punch_state'] == '1':
                    if not temp_time and not temp_state:
                        temp_time = val['punch_time']
                        temp_state = val['punch_state']
                    else:
                        temp_last_punch_out = val['punch_time']
                    break
                else:continue

            temp_break = ''
            if temp_time and temp_last_punch_out and key_date == today_date:
                temp_break = (temp_time.replace(tzinfo=None) - temp_last_punch_out.replace(tzinfo=None)).seconds
                temp_break = str(timedelta(seconds=temp_break))

            if value[-1]['punch_state'] != '1':
                for i in value.copy()[::-1]:
                    if i['punch_state'] != '1':
                        value.remove(i)
                        missing_punch_out = True
                    else:
                        break

            if not value and temp_state == '0':
                diff_temp_time = (datetime.now() - first_temp_time.replace(tzinfo=None)).seconds
                temp_working_hours = diff_temp_time
                diffrant_hours = actual_work_hours * 3600 - diff_temp_time
                if diffrant_hours > 0:
                    required_hours = (datetime.now() + timedelta(seconds=diffrant_hours)).strftime("%H:%M:%S")
                else:
                    required_hours = 0

            last_punch_out = value[-1]['punch_time'].strftime("%H:%M:%S")

            total_hr, working_hr, break_hr = 0, 0, 0
            total_hr = (value[-1]['punch_time'] - value[0]['punch_time']).total_seconds()
            start_time, end_time = '', ''
            previous_state = None
            for index, time_data in enumerate(value):
                if time_data['punch_state'] == '0' and previous_state != 0:
                    start_time = time_data['punch_time']
                    current_state = 0
                elif time_data['punch_state'] == '1':
                    try:
                        if value[index + 1]['punch_state'] == '1':
                            continue
                    except:
                        pass

                    end_time = time_data['punch_time']
                    current_state = 1
                else:
                    continue

                if start_time and end_time:
                    working_hr += (end_time - start_time).total_seconds()
                    start_time, end_time = '', ''

                previous_state = current_state

                if key_date == today_date and index == len(value)-1:
                    if temp_state == '0':
                        diff_temp_time = (datetime.now() - temp_time.replace(tzinfo=None)).seconds
                        temp_working_hours = diff_temp_time
                        diffrant_hours = actual_work_hours * 3600 - (working_hr + diff_temp_time)
                    else:
                        diffrant_hours = actual_work_hours * 3600 - working_hr

                    if diffrant_hours > 0:
                        required_hours = (datetime.now() + timedelta(seconds=diffrant_hours)).strftime("%H:%M:%S")
                    else:
                        required_hours = 0

            effective_hours = int(working_hr - total_diff_idle_time + temp_working_hours)
            if effective_hours <= 0:
                effective_hours = 0

            if effective_hours - (actual_work_hours * 3600) > 0:
                overtime_hr = effective_hours - (actual_work_hours * 3600)
                overtime_hr = str(timedelta(seconds=overtime_hr))
            else:
                overtime_hr = '00:00:00'

            final_output_dict[key] = {
                'total_effective_hours': format_seconds_to_hms(effective_hours),
                'total_working_hours': format_seconds_to_hms(working_hr),
                'temp_working_hours': format_seconds_to_hms(temp_working_hours),
                'total_over_time': overtime_hr,
                'total_break_time': str(timedelta(seconds=(total_hr - working_hr))),
                'temp_break': temp_break,
                'total_idle_time': str(total_idle_time),
                'total_approved_idle_time': str(total_approved_idle_time),
                'first_punch_in': first_punch_in,
                'last_punch_out': last_punch_out,
                'is_late_coming': late_coming_status,
                'missing_punch_in': missing_punch_in,
                'missing_punch_out': missing_punch_out,
                'required_hours': str(required_hours),
                    }

        except Exception as e:
            if total_diff_idle_time:total_effective_hours = temp_working_hours - total_diff_idle_time
            else:total_effective_hours = temp_working_hours

            final_output_dict[key] = {
                'total_effective_hours': format_seconds_to_hms(total_effective_hours),
                'total_working_hours': '00:00:00',
                'temp_working_hours': format_seconds_to_hms(temp_working_hours),
                'total_over_time': '00:00:00',
                'total_break_time': '00:00:00',
                'temp_break': '00:00:00',
                'total_idle_time': str(total_idle_time),
                'total_approved_idle_time': str(total_approved_idle_time),
                'first_punch_in': first_punch_in,
                'last_punch_out': last_punch_out,
                'is_late_coming': late_coming_status,
                'missing_punch_in': missing_punch_in,
                'missing_punch_out': missing_punch_out,
                'required_hours': str(required_hours),
            }

        timesheet_user = CustomUser.objects.get(email=user.email)

        try:
            insert_dic = deepcopy(final_output_dict[key])
            insert_dic.pop('required_hours')
            insert_dic.pop('temp_break')
            insert_dic.pop('temp_working_hours')
            obj, created = EmployeeTimeSheet.objects.update_or_create(
                user=timesheet_user,
                date=key_date,
                defaults={**insert_dic, 'updated_by': req_user}
            )
            if created:
                obj.created_by = req_user
                obj.save()
        except Exception as E:
            print(E)

    final_total_effective_hours = sum(
        timedelta(
            hours=int(day['total_effective_hours'].split(':')[0]),
            minutes=int(day['total_effective_hours'].split(':')[1]),
            seconds=int(day['total_effective_hours'].split(':')[2])
        ).total_seconds()
        for day in final_output_dict.values() if ':' in day['total_effective_hours']
    )

    final_total_working_hours = sum(
        timedelta(
            hours=int(day['total_working_hours'].split(':')[0]),
            minutes=int(day['total_working_hours'].split(':')[1]),
            seconds=int(day['total_working_hours'].split(':')[2])
        ).total_seconds()
        for day in final_output_dict.values() if day['total_working_hours']
    )

    final_total_overtime = sum(
        timedelta(
            hours=int(day['total_over_time'].split(':')[0]),
            minutes=int(day['total_over_time'].split(':')[1]),
            seconds=int(day['total_over_time'].split(':')[2])
        ).total_seconds()
        for day in final_output_dict.values() if day['total_over_time']
    )

    final_total_break_time = sum(
        timedelta(
            hours=int(day['total_break_time'].split(':')[0]),
            minutes=int(day['total_break_time'].split(':')[1]),
            seconds=int(day['total_break_time'].split(':')[2])
        ).total_seconds()
        for day in final_output_dict.values() if day['total_break_time']
    )

    final_total_idle_time = str(sum(
        timedelta(
            hours=int(day['total_idle_time'].split(':')[0]),
            minutes=int(day['total_idle_time'].split(':')[1]),
            seconds=int(day['total_idle_time'].split(':')[2])
        ).total_seconds()
        for day in final_output_dict.values() if day['total_idle_time']
    ))

    # final_total_idle_time = str(round(sum(float(sit['total_idle_time']) for sit in final_output_dict.values() if sit['total_idle_time']), 2))

    # final_total_required_hours = float(len(final_output_dict) * 8.5 * 3600) - float(final_total_working_hours)
    final_total_required_hours = float(len(final_output_dict) * 8.5 * 3600) - float(final_total_effective_hours)
    if final_total_required_hours <= 0.0:
        final_total_required_hours = 0.0

    final_dict = {}
    final_dict['final_total_effective_hours'] = format_seconds_to_hms(final_total_effective_hours)
    final_dict['final_total_working_hours'] = format_seconds_to_hms(final_total_working_hours)
    final_dict['final_total_required_hours'] = format_seconds_to_hms(final_total_required_hours)
    final_dict['final_total_overtime'] = format_seconds_to_hms(final_total_overtime)
    final_dict['final_total_break_time'] = format_seconds_to_hms(final_total_break_time)
    final_dict['final_total_idle_time'] = format_seconds_to_hms(float(final_total_idle_time))
    final_dict['data'] = final_output_dict

    return final_dict


def calculate_work_hours(start_date, end_date, email,base_permissions ,team, req_user, re_calculate):
    end_date = end_date + timedelta(days=1)
    current_user_mail = req_user.email
    user = None
    if 'all' in base_permissions:
        user = CustomUser.objects.filter(email=email).first()
    elif 'team' in base_permissions:
        if email in team:
            user = CustomUser.objects.filter(email=email).first()
    elif 'owned' in base_permissions:
        if current_user_mail == email:
            user = CustomUser.objects.filter(email=email).first()

    if not user:
        response = 'You do not have access!'
        return response

    employee_id = int(str(user.employee_id).replace('QB', ''))

    if not employee_id:
        raise ValueError('employee id not found!')

    zkteco_user = PersonnelEmployee.objects.using('zkteco').get(emp_code=employee_id)
    if not zkteco_user:
        raise ValueError('zkteco user not found!')

    IclockTransaction_use = list(IclockTransaction.objects.using('zkteco').filter(
        emp=zkteco_user,
        # punch_time__range=[start_date, end_date]
        punch_time__gte=start_date,
        punch_time__lte=end_date,
    ).values('emp_code', 'emp__first_name', 'punch_time', 'punch_state'))

    if not IclockTransaction_use:
        raise ValueError('punch transaction not found!')

    try:
        final_time = calculate_time(IclockTransaction_use, email, user, req_user, re_calculate)
    except Exception as e:
        raise ValueError(e)

    if not final_time:
        raise ValueError('final_time is None!')

    return final_time


class WorkingHoursCalculating(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        re_calculate = bool(request.GET.get('re_calculate', False))
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        email = request.GET.get('email', None)
        if email and start_date and end_date:
            email_user = CustomUser.objects.filter(email=email).first()
            first_name = email_user.first_name
            last_name = email_user.last_name
            try:
                start_date = timezone.make_aware(datetime.strptime(start_date, "%d/%m/%Y"), timezone=pytz.UTC)
                end_date = timezone.make_aware(datetime.strptime(end_date, "%d/%m/%Y"), timezone=pytz.UTC)
            except:
                self.response_format['error'] = 'wrong date format, valid format is DD/MM/YYYY'
                self.response_format['status'] = False
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            error, final_time, flag, res_status = '', [], True, status.HTTP_200_OK
            try:
                permissions = request.user.groups.all().first().permissions.filter(
                    content_type__model='customuser').values_list('codename', flat=True)
                base_permissions = [permission.split('_')[0] for permission in permissions]
                # team = request.user.subordinates.values_list('email', flat=True)
                team = get_all_reporting_users(request.user)
                team = [i.email for i in team]
                final_time = calculate_work_hours(start_date, end_date, email, base_permissions, team, request.user, re_calculate)
            except Exception as e:
                error = str(e)
                flag = False
                res_status = status.HTTP_400_BAD_REQUEST

            self.response_format['error'] = error
            self.response_format['status'] = flag
            self.response_format['data'] = final_time
            self.response_format['user'] = {'first_name':first_name,'last_name':last_name}
            return Response(self.response_format, status=res_status)















