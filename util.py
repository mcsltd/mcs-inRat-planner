import os

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