from java.util import Calendar, TimeZone, Date
from java.time import Instant, ZoneId, ZonedDateTime
from java.time.format import DateTimeFormatter

def shift_timestamp(timestamp,timezone_str):
	
	# Create ZoneId objects for both time zones
	zoneA = ZoneId.of('UTC')
	zoneB = ZoneId.of(timezone_str)
	
	# Create ZonedDateTime objects for the same instant in both time zones
	zonedDateTimeA = ZonedDateTime.ofInstant(Instant.ofEpochMilli(timestamp), zoneA)
	zonedDateTimeB = ZonedDateTime.ofInstant(Instant.ofEpochMilli(timestamp), zoneB)
	
	# Get the offsets for both ZonedDateTime objects
	offsetA = zonedDateTimeA.getOffset()
	offsetB = zonedDateTimeB.getOffset()
	
	# Calculate the difference in the offsets in total milliseconds
	offsetDifferenceInMillis = (offsetB.getTotalSeconds() - offsetA.getTotalSeconds()) * 1000
	
	adjustedTimestamp = timestamp - offsetDifferenceInMillis
	
	return adjustedTimestamp

def shift_timestampold(timestamp,timezone_str):
	
	# Create a calendar instance and set it to the UTC time
	calendar = Calendar.getInstance(TimeZone.getTimeZone("UTC"))
	calendar.setTime(Date(timestamp * 1000))
	# Get the timezone offset in milliseconds
	target_timezone = TimeZone.getTimeZone(timezone_str)
	offset_milliseconds = target_timezone.getOffset(calendar.getTimeInMillis())
	# Shift timestamp
	timestamp_shift = timestamp+offset_milliseconds

	return timestamp_shift
		
			