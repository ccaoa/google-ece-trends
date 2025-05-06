"""
Functions that are essential to many CCAoA Research Team workflows.

A merger of the former `quick` and `corefunctions` modules.
"""

import time
from collections import defaultdict
from distutils.util import strtobool


def runtime(start: time.time):
    """Prints out the run time for a script in hours, minutes, and seconds. Requires import of time package.
    Requires a `start` variable at the beginning of your script where start = time.time()
    """
    time_dot_time = time.time()
    time_diff = time_dot_time - start

    hours = int(time_diff / 3600)
    hours_remainder = time_diff % 3600
    minutes = int(hours_remainder / 60)
    minutes_remainder = hours_remainder % 60
    seconds = int(minutes_remainder)
    print("Run Time:", hours, "hr,", minutes, "min,", seconds, "sec.")

    return time_diff


def string_to_bool(string_to_become_bool, suppress_prints=False):
    """Converts true/false strings into boolean items for downstream python use."""
    # https://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python
    tf_input = str(string_to_become_bool)
    if str(tf_input).lower() in [
        "tru",
        "tr",
        "truth",
        "y",
        "yes",
        "1",
        "yep",
        "oui",
        "si",
        "vrai",
        "cierto",
        "please",
        "ye",
    ]:
        tf_input = "true"
    if str(tf_input).lower() in [
        "fal",
        "fa",
        "fals",
        "no",
        "n",
        "na",
        "0",
        "nope",
        "non",
        "faux",
        "falsa",
        "falso",
    ]:
        tf_input = "false"
    try:
        the_bool_trueorfalse = bool(strtobool(tf_input))
    except ValueError:  # Exception: # as exc:
        if suppress_prints is False:
            print(tf_input, "is an invalid bool. Pass a valid value.")
            # print(exc)
        the_bool_trueorfalse = None

    return the_bool_trueorfalse


def find_value_in_list(
    in_value: str,
    values_list: list,
    return_input: bool = False,
    case_or_type_sensitive: bool = False,
) -> True:
    """Check if a value is in a list (or dict) of values."""
    # Make working string versions of the input variables.
    # # Do this instead of hard converting the variables so you can output the original input values.
    working_in_value = str(in_value)
    working_list = [str(i) for i in values_list]
    value_lower = working_in_value.lower()
    if string_to_bool(case_or_type_sensitive) is False:
        # The user doesn't want case or original type to play a factor in the match.
        # # Resilient part of this matcher. Catches all different types of matches!
        for sval in working_list:
            if sval.lower() == value_lower:
                if string_to_bool(return_input) is True:
                    # Return the original string being tested.
                    return in_value
                else:
                    # Return the semi-matching version of the testing string that exists in the list.
                    # # This is the default because this will most often be used to check if a user's argument matches
                    # # # a predefined list.
                    # return val
                    # You cannot return the variable in case it is a different object type than the original list item.
                    # # Find the original item in the OG list.
                    locat = working_list.index(sval)
                    ret_val = values_list[locat]
                    return ret_val
    else:
        # The an exact string match.
        if any(val == in_value for val in values_list):
            if string_to_bool(return_input):
                # Return the original string being tested.
                return in_value
            else:
                # Return the exact-matching version of the testing string that exists in the list.
                return next(val for val in values_list if val == in_value)
    # Else, if no matches, return False
    return False


def reverse_dict(dictionary: dict):
    """Takes an input dictionary and reverses the keys and values.
    Input dictionary values do not need to be unique, and they can be both individual and list types.
    """
    # Create a defaultdict to store reversed values
    reverse_dictionary = defaultdict(list)

    for key, value in dictionary.items():
        # https://stackoverflow.com/questions/13675296/how-to-overcome-typeerror-unhashable-type-list
        if isinstance(value, list):
            for v in value:
                reverse_dictionary[v].append(key)
        else:
            reverse_dictionary[value].append(key)

    # If all the values in the dict have a len <=1, set them as individual, non_listed values.
    if all(len(v) <= 1 for v in reverse_dictionary.values()):
        reverse_dictionary = {
            k: v[0] if v else None for k, v in reverse_dictionary.items()
        }

    # Convert defaultdict item back to a regular dictionary
    dict_return = dict(reverse_dictionary)
    return dict_return


def statedict():
    """Dictionary with the state abbreviations: full-length state name"""
    states = {
        "AK": "Alaska",
        "AL": "Alabama",
        "AR": "Arkansas",
        "AS": "American Samoa",
        "AZ": "Arizona",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DC": "District of Columbia",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "GU": "Guam",
        "HI": "Hawaii",
        "IA": "Iowa",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "MA": "Massachusetts",
        "MD": "Maryland",
        "ME": "Maine",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MO": "Missouri",
        "MP": "Northern Mariana Islands",
        "MS": "Mississippi",
        "MT": "Montana",
        # "NA": "National",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "NE": "Nebraska",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NV": "Nevada",
        "NY": "New York",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "PR": "Puerto Rico",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VA": "Virginia",
        "VI": "Virgin Islands",
        "VT": "Vermont",
        "WA": "Washington",
        "WI": "Wisconsin",
        "WV": "West Virginia",
        "WY": "Wyoming",
    }

    return states


