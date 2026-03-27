import os
import shutil

from device.inrat_v0.constants import InRatDataRateEcg
from structure import RecordData


def delete_file(file_path: str | None) -> bool:
    """ Удаляет файл по указанному пути. """

    if file_path is None:
        return True

    try:
        os.remove(file_path)
        return True
    except FileNotFoundError:
        return False
    except PermissionError:
        return False
    except OSError as e:
        return False


def copy_file(path_to_copy: str, record: RecordData) -> str:
    """ Копировать записи по выбранному пути """
    if record.path is None:
        error_message = f"Путь до файла не определен {record.path}."
        return error_message

    if record.file_format == "EDF":

        if not os.path.exists(record.path):
            error_message = f"Ошибка: исходный файл не существует - {record.path}"
            return error_message

        if os.path.isdir(path_to_copy):
            filename = os.path.basename(record.path)
            destination_path = os.path.join(path_to_copy, filename)

            if not os.path.exists(destination_path):
                shutil.copy2(record.path, destination_path)
                return ""
            else:
                error_message = f"Файл {filename} уже существует в выбранной папке!"
                return error_message

    elif record.file_format == "WFDB":
        if os.path.isdir(path_to_copy):

            filename = os.path.basename(record.path)
            if ".dat" in filename:
                filename = filename.split(".dat")[0]
            if ".hea" in filename:
                filename = filename.split(".hea")[0]

            # копирование файла .hea
            filename_header = "".join([filename, ".hea"])
            path_to_header = os.path.join(os.path.dirname(record.path), filename_header) # путь до файла .hea
            destination_path_header = os.path.join(path_to_copy, filename_header)
            if os.path.exists(destination_path_header):
                error_message = f"Файл {filename_header} уже существует в выбранной папке!"
                return error_message
            shutil.copy2(path_to_header, destination_path_header)

            # копирование файла .dat
            filename_data = "".join([filename, ".dat"])
            path_to_data = os.path.join(os.path.dirname(record.path), filename_data)
            destination_path_data = os.path.join(path_to_copy, filename_data)
            if os.path.exists(destination_path_data):
                error_message = f"Файл {filename} уже существует в выбранной папке!"
                return error_message
            shutil.copy2(path_to_data, destination_path_data)

            return ""
    else:
        error_message = "Неизвестный тип файла"
        return error_message


def convert_in_rat_sample_rate_to_str(code: int):
    """ Функция конвертации кодов частоты оцифровки в строки """
    if InRatDataRateEcg.HZ_500.value == code:
        return "500 Гц"
    elif InRatDataRateEcg.HZ_1000.value == code:
        return "1000 Гц"
    elif InRatDataRateEcg.HZ_2000.value == code:
        return "2000 Гц"
    return None


def seconds_to_label_time(seconds: float) -> str:
    if seconds < 0:
        raise ValueError("Cекунды меньше 0")

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"