import requests
import json
import logging


class APIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.example.com"

    def get_movie_schedules(self, location, date):
        endpoint = "/schedules"
        url = f"{self.base_url}{endpoint}"
        params = {
            "location": location,
            "date": date,
            "api_key": self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            schedules = response.json()
            return schedules
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while retrieving schedules: {e}")
            return None

    def get_movie_details(self, movie_id):
        endpoint = f"/movies/{movie_id}"
        url = f"{self.base_url}{endpoint}"
        params = {
            "api_key": self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            movie_details = response.json()
            return movie_details
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while retrieving movie details: {e}")
            return None

    def check_seat_availability(self, movie_id, showtime, seats):
        endpoint = "/seats/check_availability"
        url = f"{self.base_url}{endpoint}"
        payload = {
            "movie_id": movie_id,
            "showtime": showtime,
            "seats": seats
        }
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            availability = response.json().get("availability")
            return availability
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while checking seat availability: {e}")
            return False

    def make_ticket_booking(self, movie_id, showtime, seats):
        endpoint = "/bookings"
        url = f"{self.base_url}{endpoint}"
        payload = {
            "movie_id": movie_id,
            "showtime": showtime,
            "seats": seats
        }
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            booking_status = response.json().get("status")
            return booking_status == "success"
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while making ticket booking: {e}")
            return False

    def send_booking_confirmation_email(self, movie_id, showtime, seats):
        endpoint = "/send"
        url = f"{self.base_url}{endpoint}"
        payload = {
            "to": "customer@example.com",
            "subject": "Booking Confirmation",
            "body": f"Thank you for booking tickets!\n\nMovie ID: {movie_id}\nShowtime: {showtime}\nSeats: {seats}"
        }
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while sending booking confirmation email: {e}")
            return False
