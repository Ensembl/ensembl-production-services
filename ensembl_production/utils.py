# -*- coding: utf-8 -*-
import json


def escape_perl_string(v):
    """Escape characters with special meaning in perl"""
    return str(v).replace("$", "\\$").replace("\"", "\\\"").replace("@", "\\@")


def perl_string_to_python(s):
    """Parse a Perl hash string into a Python dict"""
    s = s.replace("=>", ":").replace("\\$", "$").replace("\\@", "@").replace('\'', '"')
    return json.loads(s)
