"""
Automated tests for hotel_booking.py (PS No. 68)
Run with:  python test_hotel_booking.py
Part A: the 4 test cases from the project sheet
Part B: the 5 "Bare Minimum Requirements"
"""
import io, os, tempfile, unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import one as hb


def run(inputs, func):
    """Call func() while feeding `inputs` to input(); return printed text."""
    buf = io.StringIO()
    with patch("builtins.input", side_effect=list(inputs)), redirect_stdout(buf):
        func()
    return buf.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        # every test runs in a fresh folder so bookings.txt starts empty
        self.old = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)
        hb.bookings.clear()

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()


# ------------------------- PART A: TEST CASES -------------------------
class TestCases(Base):
    def test_case_1_normal_input(self):
        out = run(["Amit", "101", "2"], hb.book_room)
        self.assertIn("Room 101 booked for Amit | 2 nights", out)
        self.assertIn("Bill: 4000 + GST 480 = Rs. 4480", out)

    def test_case_2_boundary_minimum(self):
        out = run(["Neha", "102", "1"], hb.book_room)
        self.assertIn("Room 102 booked for Neha | 1 night", out)
        self.assertNotIn("1 nights", out)
        self.assertIn("Bill: 3500 + GST 420 = Rs. 3920", out)

    def test_case_3_invalid_already_booked(self):
        run(["Amit", "101", "2"], hb.book_room)           # Room 101 booked by Amit
        out = run(["Neha", "101", "3"], hb.book_room)     # Neha tries room 101
        self.assertIn("Room 101 is already booked. Please choose another room.", out)
        self.assertEqual(len(hb.bookings), 1)             # no second booking added

    def test_case_4_different_valid_scenario(self):
        with open("bookings.txt", "w") as f:              # file has: Room 101 - Amit - 2
            f.write("101|Amit|2\n")
        hb.load_bookings()
        out_a = run([], hb.view_available)                # (a) menu option 1
        self.assertEqual(out_a.strip(), "102 Double Rs. 3500 | 201 Suite Rs. 6000")
        out_b = run(["101"], hb.cancel_booking)           # (b) menu option 4
        self.assertIn("Booking for room 101 cancelled. Room 101 is now available.", out_b)
        self.assertFalse(hb.is_booked(101))


# ------------------- PART B: BARE MINIMUM REQUIREMENTS -------------------
class Requirements(Base):
    def test_req2_dictionary_and_list(self):
        self.assertIsInstance(hb.ROOMS, dict)
        self.assertEqual(hb.ROOMS[101]["rate"], 2000)
        self.assertEqual(hb.ROOMS[102]["rate"], 3500)
        self.assertEqual(hb.ROOMS[201]["rate"], 6000)
        run(["Amit", "101", "2"], hb.book_room)
        self.assertIsInstance(hb.bookings, list)
        self.assertIsInstance(hb.bookings[0], dict)

    def test_req3_functions_exist(self):
        for name in ("view_available", "book_room", "cancel_booking", "generate_bill"):
            self.assertTrue(callable(getattr(hb, name)), name)

    def test_req3_generate_bill(self):
        run(["Raj", "201", "3"], hb.book_room)
        out = run(["201"], hb.generate_bill)
        self.assertIn("Bill: 18000 + GST 2160 = Rs. 20160", out)

    def test_req4_invalid_room_rejected(self):
        for bad in ("999", "abc", "", "-101", "10.1"):
            hb.bookings.clear()
            out = run(["Amit", bad, "2"], hb.book_room)
            self.assertIn("Invalid room number", out, bad)
            self.assertEqual(hb.bookings, [])

    def test_req4_nights_validation(self):
        for bad in ("0", "31", "-1", "abc", "", "2.5", "100"):
            hb.bookings.clear()
            out = run(["Amit", "101", bad], hb.book_room)
            self.assertIn("Invalid nights", out, bad)
            self.assertEqual(hb.bookings, [], bad)

    def test_req4_nights_limits_accepted(self):
        out1 = run(["A", "101", "1"], hb.book_room)
        out30 = run(["B", "102", "30"], hb.book_room)
        self.assertIn("booked", out1)
        self.assertIn("booked", out30)

    def test_req4_no_double_booking_any_room(self):
        for room in ("101", "102", "201"):
            run(["First", room, "1"], hb.book_room)
            out = run(["Second", room, "1"], hb.book_room)
            self.assertIn("already booked", out)
        self.assertEqual(len(hb.bookings), 3)

    def test_req5_save_after_book(self):
        run(["Amit", "101", "2"], hb.book_room)
        with open("bookings.txt") as f:
            self.assertEqual(f.read().strip(), "101|Amit|2")

    def test_req5_save_after_cancel(self):
        run(["Amit", "101", "2"], hb.book_room)
        run(["101"], hb.cancel_booking)
        with open("bookings.txt") as f:
            self.assertEqual(f.read().strip(), "")

    def test_req5_not_saved_on_failed_booking(self):
        run(["Amit", "101", "2"], hb.book_room)
        run(["Neha", "101", "3"], hb.book_room)           # rejected
        with open("bookings.txt") as f:
            self.assertEqual(f.read().strip(), "101|Amit|2")

    def test_req5_load_at_start(self):
        run(["Amit", "101", "2"], hb.book_room)
        hb.bookings.clear()                               # simulate closing the program
        hb.load_bookings()                                # simulate starting again
        self.assertEqual(hb.bookings, [{"room": 101, "guest": "Amit", "nights": 2}])
        out = run(["Neha", "101", "1"], hb.book_room)     # still blocked after restart
        self.assertIn("already booked", out)

    def test_req5_missing_or_bad_file(self):
        hb.load_bookings()                                # no file: must not crash
        self.assertEqual(hb.bookings, [])
        with open("bookings.txt", "w") as f:
            f.write("garbage\n101|Amit|2\n999|X|1\n102|Y|abc\n")
        hb.load_bookings()                                # bad lines skipped
        self.assertEqual(len(hb.bookings), 1)

    def test_cancel_nonexistent(self):
        out = run(["102"], hb.cancel_booking)
        self.assertIn("no booking", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
