# HackatonFlaskProject

# System ewidencji obecności (Flask + QR)

Prosta aplikacja webowa do rejestrowania obecności uczniów za pomocą kodów QR.

System pozwala nauczycielowi tworzyć sesje obecności, a uczniom potwierdzać obecność przez stronę lub skan QR kodu.

---

## Funkcje

- Tworzenie sesji obecności (nauczyciel)
- Generowanie QR kodu dla każdej sesji
- Zgłaszanie obecności przez uczniów
- Podgląd listy obecnych w czasie rzeczywistym
- Automatyczne wygaszanie sesji (1 godzina)
- Prosty interfejs webowy

---

## Technologie

- Python 3
- Flask
- qrcode
- Pillow
- HTML + JavaScript

---

## Instalacja i uruchomienie

### 1. Pobranie projektu


git clone <URL_REPO>
cd <NAZWA_PROJEKTU>
2. Utworzenie środowiska wirtualnego (zalecane)
python -m venv venv

Aktywacja środowiska:

Windows:

venv\Scripts\activate

Linux / MacOS:

source venv/bin/activate
3. Instalacja bibliotek
pip install flask qrcode pillow
4. Uruchomienie aplikacji
python app.py

Po uruchomieniu zobaczysz w terminalu:

Serwer ewidencji obecności uruchomiony na localhost
Nauczyciel:   http://localhost:5000/teacher
Dostęp do aplikacji
Panel nauczyciela

Otwórz w przeglądarce:

http://localhost:5000/teacher

Funkcje:

tworzenie nowych sesji
generowanie QR kodu
podgląd obecności uczniów w czasie rzeczywistym
🎓 Panel ucznia

Uczeń korzysta z linku lub QR kodu:

http://localhost:5000/student/<session_id>

Proces:

Wybór imienia z listy
Kliknięcie „Jestem obecny/a”
Potwierdzenie zapisania obecności
Konfiguracja

W pliku app.py możesz zmienić adres serwera:

BASE_URL = "http://localhost:5000"

Jeśli uruchamiasz projekt online (VPS / hosting), zmień na swój adres IP lub domenę.

 Czas trwania sesji

Domyślnie sesja trwa:

3600 sekund (1 godzina)

Zmiana w kodzie:

"expires": time.time() + 3600
API (opcjonalnie)
Tworzenie sesji

POST /start_session

Zaznaczenie obecności

POST /api/mark/<session_id>

Body:

{
  "student_id": 1
}
Status sesji

GET /session_status/<session_id>

Ważne informacje !
Dane przechowywane są w pamięci RAM
Po restarcie aplikacji wszystkie sesje znikają
Projekt ma charakter edukacyjny
▶️ Szybki start (TL;DR)
git clone <URL_REPO>
cd <PROJECT>
python -m venv venv
venv\Scripts\activate   # Windows
pip install flask qrcode pillow
python app.py

Wejdź:

http://localhost:5000/teacher
Autor R.O

System ewidencji obecności stworzony w Flask + QR code.
