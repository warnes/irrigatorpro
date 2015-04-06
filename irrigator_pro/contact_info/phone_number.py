# Class to handle validation and formatting of phone numbers.

import re

class PhoneNumber:
    p1 = re.compile('^[\d\s()-]+$')
    p2 = re.compile('[^\d]+')

    def __init__(self, number):
        self.original = number

        stripped = number.strip()
        if stripped == '':
            self.valid = True
            self.original = ''
            self.unformatted = ''
            return

        # Check that the string contains only [0-9()-]
        # so 555()---555---5555 is accepted. 
        if not PhoneNumber.p1.match(number):
            self.valid = False
            self.unformatted = self.original
            self.error_msg = "Number can only contain numbers, the - sign, and ()"
            return

        # Extract all the numbers
        m = PhoneNumber.p2.sub("", stripped)
        if len(m) != 10:
            self.valid = False
            self.unformatted = self.original
            self.error_msg = 'Number must contain 10 numbers, preferably in the format (555) 555-5555' 
            return

        # If we make it here the number is valid
        self.valid = True
        self.unformatted = m
