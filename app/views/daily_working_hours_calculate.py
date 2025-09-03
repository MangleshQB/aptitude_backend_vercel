from datetime import datetime, timedelta, time, date
from django.utils import timezone
import pytz
from app.models import CustomUser, PersonnelEmployee, IclockTransaction
from tracking.models import UserMouseTracking, EmployeeTimeSheet, IdleTimeApproval
from django.db.models import Sum
from copy import deepcopy


def format_seconds_to_hms(total_seconds):
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"


def calculate_time(data_list, user):
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

        if key_date != today_date:
            timesheet_data = EmployeeTimeSheet.objects.filter(date=key_date).values().first()
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
                }
                continue

        (missing_punch_in, missing_punch_out, late_coming_status, last_punch_out, first_punch_in, total_idle_time,
         total_approved_idle_time, effective_hours) = False, False, False, '', '', 0.0, 0.0, ''
        try:
            try:
                idle_time_data = UserMouseTracking.objects.filter(user__email=user.email,
                                                                  created_at__date=datetime.strptime(key, "%Y-%m-%d"))
                if idle_time_data:
                    for itd in idle_time_data:
                        total_idle_time += float(itd.idle_time)
                        approve_idle_time = IdleTimeApproval.objects.filter(ref_idle_time=itd,
                                                                            status=IdleTimeApproval.approved).values(
                            'idle_time').first()
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

            if value[-1]['punch_state'] != '1':
                for i in value.copy()[::-1]:
                    if i['punch_state'] != '1':
                        value.remove(i)
                        missing_punch_out = True
                    else:
                        break

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


            effective_hours = int(working_hr - total_diff_idle_time)
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
                'total_over_time': overtime_hr,
                'total_break_time': str(timedelta(seconds=(total_hr - working_hr))),
                'total_idle_time': str(total_idle_time),
                'total_approved_idle_time': str(total_approved_idle_time),
                'first_punch_in': first_punch_in,
                'last_punch_out': last_punch_out,
                'is_late_coming': late_coming_status,
                'missing_punch_in': missing_punch_in,
                'missing_punch_out': missing_punch_out,
            }

        except Exception as e:
            final_output_dict[key] = {
                'total_effective_hours': '00:00:00',
                'total_working_hours': '00:00:00',
                'total_over_time': '00:00:00',
                'total_break_time': '00:00:00',
                'total_idle_time': str(total_idle_time),
                'total_approved_idle_time': str(total_approved_idle_time),
                'first_punch_in': first_punch_in,
                'last_punch_out': last_punch_out,
                'is_late_coming': late_coming_status,
                'missing_punch_in': missing_punch_in,
                'missing_punch_out': missing_punch_out,
            }

        timesheet_user = CustomUser.objects.get(email=user.email)

        obj, created = EmployeeTimeSheet.objects.update_or_create(
            user=timesheet_user,
            date=key_date,
            defaults={**final_output_dict[key], 'updated_by': user}
        )
        if created:
            obj.created_by = user
            obj.save()

    # final_total_working_hours = sum(
    #     timedelta(
    #         hours=int(day['total_working_hours'].split(':')[0]),
    #         minutes=int(day['total_working_hours'].split(':')[1]),
    #         seconds=int(day['total_working_hours'].split(':')[2])
    #     ).total_seconds()
    #     for day in final_output_dict.values() if day['total_working_hours']
    # )
    #
    # final_total_overtime = sum(
    #     timedelta(
    #         hours=int(day['total_over_time'].split(':')[0]),
    #         minutes=int(day['total_over_time'].split(':')[1]),
    #         seconds=int(day['total_over_time'].split(':')[2])
    #     ).total_seconds()
    #     for day in final_output_dict.values() if day['total_over_time']
    # )
    #
    # final_total_break_time = sum(
    #     timedelta(
    #         hours=int(day['total_break_time'].split(':')[0]),
    #         minutes=int(day['total_break_time'].split(':')[1]),
    #         seconds=int(day['total_break_time'].split(':')[2])
    #     ).total_seconds()
    #     for day in final_output_dict.values() if day['total_break_time']
    # )
    #
    # final_total_idle_time = str(sum(
    #     timedelta(
    #         hours=int(day['total_idle_time'].split(':')[0]),
    #         minutes=int(day['total_idle_time'].split(':')[1]),
    #         seconds=int(day['total_idle_time'].split(':')[2])
    #     ).total_seconds()
    #     for day in final_output_dict.values() if day['total_idle_time']
    # ))
    #
    # final_dict = {}
    # final_dict['final_total_working_hours'] = format_seconds_to_hms(final_total_working_hours)
    # final_dict['final_total_overtime'] = format_seconds_to_hms(final_total_overtime)
    # final_dict['final_total_break_time'] = format_seconds_to_hms(final_total_break_time)
    # final_dict['final_total_idle_time'] = format_seconds_to_hms(float(final_total_idle_time))
    # final_dict['data'] = final_output_dict
    #
    # return final_dict


def calculate_work_hours():
    all_user = CustomUser.objects.all()

    today_date = datetime.strptime(datetime.today().date().strftime("%d/%m/%Y"), "%d/%m/%Y")
    today_date = timezone.make_aware(today_date, timezone=pytz.UTC)

    for user in all_user:
        try:
            employee_id = int(str(user.employee_id).replace('QB', ''))
            if not employee_id: raise Exception
        except Exception as e:
            continue

        try:
            zkteco_user = PersonnelEmployee.objects.using('zkteco').get(emp_code=employee_id)
            if not zkteco_user:
                raise Exception
        except Exception as e:
            continue

        try:
            IclockTransaction_use = list(IclockTransaction.objects.using('zkteco').filter(
                emp=zkteco_user,
                punch_time__gte=today_date,
                punch_time__lte=today_date + timedelta(days=1),
            ).values('emp_code', 'emp__first_name', 'punch_time', 'punch_state'))
            if not IclockTransaction_use: raise Exception
        except Exception as e:
            continue

        try:
            calculate_time(IclockTransaction_use, user)
        except:
            continue

    return today_date.strftime("%Y-%m-%d")

if __name__ == '__main__':
    # calculate_work_hours()
    pass





































