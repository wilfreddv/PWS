import crypt
from collections import defaultdict
import pandas as pd

def get_salt():
    return crypt.mksalt(crypt.METHOD_SHA512)

def hash_password(p,s):
        return crypt.crypt(p, s)

def restructure_form(form):
    """
    Restructure the form to put it into database easily
    """
    #[hour|date|room]
    #[[date, hour, rooma, roomb, roomc]]

    #Relies on werkzeug.datastructures.ImmutableMultiDict being ordered :S
    tmp = defaultdict(list)
    for key in sorted(form.keys()):
        val = form[key]
        h, d, _ = key.split('|')
        tmp[d+'|'+h].append(val)

    out = []
    for key, val in tmp.items():
        date, hour = key.split('|')
        tmp = [date, hour]
        tmp.extend(val)
        out.append(tmp)

    return out
