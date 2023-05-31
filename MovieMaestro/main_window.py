import tkinter as tk
from tkinter import ttk, messagebox
from api_client import APIClient
from utils import load_config, load_encryption_key, decrypt_config

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Movie Maestro")
        self.geometry("400x300")
        self.configure(bg="#f2f2f2")

        # Load configuration
        config_file_path = "config.json"
        encryption_key_path = "key.key"

        encryption_key = load_encryption_key(encryption_key_path)
        if not encryption_key:
            messagebox.showerror("Error", "Failed to load encryption key.")
            self.destroy()
            return

        encrypted_config = load_config(config_file_path)
        if not encrypted_config:
            messagebox.showerror("Error", "Failed to load config file.")
            self.destroy()
            return

        decrypted_config = decrypt_config(encrypted_config, encryption_key)
        if not decrypted_config:
            messagebox.showerror("Error", "Failed to decrypt config.")
            self.destroy()
            return

        self.api_client = APIClient(decrypted_config)

        # Location Selection
        location_label = tk.Label(self, text="Select Location:", font=("Arial", 14), bg="#f2f2f2")
        location_label.pack(pady=10)

        location_var = tk.StringVar()
        location_dropdown = ttk.Combobox(self, textvariable=location_var, state="readonly", font=("Arial", 12))
        location_dropdown["values"] = ("Location 1", "Location 2", "Location 3")  # Replace with actual values
        location_dropdown.current(0)
        location_dropdown.pack(pady=10)

        # Date Entry
        date_label = tk.Label(self, text="Enter Date (YYYY-MM-DD):", font=("Arial", 14), bg="#f2f2f2")
        date_label.pack()

        date_entry = tk.Entry(self, font=("Arial", 12))
        date_entry.pack(pady=10)

        def search_schedules():
            location = location_var.get()
            date = date_entry.get()

            if not self.api_client.validate_date(date):
                messagebox.showerror("Error", "Invalid date format.")
                return

            schedules = self.api_client.get_movie_schedules(location, date)

            if not schedules:
                messagebox.showinfo("Movie Schedules", "No schedules available.")
                return

            self.display_schedules_table(schedules)

        search_button = tk.Button(self, text="Search Schedules", command=search_schedules, font=("Arial", 12))
        search_button.pack(pady=10)

        def book_tickets_dialog():
            selection = messagebox.askquestion("Book Tickets", "Do you want to book tickets?")
            if selection == "yes":
                index = messagebox.askinteger("Select Schedule", "Enter the index of the schedule you want to view:")
                if index is not None:
                    schedules = self.api_client.get_movie_schedules(location_var.get(), date_entry.get())
                    if schedules and 0 <= index < len(schedules):
                        schedule = schedules[index]
                        self.display_movie_schedule(schedule)
                        movie_id = schedule["movie_id"]
                        showtime = messagebox.askstring("Select Showtime", "Enter the desired showtime:")
                        seats = messagebox.askinteger("Enter Seats", "Enter the number of seats to book:")
                        if showtime and seats is not None:
                            self.book_tickets(movie_id, showtime, seats)

        book_tickets_button = tk.Button(self, text="Book Tickets", command=book_tickets_dialog, font=("Arial", 12))
        book_tickets_button.pack(pady=10)

    def display_schedules_table(self, schedules):
        table_window = tk.Toplevel(self)
        table_window.title("Movie Schedules")
        table_window.geometry("600x400")

        if not schedules:
            no_schedules_label = tk.Label(table_window, text="No schedules available.", font=("Arial", 14))
            no_schedules_label.pack(pady=50)
            return

        table = ttk.Treeview(table_window, columns=("Index", "Title", "Duration", "Showtimes"), show="headings")
        table.heading("Index", text="Index")
        table.heading("Title", text="Title")
        table.heading("Duration", text="Duration")
        table.heading("Showtimes", text="Showtimes")

        for index, schedule in enumerate(schedules):
            movie_id = schedule["movie_id"]
            movie_details = self.api_client.get_movie_details(movie_id)
            if movie_details:
                title = movie_details["title"]
                duration = movie_details["duration"]
                showtimes = ", ".join(schedule["showtimes"])
                table.insert("", "end", values=(index, title, duration, showtimes))

        table.pack(pady=10)

    def display_movie_schedule(self, schedule):
        movie_id = schedule["movie_id"]
        movie_details = self.api_client.get_movie_details(movie_id)
        if movie_details:
            title = movie_details["title"]
            duration = movie_details["duration"]
            synopsis = movie_details["synopsis"]
            showtimes = schedule["showtimes"]

            messagebox.showinfo("Movie Schedule", f"Title: {title}\nDuration: {duration} minutes\nSynopsis: {synopsis}\nShowtimes: {', '.join(showtimes)}")
        else:
            messagebox.showerror("Error", "Failed to retrieve movie details.")

    def book_tickets(self, movie_id, showtime, seats):
        if self.api_client.validate_seats(seats):
            if not self.api_client.check_seat_availability(movie_id, showtime, seats):
                messagebox.showinfo("Booking Failed", "Seats not available.")
                return

            booking_successful = self.api_client.make_ticket_booking(movie_id, showtime, seats)

            if booking_successful:
                messagebox.showinfo("Booking Successful", "Tickets booked successfully!")
                self.api_client.send_booking_confirmation_email(movie_id, showtime, seats)
            else:
                messagebox.showinfo("Booking Failed", "Booking failed. Please try again later.")
        else:
            messagebox.showinfo("Invalid Seats", "Invalid number of seats.")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
