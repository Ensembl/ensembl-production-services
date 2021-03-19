#   See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.import json


def escape_perl_string(v):
    """Escape characters with special meaning in perl"""
    return str(v).replace("$", "\\$").replace("\"", "\\\"").replace("@", "\\@") if v else ''


def perl_string_to_python(s):
    """Parse a Perl hash string into a Python dict"""
    if s:
        s = s.replace("=>", ":").replace("\\$", "$").replace("\\@", "@").replace('\'', '"').replace('\n', '')
        return json.loads(s)
    else:
        return ''


def perl_string_to_python_website(s):
    """Parse a Perl hash string into a Python dict"""
    if s:
        s = s.replace("=>", ":").replace("\\$", "$").replace("\\@", "@").replace('\n', '').replace('\r', '')
        return json.loads(s)
    else:
        return ''


def list_to_perl_string(input_list):
    """Transform the supplied array into a string representation of a Perl array"""
    elems = []
    for v in input_list:
        t = type(v).__name__
        if t == 'str':
            elems.append("\"%s\"" % escape_perl_string(v))
        elif t == 'unicode':
            elems.append("\"%s\"" % escape_perl_string(str(v)))
        elif t in ('int', 'long'):
            elems.append("%d" % v)
        elif t == 'float':
            elems.append("%f" % v)
        elif t == 'list':
            elems.append("%s" % list_to_perl_string(v))
        elif t == 'dict':
            elems.append("%s" % to_internal_value(v))
        else:
            raise Exception("Unsupported type " + str(t))
    return "[%s]" % ", ".join(elems)


def to_internal_value(data):
    """Transform the supplied dict into a string representation of a Perl hash"""
    pairs = []
    for k, v in sorted([(k, v) for k, v in data.items() if v is not None], key=lambda x: x[0]):
        k = str(k)
        t = type(v).__name__
        if t == 'str':
            pairs.append("\"%s\" => \"%s\"" % (k, escape_perl_string(v)))
        elif t == 'unicode':
            pairs.append("\"%s\" => \"%s\"" % (k, escape_perl_string(str(v))))
        elif t in ('int', 'long'):
            pairs.append("\"%s\" => %d" % (k, v))
        elif t == 'float':
            pairs.append("\"%s\" => %f" % (k, v))
        elif t == 'list':
            pairs.append("\"%s\" => %s" % (k, list_to_perl_string(v)))
        elif t == 'dict':
            pairs.append("\"%s\" => %s" % (k, to_internal_value(v)))
        elif t == 'bool':
            if str(v) == "True":
                pairs.append("\"%s\" => %d" % (k, 1))
        else:
            raise Exception("Unsupported type " + str(t))
    return "{%s}" % ", ".join(pairs)
