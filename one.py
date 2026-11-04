"""
Project Title : Hotel Room Booking System (PS No. 68)
Course        : Programming Fundamentals Using Python (RU-100-05-00058)
Programme     : BCA / First Semester / Section 1C
Language : Python 3
Concepts : Dictionaries, Lists, Functions, File Handling
"""

# ---------------------------------------------------------------
# 1. CONSTANTS
# ---------------------------------------------------------------
FILE_NAME = "bookings.txt"
GST_RATE = 0.12          # 12% GST
MIN_NIGHTS = 1
MAX_NIGHTS = 30

# Dictionary: room number -> details (type and rate per night)
ROOMS = {
    101: {"type": "Single", "rate": 2000},
    102: {"type": "Double", "rate": 3500},
    201: {"type": "Suite", "rate": 6000},
}

# List of dictionaries: each dictionary is one booking
# Example: {"room": 101, "guest": "Amit", "nights": 2}
bookings = []


# ---------------------------------------------------------------
# 2. FILE HANDLING
# ---------------------------------------------------------------
def load_bookings():
    """Read bookings.txt at program start. Each line: room|guest|nights"""
    bookings.clear()
    try:
        with open(FILE_NAME, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) != 3:
                    continue  # skip damaged lines
                room, guest, nights = parts
                if room.isdigit() and nights.isdigit() and int(room) in ROOMS:
                    bookings.append(
                        {"room": int(room), "guest": guest, "nights": int(nights)}
                    )
    except FileNotFoundError:
        pass  # first run: no file yet, start with empty list


def save_bookings():
    """Write all current bookings to bookings.txt (called after every change)."""
    with open(FILE_NAME, "w") as f:
        for b in bookings:
            f.write(f"{b['room']}|{b['guest']}|{b['nights']}\n")


# ---------------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------------
def is_booked(room_no):
    """Return True if the room already has a booking."""
    for b in bookings:
        if b["room"] == room_no:
            return True
    return False


def find_booking(room_no):
    """Return the booking dictionary for a room, or None."""
    for b in bookings:
        if b["room"] == room_no:
            return b
    return None


def calculate_bill(room_no, nights):
    """Bill = rate x nights + 12% GST. Returns (amount, gst, total)."""
    amount = ROOMS[room_no]["rate"] * nights
    gst = round(amount * GST_RATE)
    return amount, gst, amount + gst


def read_room_number():
    """Ask for a room number; return int or None if invalid."""
    text = input("Room: ").strip()
    if not text.isdigit() or int(text) not in ROOMS:
        print("Invalid room number. Valid rooms:",
              ", ".join(str(r) for r in ROOMS))
        return None
    return int(text)


# ---------------------------------------------------------------
# 4. MAIN FEATURES
# ---------------------------------------------------------------
def view_available():
    """Menu 1: show rooms that are not booked."""
    free = [r for r in ROOMS if not is_booked(r)]
    if not free:
        print("No rooms are available.")
        return
    parts = [f"{r} {ROOMS[r]['type']} Rs. {ROOMS[r]['rate']}" for r in free]
    print(" | ".join(parts))


def book_room():
    """Menu 2: book a room for a guest."""
    guest = input("Guest: ").strip()
    if not guest or "|" in guest:
        print("Invalid guest name.")
        return

    room_no = read_room_number()
    if room_no is None:
        return

    # No double booking
    if is_booked(room_no):
        print(f"Room {room_no} is already booked. Please choose another room.")
        return

    nights_text = input("Nights: ").strip()
    if not nights_text.isdigit() or not (MIN_NIGHTS <= int(nights_text) <= MAX_NIGHTS):
        print(f"Invalid nights. Enter a whole number from {MIN_NIGHTS} to {MAX_NIGHTS}.")
        return
    nights = int(nights_text)

    bookings.append({"room": room_no, "guest": guest, "nights": nights})
    save_bookings()

    night_word = "night" if nights == 1 else "nights"
    amount, gst, total = calculate_bill(room_no, nights)
    print(f"Room {room_no} booked for {guest} | {nights} {night_word}")
    print(f"Bill: {amount} + GST {gst} = Rs. {total}")


def generate_bill():
    """Menu 3: print the bill for an existing booking."""
    room_no = read_room_number()
    if room_no is None:
        return
    b = find_booking(room_no)
    if b is None:
        print(f"Room {room_no} has no booking.")
        return
    amount, gst, total = calculate_bill(room_no, b["nights"])
    print(f"Guest: {b['guest']} | Room {room_no} | {b['nights']} night(s)")
    print(f"Bill: {amount} + GST {gst} = Rs. {total}")


def cancel_booking():
    """Menu 4: cancel the booking of a room."""
    room_no = read_room_number()
    if room_no is None:
        return
    b = find_booking(room_no)
    if b is None:
        print(f"Room {room_no} has no booking to cancel.")
        return
    bookings.remove(b)
    save_bookings()
    print(f"Booking for room {room_no} cancelled. Room {room_no} is now available.")


# ---------------------------------------------------------------
# 5. MENU / PROGRAM ENTRY
# ---------------------------------------------------------------
def show_menu():
    print("\n===== HOTEL ROOM BOOKING SYSTEM =====")
    print("1. View available rooms")
    print("2. Book a room")
    print("3. Generate bill")
    print("4. Cancel a booking")
    print("5. Exit")


def main():
    load_bookings()          # load saved bookings at start
    while True:
        show_menu()
        choice = input("Menu option: ").strip()
        if choice == "1":
            view_available()
        elif choice == "2":
            book_room()
        elif choice == "3":
            generate_bill()
        elif choice == "4":
            cancel_booking()
        elif choice == "5":
            print("Thank you. Goodbye!")
            break
        else:
            print("Invalid option. Please enter 1 to 5.")


if __name__ == "__main__":
    main()