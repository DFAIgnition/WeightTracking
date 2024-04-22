###############################################################################################
# Encode a string to URL. Main use would be for URL calls of projects that accept parameters
###############################################################################################

# 	Example usage:
#	encoded_value1 = encode_to_url("Hello/World!")
#	print(encoded_value1)  # Outputs: "Hello%2FWorld%21"
#
#	encoded_value2 = encode_to_url("Hello/World!", safe='/')
#	print(encoded_value2)  # Outputs: "Hello/World%21"



def encodeToURL(value, safe=''):

    """
    Encodes a string to be safely included in a URL.

    Args:
        value (str): The string to encode.
        safe (str, optional): Characters that should not be quoted. Defaults to an empty string (encode everything).

    Returns:
        str: The URL encoded string.
        
    # Example usage:
    
    encoded_value1 = encode_to_url("Hello/World!")
    print(encoded_value1)  # Outputs: "Hello%2FWorld%21"
    
    encoded_value2 = encode_to_url("Hello/World!", safe='/')
    print(encoded_value2)  # Outputs: "Hello/World%21"
    
    """
    
    encoded_chars = []
    for char in value:
        if char.isalnum() or char in safe:
            encoded_chars.append(char)
        else:
            encoded_chars.append('%{:02X}'.format(ord(char)))
    return ''.join(encoded_chars)
    

def SecondsToString(value):
    # Transform value in seconds to a string showing days/hours/minutes/seconds

    days = value // 86400
    hours = (value % 86400) // 3600
    minutes = (value % 3600) // 60
    seconds = value % 60
    
    time_components = str(hours).zfill(2) + ":" + str(minutes).zfill(2)
    # + ":" + str(seconds).zfill(2)
    
    if days > 0:
        return str(days) + " d " + time_components if days > 0 else time_components
    else:
        return time_components
        
def SecondsToHoursAndMinutes(value):
    # Transform value in seconds to a string showing hours and minutes only

    hours = (value // 3600) % 24  # Modulo 24 to reset hours after every full day
    minutes = (value % 3600) // 60
    
    # Format the time components to a string with zero-filled hours and minutes
    time_components = str(hours) + ":" + str(minutes).zfill(2)
    
    return time_components
    
def SecondsToMinutes(value):

    # Transform value in seconds to a string showing minutes only
    
        minutes = value // 60  # Get the total minutes
        
        # Format the minutes to a string with zero-filling as needed
        time_components = str(minutes) + " m"
        
        return time_components

def SecondsToDaysOrHoursOrMinutesOrSeconds(value):
    # Transform value in seconds to a string showing minutes, hours if minutes exceed 60, or days if hours exceed 24.

    minutes = value // 60
    hours = minutes // 60
    days = hours // 24

    if days > 0:
        # If there are days, show in days, ignoring hours, minutes, and seconds
        return str(days) + " d"
    elif hours > 0:
        # If there are hours but less than a day, show in hours, ignoring minutes and seconds
        return str(hours) + " h"
    elif minutes > 0:
        # If there are minutes but less than an hour, show in minutes, ignoring seconds
        return str(minutes) + " m"
    else:
        # If there are only seconds, show in seconds
        return str(value) + " s"
        

def SecondsToHours(value):
    # Transform value in seconds to a string showing days/hours/minutes/seconds
	
	hours = value // 3600
	return str(hours) + " h "
	