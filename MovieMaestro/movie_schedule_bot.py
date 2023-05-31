import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re
import os
import prettytable
import json
import logging
from cryptography.fernet import Fernet

CONFIG_FILE = "config.json"
ENCRYPTED_CONFIG_FILE = "encrypted_config.json"
KEY_FILE = "key.key"

class MovieScheduleBot:
    def __init__(self):
        self.api_key = None
        self.auth_token = None
        self.email_auth_token = None
        self.fernet_key = None

    def generate_default_config(self):
        config = {
            "MOVIE_API_KEY": "YOUR_MOVIE_API_KEY",
            "TICKETING_SYSTEM_AUTH_TOKEN": "YOUR_TICKETING_SYSTEM_AUTH_TOKEN",
            "EMAIL_SERVICE_AUTH_TOKEN": "YOUR_EMAIL_SERVICE_AUTH_TOKEN"
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    def encrypt_config(self):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        fernet = Fernet(self.fernet_key)
        encrypted_config = fernet.encrypt(json.dumps(config).encode())

        with open(ENCRYPTED_CONFIG_FILE, "wb") as f:
            f.write(encrypted_config)

    def decrypt_config(self):
        with open(ENCRYPTED_CONFIG_FILE, "rb") as f:
            encrypted_config = f.read()

        fernet = Fernet(self.fernet_key)
        decrypted_config = fernet.decrypt(encrypted_config).decode()

        return json.loads(decrypted_config)

    def load_config(self):
        try:
            with open(KEY_FILE, "rb") as f:
                self.fernet_key = f.read()

            if not os.path.exists(ENCRYPTED_CONFIG_FILE):
                self.generate_default_config()
                self.encrypt_config()
            else:
                config = self.decrypt_config()
                self.api_key = config.get("MOVIE_API_KEY")
                self.auth_token = config.get("TICKETING_SYSTEM_AUTH_TOKEN")
                self.email_auth_token = config.get("EMAIL_SERVICE_AUTH_TOKEN")

        except (FileNotFoundError, json.JSONDecodeError):
            logging.error("Failed to load configuration file.")

    def check_seat_availability(self, movie_id, showtime, seats):
        # Check seat availability using an external ticketing system API
        url = "https://api.ticketing-system.com/seats/check_availability"
        payload = {
            "movie_id": movie_id,
            "showtime": showtime,
            "seats": seats
        }
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
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
        # Make ticket booking using an external ticketing system API
        url = "https://api.ticketing-system.com/bookings"
        payload = {
            "movie_id": movie_id,
            "showtime": showtime,
            "seats": seats,
            "customer_id": "CUSTOMER_ID"
        }
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
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
        # Send booking confirmation email using an email sending service
        email_service_url = "https://api.email-service.com/send"
        payload = {
            "to": "customer@example.com",
            "subject": "Booking Confirmation",
            "body": f"Thank you for booking tickets!\n\nMovie ID: {movie_id}\nShowtime: {showtime}\nSeats: {seats}"
        }
        headers = {
            "Authorization": f"Bearer {self.email_auth_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(email_service_url, json=payload, headers=headers)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while sending booking confirmation email: {e}")
            return False

    def validate_date(self, date):
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        return re.match(pattern, date)

    def validate_seats(self, seats):
        try:
            seats = int(seats)
            return seats > 0
        except ValueError:
            return False

    def get_movie_schedules(self, location, date):
        try:
            url = f"https://api.movies.com/schedules?location={location}&date={date}&api_key={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            schedules = response.json()
            return schedules
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while retrieving schedules: {e}")
            return None

    def get_movie_details(self, movie_id):
        try:
            url = f"https://api.movies.com/movies/{movie_id}?api_key={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            movie_details = response.json()
            return movie_details
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while retrieving movie details: {e}")
            return None

    def display_movie_schedule(self, schedule):
        movie_id = schedule["movie_id"]
        movie_details = self.get_movie_details(movie_id)
        if movie_details:
            title = movie_details["title"]
            duration = movie_details["duration"]
            synopsis = movie_details["synopsis"]
            showtimes = schedule["showtimes"]

            messagebox.showinfo("Movie Schedule", f"Title: {title}\nDuration: {duration} minutes\nSynopsis: {synopsis}\nShowtimes: {', '.join(showtimes)}")
        else:
            messagebox.showerror("Error", "Failed to retrieve movie details.")

    def display_schedules_table(self, schedules):
        if not schedules:
            messagebox.showinfo("Movie Schedules", "No schedules available.")
            return

        table = prettytable.PrettyTable()
        table.field_names = ["Index", "Title", "Duration", "Showtimes"]

        for index, schedule in enumerate(schedules):
            movie_id = schedule["movie_id"]
            movie_details = self.get_movie_details(movie_id)
            if movie_details:
                title = movie_details["title"]
                duration = movie_details["duration"]
                showtimes = ", ".join(schedule["showtimes"])
                table.add_row([index, title, duration, showtimes])

        messagebox.showinfo("Movie Schedules", table)

    def book_tickets(self, movie_id, showtime, seats):
        if self.validate_seats(seats):
            if not self.check_seat_availability(movie_id, showtime, seats):
                messagebox.showinfo("Booking Failed", "Seats not available.")
                return

            booking_successful = self.make_ticket_booking(movie_id, showtime, seats)

            if booking_successful:
                messagebox.showinfo("Booking Successful", "Tickets booked successfully!")
                self.send_booking_confirmation_email(movie_id, showtime, seats)
            else:
                messagebox.showinfo("Booking Failed", "Booking failed. Please try again later.")
        else:
            messagebox.showinfo("Invalid Seats", "Invalid number of seats.")

    def main(self):
        if not os.path.exists(CONFIG_FILE):
            self.generate_default_config()

        self.load_config()

        logging.basicConfig(level=logging.INFO)

        root = tk.Tk()
        root.title("Movie Schedule Bot")

        # Location Selection
        location_label = tk.Label(root, text="Select location:")
        location_label.grid(row=0, column=0, padx=10, pady=10)

        location_var = tk.StringVar()
        location_dropdown = ttk.Combobox(root, textvariable=location_var, state="readonly")
        location_dropdown["values"] = ("Location 1", "Location 2", "Location 3")  # Update with actual values
        location_dropdown.current(0)
        location_dropdown.grid(row=0, column=1, padx=10, pady=10)

        # Date Entry
        date_label = tk.Label(root, text="Enter the date (YYYY-MM-DD):")
        date_label.grid(row=1, column=0, padx=10, pady=10)

        date_entry = tk.Entry(root)
        date_entry.grid(row=1, column=1, padx=10, pady=10)

        def search_schedules():
            location = location_var.get()
            date = date_entry.get()

            if not self.validate_date(date):
                messagebox.showerror("Error", "Invalid date format.")
                return

            schedules = self.get_movie_schedules(location, date)

            if not schedules:
                messagebox.showerror("Error", "Failed to retrieve schedules.")
                return

            self.display_schedules_table(schedules)

        search_button = tk.Button(root, text="Search Schedules", command=search_schedules)
        search_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        def book_tickets_dialog():
            selection = messagebox.askquestion("Book Tickets", "Do you want to book tickets?")
            if selection == "yes":
                index = messagebox.askinteger("Select Schedule", "Enter the index of the schedule you want to view:")
                if index is not None:
                    schedules = self.get_movie_schedules(location_var.get(), date_entry.get())
                    if schedules and 0 <= index < len(schedules):
                        schedule = schedules[index]
                        self.display_movie_schedule(schedule)
                        movie_id = schedule["movie_id"]
                        showtime = messagebox.askstring("Select Showtime", "Enter the desired showtime:")
                        seats = messagebox.askinteger("Enter Seats", "Enter the number of seats to book:")
                        if showtime and seats is not None:
                            self.book_tickets(movie_id, showtime, seats)

        book_tickets_button = tk.Button(root, text="Book Tickets", command=book_tickets_dialog)
        book_tickets_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        root.mainloop()

if __name__ == "__main__":
    bot = MovieScheduleBot()
    bot.main()
