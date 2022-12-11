from datetime import date, time, datetime, timedelta

HORACOMIENZOPEDIDO = datetime.now().time().replace(hour=10, minute=0, second=0)
HORAMEDIANOCHE24 = datetime.now().time().replace(hour=23, minute=59, second=59)
HORAMEDIANOCHE0 = datetime.now().time().replace(hour=0, minute=0, second=0)
HORAFINALIZA = datetime.now().time().replace(hour=9, minute=30, second=0)