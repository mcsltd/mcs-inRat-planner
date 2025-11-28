@echo off
setlocal enabledelayedexpansion

title Установка ECG Recorder
echo ========================================
echo        УСТАНОВКА ECG RECORDER
echo ========================================
echo.

set PYTHON_EXE=python
set VENV_DIR=venv
set REQUIREMENTS=requirements.txt
set LOG_FILE=install.log

:: Проверка наличия requirements.txt
if not exist "%REQUIREMENTS%" (
    call :log "ОШИБКА: Файл %REQUIREMENTS% не найден"
    echo Файл требований %REQUIREMENTS% не найден!
    echo Убедитесь, что он находится в той же папке.
    pause
    exit /b 1
)

:: Создание виртуального окружения
call :log "Создание виртуального окружения..."
if exist "%VENV_DIR%" (
    call :log "Виртуальное окружение уже существует, удаляем..."
    rmdir /s /q "%VENV_DIR%" 2>nul
)

%PYTHON_EXE% -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    call :log "ОШИБКА: Не удалось создать виртуальное окружение"
    echo Не удалось создать виртуальное окружение!
    pause
    exit /b 1
)
call :log "Виртуальное окружение создано успешно"

:: Активация виртуального окружения
call :log "Активация виртуального окружения..."
call "%VENV_DIR%\Scripts\activate"
if %errorlevel% neq 0 (
    call :log "ОШИБКА: Не удалось активировать виртуальное окружение"
    echo Не удалось активировать виртуальное окружение!
    pause
    exit /b 1
)

:: Обновление pip
call :log "Обновление pip..."
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    call :log "ПРЕДУПРЕЖДЕНИЕ: Не удалось обновить pip, продолжаем..."
)

:: Установка зависимостей
call :log "Установка зависимостей из %REQUIREMENTS%..."
echo Устанавливаем зависимости, это может занять несколько минут...
python -m pip install -r "%REQUIREMENTS%"
if %errorlevel% neq 0 (
    call :log "ОШИБКА: Не удалось установить зависимости"
    echo.
    echo ========================================
    echo Ошибка при установке зависимостей!
    echo.
    echo Попробуйте следующие решения:
    echo 1. Запустите install.bat от имени администратора
    echo 2. Проверьте подключение к интернету
    echo 3. Убедитесь, что антивирус не блокирует установку
    echo ========================================
    echo.
    pause
    exit /b 1
)
call :log "Зависимости установлены успешно"

:: start.bat
echo @echo off > start.bat
echo call %VENV_DIR%\Scripts\activate >> start.bat
echo python src\main.py >> start.bat
echo pause >> start.bat

:: update.bat
echo @echo off > update.bat
echo call %VENV_DIR%\Scripts\activate >> update.bat
echo python -m pip install --upgrade -r requirements.txt >> update.bat
echo echo Обновление завершено! >> update.bat
echo pause >> update.bat

:: Создание конфигурационного файла по умолчанию
if not exist "config\default.yaml" (
    call :log "Создание конфигурационного файла..."
    echo # Конфигурация ECG Recorder > config\default.yaml
    echo bluetooth: >> config\default.yaml
    echo   scan_timeout: 30 >> config\default.yaml
    echo   retry_attempts: 3 >> config\default.yaml
    echo schedule: >> config\default.yaml
    echo   check_interval: 60 >> config\default.yaml
    echo recording: >> config\default.yaml
    echo   duration: 300 >> config\default.yaml
    echo   sample_rate: 500 >> config\default.yaml
)

:: Финальное сообщение
call :log "Установка завершена успешно!"
echo.
echo ========================================
echo    УСТАНОВКА УСПЕШНО ЗАВЕРШЕНА!
echo ========================================
echo.
echo Что дальше?
echo 1. Запустите start.bat для начала работы
echo 2. Запустите update.bat для обновления
echo 3. Проверьте папку config для настроек
echo.
echo Логи установки: %LOG_FILE%
echo.
echo Счастливых записей ЭКГ! ❤️
echo.

:: Автоматическое закрытие через 30 секунд
choice /c yn /t 30 /d y /m "Закрыть окно сейчас? (Y - да, N - оставить открытым)"
if %errorlevel% equ 1 (
    call :log "Окно закрыто пользователем"
    exit /b 0
) else (
    call :log "Окно оставлено открытым"
)

endlocal