def statedict_reverse():
    """Dictionary with full-length state name: state abbreviations"""
    og_states_dict = statedict()
    reverse_states_dict = reverse_dict(og_states_dict)
    return reverse_states_dict


def st_upperformat(st, suppress_print=False):
    """Takes an input variable designating a US State and makes sure the format is correct & upper case"""
    st = str(st)
    st = " ".join("".join(e for e in st if e.isalnum() or e == " ").split())
    title = str(st).title().replace(" Of ", " of ")
    if title in statedict_reverse():
        # If someone entered the full version of the state instead of abbreviation, set the abbreviation.
        # # Use the "of" catch to ensure DC works
        st = statedict_reverse()[title]
    stfrmt = (st.upper().replace(" ", ""))[:2]
    if stfrmt in statedict():
        pass  # Everything checks out.
    else:
        stfrmt = None
        if suppress_print is False:
            print(
                "Input state variable",
                st,
                "is an invalid entry. Re-assign the state abbreviation string & try again.",
            )
    return stfrmt


def stabv2fulllen(st, suppress_print=False):
    """Takes an abbreviation (EX: AL) designating a US State input variable and returns its long form. EX: Alabama"""
    stfrmt = st_upperformat(st, suppress_print=suppress_print)
    state_dict = statedict()
    if stfrmt in state_dict:
        longform = state_dict[stfrmt]
    else:
        longform = None
        if suppress_print is False:
            print(
                "Input state variable",
                st,
                "is an invalid entry. Re-assign the state long-form string & try again.",
            )

    return longform


def fips_state_converter(
    st_or_fips_input_var,
    state_to_fips=True,
    full_state_name=False,
    suppress_print=False,
):
    """Takes an input variable designating a US State and returns its FIPS Code in text format
    OR takes a FIPS Code and returns a US State name or abbreviation."""
    st_abv = st_upperformat(
        st_or_fips_input_var, suppress_print=True
    )  # suppress_print=suppress_print)
    fips_state_dict = {
        "AL": "01",
        "AK": "02",
        "AZ": "04",
        "AR": "05",
        "CA": "06",
        "CO": "08",
        "CT": "09",
        "DE": "10",
        "FL": "12",
        "GA": "13",
        "HI": "15",
        "ID": "16",
        "IL": "17",
        "IN": "18",
        "IA": "19",
        "KS": "20",
        "KY": "21",
        "LA": "22",
        "ME": "23",
        "MD": "24",
        "MA": "25",
        "MI": "26",
        "MN": "27",
        "MS": "28",
        "MO": "29",
        "MT": "30",
        "NE": "31",
        "NV": "32",
        "NH": "33",
        "NJ": "34",
        "NM": "35",
        "NY": "36",
        "NC": "37",
        "ND": "38",
        "OH": "39",
        "OK": "40",
        "OR": "41",
        "PA": "42",
        "RI": "44",
        "SC": "45",
        "SD": "46",
        "TN": "47",
        "TX": "48",
        "UT": "49",
        "VT": "50",
        "VA": "51",
        "WA": "53",
        "WV": "54",
        "WI": "55",
        "WY": "56",
        "AS": "60",
        "GU": "66",
        "MP": "69",
        "PR": "72",
        "VI": "78",
        "DC": "11",
    }
    if string_to_bool(state_to_fips) is False or st_abv is None:
        # The user wants to go from FIPS to state OR invalid entry.
        fips_reverse_dict = reverse_dict(fips_state_dict)
        # https://stackoverflow.com/questions/733454/best-way-to-format-integer-as-string-with-leading-zeros
        in_fips = str(st_or_fips_input_var).zfill(2)
        if in_fips in fips_reverse_dict:
            # Get the ST abv of the input FIPS.
            item_to_return = st_upperformat(fips_reverse_dict[in_fips])
            if string_to_bool(full_state_name) is True:
                item_to_return = stabv2fulllen(item_to_return)
        else:
            item_to_return = None
            if string_to_bool(suppress_print) is False:
                print(
                    ("'" + st_or_fips_input_var + "'"),
                    "is an invalid entry for ST ~ FIPS conversion. Please re-enter and retry.",
                )
    else:
        # The user wants to go from State to FIPS Code.
        item_to_return = fips_state_dict[st_abv]

    return item_to_return
