import os
import shutil
import csv
from pathlib import Path
from tracking.models import UserScreenshots


def export_user_screenshots(selected_year,selected_month):
    base_export_dir = Path.home() / "Desktop" / "UserScreenshotsExport"
    base_export_dir.mkdir(parents=True, exist_ok=True)  # Create base directory if it doesn't exist

    csv_file_path = base_export_dir / "user_screenshots.csv"
    print("csv_file_path",csv_file_path)
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['ID', 'User', 'File', 'Created At', 'Updated At', 'File Status', 'New Location'])

        # print("get data................")
        screenshots = UserScreenshots.objects.filter(created_at__year=selected_year,created_at__month=selected_month)
        print(">>>>>>>>>>>>>>>>>>>",screenshots)
        for screenshot in screenshots:
            created_date = screenshot.created_at.date()
            year = created_date.year
            month = created_date.month
            day = created_date.day

            user_dir = base_export_dir / str(year) / str(month) /str('user-'+str(screenshot.user.id)) /str(day)
            user_dir.mkdir(parents=True, exist_ok=True)  # Create the directory structure

            new_file_path = user_dir / Path(screenshot.file.name).name

            original_file_path = screenshot.file.path

            if os.path.exists(original_file_path):
                try:
                    shutil.copy(original_file_path, new_file_path)  # Copy file to new location
                except Exception as e:
                    print(e)
            else:
                pass
            csv_writer.writerow([
                screenshot.id,
                screenshot.user.id,
                screenshot.file.name,
                screenshot.created_at,
                screenshot.updated_at
            ])

    print(f"Export completed. CSV saved to {csv_file_path} and files saved to {base_export_dir}")
