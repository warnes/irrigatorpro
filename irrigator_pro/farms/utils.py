from farms.models import *
from datetime import datetime, date

from decimal import Decimal
from common.utils import daterange, quantize



def to_faren(temp_c):
    return quantize(Decimal(9.0) * temp_c /Decimal(5.0) + Decimal(32.0))

def to_inches(original, original_units):
    if original_units == "mm":
        original = original / Decimal(10)
    return quantize(original * Decimal(0.3937008))
