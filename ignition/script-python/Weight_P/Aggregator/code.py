import system
from java.text import SimpleDateFormat
from java.util import Date, Calendar
from org.apache.commons.math3.stat.descriptive import DescriptiveStatistics

# Helper functions, Move to CORE after done

###############################################################
# SystemLogger
###############################################################
def SystemLogger(LoggerActive, LoggerName, Message):
	if LoggerActive:
	    system.util.getLogger(LoggerName).info(Message)
        
###############################################################
# getWeeksBetween
###############################################################
def getWeeksBetween(startCal, endCal):
	tempCal = startCal.clone()  
	weeks = 0
	while tempCal.before(endCal):
	    tempCal.add(Calendar.WEEK_OF_YEAR, 1)
	    weeks += 1
	return weeks
    
###############################################################
# createWeekCalendar
###############################################################
def createWeekCalendar(baseCal, weeksToAdd):
	cal = Calendar.getInstance()
	cal.setTime(baseCal.getTime())
	cal.add(Calendar.WEEK_OF_YEAR, weeksToAdd)
	return cal
	
	
###############################################################
# Main function - ProcessWeek
###############################################################
def ProcessWeek(Start, End, site_id, scale_id):
	
	
	LoggerActive = False
	
	scale_data = {}
	progress2 = 0
	
	# Retrieve data entries based on site and scale ID.
	entries = system.db.runNamedQuery("Weight_Q/DB_Query/Get_All", {'site_id': site_id, 'scale_id': scale_id})
		
	all_tags = []
	tag_path_mapping = {}
	entry_sp_values = {}
	loop_count  = 0
	
	SystemLogger(LoggerActive, "Weight Tracking", "Entries: {}".format(entries.getRowCount()))
	
	# Extract and map tag names from the entries.
	for entry in system.dataset.toPyDataSet(entries):

		loop_count  += 1
		SystemLogger(LoggerActive, "Weight Tracking", "Scale: {}".format(entry['scale_id']))
		SystemLogger(LoggerActive, "Weight Tracking", "Loop: {}".format(loop_count))
	
		progress2 = float(loop_count) / float(entries.getRowCount()) * 100
		system.util.sendMessage(project="WeightTracking", messageHandler="AggregatorUpdateBarScale", scope='S', payload={"progress": progress2})
	
		default_sp_values = {
					    	    'filler_sp_tag': entry['filler_sp'],
					    	    'filler_sp_high_tag': entry['filler_sp_high'],
					    	    'filler_sp_low_tag': entry['filler_sp_low']
					    	}
		
		
		original_tags = [	(entry['scale_weight'], 			'scale_weight'),
						    (entry['line_material'], 			'line_material'),
						    (entry['filler_sp_tag'], 			'filler_sp_tag'),
						    (entry['filler_sp_high_tag'], 		'filler_sp_high_tag'),
						    (entry['filler_sp_low_tag'], 		'filler_sp_low_tag'),
						    (entry['filler_reject'], 			'filler_reject'),
						    (entry['filler_metal'], 			'filler_metal'),
						    (entry['filler_reason_over'], 		'filler_reason_over'),
						    (entry['filler_reason_under'], 	'filler_reason_under'),
						    (entry['filler_reason_metal'], 	'filler_reason_metal')		]
		
		# Make sure to only use exisiting tags
		filtered_tags = [(CORE_P.Tags.getFullyQualifiedTagName(tag), key) for tag, key in original_tags if tag is not None and tag != '']
		all_tags, keys = zip(*filtered_tags)
		tag_path_mapping = dict(zip(keys, all_tags))
			
		# Query historical data for the extracted tags.
		history_data = system.tag.queryTagHistory(
		    paths=all_tags,
		    startDate=Start,
		    endDate=End,
		    returnSize=-1,
		    includeBoundingValues=True,
		    noInterpolation=False,
		    ignoreBadQuality=True,
		    columnNames=all_tags,  
		    returnFormat='Tall'
		)
		
		# Prepare data structures for processing.
		all_data = {key: [] for key in tag_path_mapping.keys()}
		last_known_values = {}
		daily_data = {}
		
		# Formatters for date and time.
		sdf_day = SimpleDateFormat("yyyy-MM-dd")
		sdf_hour = SimpleDateFormat("HH")
		sdf_day_hour = SimpleDateFormat("yyyy-MM-dd HH:00:00")
		
		# Process historical data to structure it by day and hour.
		for item in CORE_P.Utils.datasetToDicts(history_data):
		    for key, converted_tag_name in tag_path_mapping.items():
		        if converted_tag_name == item['path']:
					all_data[key].append(item)
		
		
		#######################################################################
		# Materials stuff
		#######################################################################
		materials = []
		material_index = 0		
		try:
			# If we have a tag defined, use that. 
			if ('line_material' in all_data and all_data['line_material']):
			#	SystemLogger(True, "JAY", 'DEBUG: Getting materials from Tags!')		
				materials = CORE_P.Tags.getTagChanges(entry['line_material'], Start, End)
				
				if (len(materials)>0 and materials[0]['timestamp']>Start):
					materials.insert(0, {"value": 'None', "timestamp":Start})
			
			# Else, if we have a link to a STARR unit...work out materials from that instead
			elif(entry['starr_unit_id']):
			#	SystemLogger(True, "JAY", 'DEBUG: Getting materials from STARR!')		
				materials = Weight_P.STARR.getMaterialsFromSTARR(entry['starr_unit_id'], Start, End)
				SystemLogger(True, "JAY", 'DEBUG: ' + str(materials))						
			
			# Otherwise...materials are None
			else:
			#	SystemLogger(True, "JAY", 'DEBUG: Using default materials!' +str(entry['starr_unit_id']))		
				materials = [{"value": 'None', "timestamp":Start},{"value": 'None', "timestamp":End}]
		except:
			SystemLogger(True, "JAY", CORE_P.Utils.getError())			
		
		#######################################################################
		# Process stuff
		#######################################################################		
		all_materials_key = 'All'
		try:
			for key, items in all_data.items():
				material_index = 0		
				#SystemLogger(True, "JAY", str(key))
				for item in items:
				#	SystemLogger(True, "JAY", str(item))
					timestamp = Date.from(item['timestamp'].toInstant())
					calendar_instance = Calendar.getInstance()
					calendar_instance.setTime(timestamp)
					calendar_instance.set(Calendar.MINUTE, 0)
					calendar_instance.set(Calendar.SECOND, 0)
					calendar_instance.set(Calendar.MILLISECOND, 0)
					
					day_key = sdf_day.format(timestamp)
					hour_of_day = calendar_instance.get(Calendar.HOUR_OF_DAY)
					time_start = sdf_day_hour.format(calendar_instance.getTime())
					
					#for tag in ['line_material']:
					#						if tag in tags and tags[tag]:
					#						    # Store the first value directly
					#						    tags[tag] = tags[tag][0]
					#						else:
					#						    # Use the last known or default value
					#						    tags[tag] = last_known_values.get(tag, 'N/A')	
					
					# Work out which material to use
					while ( (material_index < (len(materials)-1))  and (timestamp >= materials[material_index + 1]['timestamp']) ):
						material_index = material_index + 1 
						
					material = materials[material_index]['value']
					
					
					if day_key not in daily_data:
					   # daily_data[day_key] = {hour: {'time_start': '', 'scale_weight_values': []} for hour in range(24)}
					    daily_data[day_key] = {hour: {} for hour in range(24)}
					
					if material not in daily_data[day_key][hour_of_day]:
						daily_data[day_key][hour_of_day][material] = {'time_start': '', 'scale_weight_values': []}
						
					if all_materials_key not in daily_data[day_key][hour_of_day]:
						daily_data[day_key][hour_of_day][all_materials_key] = {'time_start': '', 'scale_weight_values': []}
						
					if 'time_start' not in daily_data[day_key][hour_of_day][material] or not daily_data[day_key][hour_of_day][material]['time_start']:
						daily_data[day_key][hour_of_day][material]['time_start'] = time_start
					if 'time_start' not in daily_data[day_key][hour_of_day][all_materials_key] or not daily_data[day_key][hour_of_day][all_materials_key]['time_start']:
						daily_data[day_key][hour_of_day][all_materials_key]['time_start'] = time_start
						
					if key not in daily_data[day_key][hour_of_day][material]:
					    daily_data[day_key][hour_of_day][material][key] = []
					if key not in daily_data[day_key][hour_of_day][all_materials_key]:
					    daily_data[day_key][hour_of_day][all_materials_key][key] = []
					    
					daily_data[day_key][hour_of_day][material][key].append(item['value'])
					daily_data[day_key][hour_of_day][all_materials_key][key].append(item['value'])
					
					if key == 'scale_weight':
					    daily_data[day_key][hour_of_day][material]['scale_weight_values'].append(item['value'])
					    daily_data[day_key][hour_of_day][all_materials_key]['scale_weight_values'].append(item['value'])
					    #daily_data[day_key][hour_of_day][material]['scale_weight_values'].append(item['timestamp'])
		except:
			SystemLogger(True, "JAY", CORE_P.Utils.getError())				

	#	SystemLogger(True, "JAY", "Materials:" + str(materials))
		
		#SystemLogger(True, "JAY", "Daily Data:" + str(daily_data))
		#return #DEBUG
		
# OLD VERSION		
#				if day_key not in daily_data:
#				    daily_data[day_key] = {hour: {'time_start': '', 'scale_weight_values': []} for hour in range(24)}
#				    
#				if 'time_start' not in daily_data[day_key][hour_of_day] or not daily_data[day_key][hour_of_day]['time_start']:
#					daily_data[day_key][hour_of_day]['time_start'] = time_start
#					SystemLogger(LoggerActive, "Weight Tracking", "Time: {}".format(time_start))
#				
#				if key not in daily_data[day_key][hour_of_day]:
#				    daily_data[day_key][hour_of_day][key] = []
#				
#				daily_data[day_key][hour_of_day][key].append(item['value'])
#				
#				if key == 'scale_weight':
#				    daily_data[day_key][hour_of_day]['scale_weight_values'].append(item['value'])
#				    
		#LoggerActive = True
	#	SystemLogger(True, 'JAY', str(daily_data.items()))
		# Aggregate and calculate statistics for each tag.
		for day, hours in daily_data.items():
		
			#for hour, tags in hours.items():
			for hour, materials in hours.items():
			
				for material, tags in materials.items():
				
					# Setting set points:
					for sp_tag in ['filler_sp_tag', 'filler_sp_high_tag', 'filler_sp_low_tag']:
						if sp_tag in tags and tags[sp_tag]:
						    # Store the first value directly
						    tags[sp_tag] = tags[sp_tag][0]
						else:
						    # Use the last known or default value
						    tags[sp_tag] = last_known_values.get(sp_tag, default_sp_values[sp_tag])	
						    
					# Setting material:
#					for tag in ['line_material']:
#						if tag in tags and tags[tag]:
#						    # Store the first value directly
#						    tags[tag] = tags[tag][0]
#						else:
#						    # Use the last known or default value
#						    tags[tag] = last_known_values.get(tag, 'N/A')	
					tags['line_material'] = material
					    
					# Working on weight Statistics			    
					if 'scale_weight_values' in tags and tags['scale_weight_values']:
						stats = DescriptiveStatistics()
						stats.clear()
						
						count_over_threshold = 0
						count_under_threshold = 0
						count_out_of_threshold = 0
						
							
						for value in tags['scale_weight_values']:
							stats.addValue(value)
							if value > tags['filler_sp_high_tag']:
								count_over_threshold += 1
							if value < tags['filler_sp_low_tag']:
								count_under_threshold += 1
							if value < tags['filler_sp_low_tag'] or value > tags['filler_sp_high_tag'] :
								count_out_of_threshold += 1
								
						tags['scale_id']=entry['scale_id']
						tags['count']=len(tags['scale_weight_values'])
						tags['standard_deviation'] = stats.getStandardDeviation()
						tags['variance'] = stats.getVariance()
						tags['weight_avg'] =  stats.getMean()
						tags['weight_max'] = stats.getMax()
						tags['weight_min'] = stats.getMin()
						tags['weight_range'] = tags['weight_max']-tags['weight_min']
						tags['percentile25'] = stats.getPercentile(25)
						tags['percentile50'] = stats.getPercentile(50)
						tags['percentile75'] = stats.getPercentile(75)
						tags['weight_sum'] = sum(tags['scale_weight_values'])
						tags['weight_target'] = tags['count']*tags['filler_sp_tag']
						tags['weight_diff'] = tags['weight_sum']- tags['weight_target']
						tags['pct_weight_over'] = (count_over_threshold / float(tags['count'])) * 100 if tags['count'] > 0 else 0
						tags['pct_weight_under'] = (count_under_threshold / float(tags['count'])) * 100 if tags['count'] > 0 else 0
						tags['pct_out_of_range'] = (count_out_of_threshold / float(tags['count'])) * 100 if tags['count'] > 0 else 0
						tags['sp_low'] = entry['filler_sp_low']
						tags['sp'] = entry['filler_sp']
						tags['sp_high'] = entry['filler_sp_high']
						tags['design'] = entry['filler_design']
						
					
					# Clean up to save memory.
					del tags['scale_weight_values']
					
					
					# Calculate aggregates and maintain last known values for certain tags.
					for tag, values in tags.items():
					    if not isinstance(values, list):
					        values = [values]  # Ensure values is a list, even if it's a single value
					
					    if tag == 'scale_weight':
					        tags[tag] = sum(values) / len(values) if values else None
					    elif tag in ['filler_reject', 'filler_metal']:
					        tags[tag] = values.count(1)
					    elif tag == 'filler_reason_over':
					        tags[tag] = values.count(1)
					    elif tag == 'filler_reason_under':
					        tags[tag] = values.count(2)
					    elif tag == 'filler_reason_metal':
					        tags[tag] = values.count(3)
					        
					        
					        
					 # Update last known values for next iteration
					for tag in ['filler_sp_tag', 'filler_sp_high_tag', 'filler_sp_low_tag','line_material']:
					    if tag in tags and tags[tag]:
					        last_known_values[tag] = tags[tag]    
					        	                    
		# Remove keys that have no hourly data or less than 2 bags per hour
		for day_key in list(daily_data.keys()):  # Iterate over each day
		    for hour_key in list(daily_data[day_key].keys()):  # Iterate over each hour
		    	for material_key in list(daily_data[day_key][hour_key].keys()):  # Iterate over each material
			        hour_data = daily_data[day_key][hour_key][material_key]
			        # Check if 'count' key exists and if its value is less than 1
			        if 'count' not in hour_data or hour_data['count'] <= 1:
			            del daily_data[day_key][hour_key][material_key]  # Delete the hour bucket
		            
		    # After processing hours, check if the day has any hours left
			if not daily_data[day_key]:  # Check if the day is empty
			    del daily_data[day_key]  # Delete the day if it has no hours
		
		# After processing, add daily_data to scale_data under the current scale_id
		if entry['scale_id'] not in scale_data:
		    scale_data[entry['scale_id']] = {}
		scale_data[entry['scale_id']].update(daily_data)  
		  
	return scale_data
	
###############################################################
# insertOrUpdateBucketData
###############################################################
def insertOrUpdateBucketData(scale_data, start_dt, end_dt):

	LoggerActive = False
	try:
		for scale_id, days_data in scale_data.items():
			SystemLogger(True, "JAY", "scale_id:" + str(scale_id) )
			
			# Delete the old versions of the rowsrows
			txId = system.db.beginTransaction(timeout=5000)
			parameters = {'scale_id':scale_id, 'start_dt':start_dt, 'end_dt':end_dt}
			system.db.runNamedQuery(project=system.project.getProjectName(), path='Weight_Q/DB_Delete/Delete_Aggregate_Rows', parameters=parameters, tx=txId)
			
			# Then add in all the new ones
			for day, hours_data in days_data.items():
				SystemLogger(True, "JAY", "day:" + str(day))	
				for hour, material_data in hours_data.items():
			#		SystemLogger(True, "JAY", "hour:" + str(hour))					
					for material, bucket in material_data.items():
					#	SystemLogger(True, "JAY", "material:" + str(material))						
						updateParams = {
										    'scale_id': bucket['scale_id'],
										    'time_start': bucket['time_start'],
										    'count': bucket.get('count', 0),
										    'weight_avg': round(bucket.get('weight_avg', 0.0),2),
										    'weight_sum': round(bucket.get('weight_sum', 0.0),2),
										    'weight_diff': round(bucket.get('weight_diff', 0.0),2),
										    'pct_weight_over': round(bucket.get('pct_weight_over', 0.0),2),
										    'pct_weight_under': round(bucket.get('pct_weight_under', 0.0),2),
										    'pct_out_of_range': round(bucket.get('pct_out_of_range', 0.0),2),
										    'standard_deviation': round(bucket.get('standard_deviation', 0.0),2),
										    'variance': round(bucket.get('variance', 0.0),2),
										    'weight_range': round(bucket.get('weight_range', 0.0),2),
										    'weight_max': round(bucket.get('weight_max', 0.0),2),
										    'weight_min': round(bucket.get('weight_min', 0.0),2),
										    'percentile25': round(bucket.get('percentile25', 0.0),2),
										    'percentile50': round(bucket.get('percentile50', 0.0),2),
										    'percentile75': round(bucket.get('percentile75', 0.0),2),
										    'reject_metal': bucket.get('reject_metal', 0),
										    'reject_over': bucket.get('reject_over', 0),
										    'reject_under': bucket.get('reject_under', 0),
										    'material': bucket.get('line_material', 'N/A'),
										    'sp_high': round(bucket.get('sp_high', 0.0),2),
										    'sp': round(bucket.get('sp', 0.0),2),
										    'sp_low': round(bucket.get('sp_low', 0.0),2),
										    'sp_high_plc': round(bucket.get('filler_sp_high_tag', 0.0),2),
										    'sp_plc': round(bucket.get('filler_sp_tag', 0.0),2),
										    'sp_low_plc': round(bucket.get('filler_sp_low_tag', 0.0),2),
										    'design': round(bucket.get('design', 50.0),2)
										}
										
#						# Updated SQL query with string formatting
#						checkSql = "SELECT COUNT(*) FROM weight.dbo.aggregated WHERE scale_id = %d AND time_start = '%s' and material = '%s' " % (scale_id, bucket['time_start'], material)
#						
#						# Running the query
#						existingCount = system.db.runScalarQuery(checkSql)
#						
#						if existingCount > 0:
#							system.db.runNamedQuery("Weight_Q/DB_Update/Update_Aggregate_Hourly", updateParams)
#						else:
#					#		SystemLogger(True, "JAY", "Inserting" + str(updateParams))
#							system.db.runNamedQuery("Weight_Q/DB_Insert/Insert_Aggregate_Hourly", updateParams)	
						#system.db.runNamedQuery("Weight_Q/DB_Insert/Insert_Aggregate_Hourly", updateParams)
						system.db.runNamedQuery(project=system.project.getProjectName(), path="Weight_Q/DB_Insert/Insert_Aggregate_Hourly", parameters=updateParams, tx=txId)
							
			system.db.commitTransaction(txId)
			system.db.closeTransaction(txId)					
							
	except:
		SystemLogger(True, "JAY", CORE_P.Utils.getError())		
		system.db.rollbackTransaction(txId)	
		system.db.closeTransaction(txId)	
	SystemLogger(True, "JAY", "Finished processing")		

###############################################################
# GetBuckets
###############################################################
def GetBuckets(Start, End, site_id=0, scale_id=0):

	LoggerActive = False

	progress = 0	

	startCal = Calendar.getInstance()
	startCal.setTimeInMillis(system.date.toMillis(Start))
	endCal = Calendar.getInstance()
	endCal.setTimeInMillis(system.date.toMillis(End))
	
	weeksBetween = getWeeksBetween(startCal, endCal)
	
	for i in range(weeksBetween):
	
		weekStart = createWeekCalendar(startCal, i)
		weekEnd = createWeekCalendar(startCal, i + 1)
		
		 # Adjust weekEnd to include up to midnight
		weekEnd.add(Calendar.DATE, 1)
		weekEnd.set(Calendar.HOUR_OF_DAY, 0)
		weekEnd.set(Calendar.MINUTE, 0)
		weekEnd.set(Calendar.SECOND, 0)
		weekEnd.set(Calendar.MILLISECOND, 0)
		
		weekEnd = weekEnd if weekEnd.before(endCal) else endCal
		
		SystemLogger(LoggerActive, "Weight Tracking", "{}, {}, {}, {}".format(weekStart.getTime(), weekEnd.getTime(), site_id, scale_id))
		
		scale_data = ProcessWeek(weekStart.getTime(),weekEnd.getTime(), site_id, scale_id)
		insertOrUpdateBucketData(scale_data, weekStart.getTime(),weekEnd.getTime())
		
		progress = float(i) / float(weeksBetween) * 100
		system.util.sendMessage(project="WeightTracking", messageHandler="AggregatorUpdateBarWeek", scope='S', payload={"progress": progress})
		
	progress = 100
	system.util.sendMessage(project="WeightTracking", messageHandler="AggregatorUpdateBarWeek", scope='S', payload={"progress": progress})
		
###############################################################
# GetBucketsGlobal
###############################################################
def GetBucketsGlobal(Start, End, site_id=0, scale_id=0):


	LoggerActive = False

	startCal = Calendar.getInstance()
	startCal.setTimeInMillis(system.date.toMillis(Start))
	endCal = Calendar.getInstance()
	endCal.setTimeInMillis(system.date.toMillis(End))
	
	weeksBetween = getWeeksBetween(startCal, endCal)
	
	for i in range(weeksBetween):
	
		weekStart = createWeekCalendar(startCal, i)
		weekEnd = createWeekCalendar(startCal, i + 1)
		
		 # Adjust weekEnd to include up to midnight
		weekEnd.add(Calendar.DATE, 1)
		weekEnd.set(Calendar.HOUR_OF_DAY, 0)
		weekEnd.set(Calendar.MINUTE, 0)
		weekEnd.set(Calendar.SECOND, 0)
		weekEnd.set(Calendar.MILLISECOND, 0)
		
		weekEnd = weekEnd if weekEnd.before(endCal) else endCal
		
		SystemLogger(LoggerActive, "Weight Tracking", "{}, {}, {}, {}".format(weekStart.getTime(), weekEnd.getTime(), site_id, scale_id))
		
		scale_data = ProcessWeek(weekStart.getTime(),weekEnd.getTime(), site_id, scale_id)
		insertOrUpdateBucketData(scale_data,weekStart.getTime(), weekEnd.getTime())
		


###############################################################
# UpdateRejects
# This will be called every hour by a scheduled task
###############################################################
def UpdateRejects():
	
	end_dt = CORE_P.Time.currentTimestampToHour()
	start_dt = CORE_P.Time.adjustTimestamp(end_dt, offset_hours=-3)
	
	# First, get the list of packing lines that have reject tags configured.
	lines = CORE_P.Utils.datasetToDicts(
			system.db.runNamedQuery(
				project=system.project.getProjectName(), 
				path='Weight_Q/Rejects_Q/Get_Lines_With_Reject_Config', 
				parameters={}
			)
		)  
	
	for line in lines:
		ProcessRejects(start_dt, end_dt, line)
		

	return

###############################################################
# ProcessRejects
###############################################################
def ProcessRejects(start_dt, end_dt, line):
	
	hour_start = start_dt
	
	print str(line)
	
	hours = []
	# Go through the time range in one hour blocks, creating an entry for each hour
	# with a list of materials, 'All', and any materials that occurred during that time. 
	while (hour_start < end_dt):
		
		hour_end = CORE_P.Time.adjustTimestamp(hour_start, offset_hours=1)
		
		hour = {'time_start':start_dt,'material':'All', 'metal_count':0, 'weight_count':0}
		
		if (line['metal_reject_tag']):	

			if (line['metal_reject_tag_type'] == 'c'):
				hour['metal_count'] = CORE_P.Tags.getTotalizerUsage(line['metal_reject_tag'], hour_start, hour_end)
			elif (line['metal_reject_tag_type'] == 'b'):
		
				hour['metal_count'] = CORE_P.Tags.countHigh(line['metal_reject_tag'], hour_start, hour_end)
		
		if (line['weight_reject_tag']):
			if (line['weight_reject_tag_type'] == 'c'):
				hour['weight_count'] = CORE_P.Tags.getTotalizerUsage(line['weight_reject_tag'], hour_start, hour_end)
			elif (line['weight_reject_tag_type'] == 'b'):
				hour['weight_count'] = CORE_P.Tags.countHigh(line['weight_reject_tag'], hour_start, hour_end)
				
		parameters = {
		    'line_id':		line['line_id'],
			'time_start':	hour_start,
			'metal_count':	hour['metal_count'], 
			'weight_count':	hour['weight_count'], 
			'material':		hour['material'] 
		}
		
		system.db.runNamedQuery(
			project=system.project.getProjectName(), 
			path='Weight_Q/Rejects_Q/UpsertReject', 
			parameters=parameters
		)
		
		# Move on to the next hour
		hour_start = hour_end
		
		
		
#	
#	# Get all the material tag data, process into one hour blocks.
#	
#	
#	LoggerActive = False
#	
#	scale_data = {}
#	progress2 = 0
#	
#	line['weight_reject_tag']
#	
#	CORE_P.Tags.getTotalizerUsage(tag, start_dt, end_dt)
#	
#	# Retrieve data entries based on site and scale ID.
#	entries = system.db.runNamedQuery("Weight_Q/DB_Query/Get_All", {'site_id': site_id, 'scale_id': scale_id})
#		
#	all_tags = []
#	tag_path_mapping = {}
#	entry_sp_values = {}
#	loop_count  = 0
#	
#	SystemLogger(LoggerActive, "Weight Tracking", "Entries: {}".format(entries.getRowCount()))
#	
#	# Extract and map tag names from the entries.
#	for entry in system.dataset.toPyDataSet(entries):
#
#		loop_count  += 1
#		SystemLogger(LoggerActive, "Weight Tracking", "Scale: {}".format(entry['scale_id']))
#		SystemLogger(LoggerActive, "Weight Tracking", "Loop: {}".format(loop_count))
#	
#		progress2 = float(loop_count) / float(entries.getRowCount()) * 100
#		system.util.sendMessage(project="WeightTracking", messageHandler="AggregatorUpdateBarScale", scope='S', payload={"progress": progress2})
#	
#		default_sp_values = {
#					    	    'filler_sp_tag': entry['filler_sp'],
#					    	    'filler_sp_high_tag': entry['filler_sp_high'],
#					    	    'filler_sp_low_tag': entry['filler_sp_low']
#					    	}
#		
#		
#		original_tags = [	(entry['scale_weight'], 			'scale_weight'),
#						    (entry['line_material'], 			'line_material'),
#						    (entry['filler_sp_tag'], 			'filler_sp_tag'),
#						    (entry['filler_sp_high_tag'], 		'filler_sp_high_tag'),
#						    (entry['filler_sp_low_tag'], 		'filler_sp_low_tag'),
#						    (entry['filler_reject'], 			'filler_reject'),
#						    (entry['filler_metal'], 			'filler_metal'),
#						    (entry['filler_reason_over'], 		'filler_reason_over'),
#						    (entry['filler_reason_under'], 	'filler_reason_under'),
#						    (entry['filler_reason_metal'], 	'filler_reason_metal')		]
#		
#		# Make sure to only use exisiting tags
#		filtered_tags = [(CORE_P.Tags.getFullyQualifiedTagName(tag), key) for tag, key in original_tags if tag is not None and tag != '']
#		all_tags, keys = zip(*filtered_tags)
#		tag_path_mapping = dict(zip(keys, all_tags))
#			
#		# Query historical data for the extracted tags.
#		history_data = system.tag.queryTagHistory(
#		    paths=all_tags,
#		    startDate=Start,
#		    endDate=End,
#		    returnSize=-1,
#		    includeBoundingValues=True,
#		    noInterpolation=False,
#		    ignoreBadQuality=True,
#		    columnNames=all_tags,  
#		    returnFormat='Tall'
#		)
#		
#		# Prepare data structures for processing.
#		all_data = {key: [] for key in tag_path_mapping.keys()}
#		last_known_values = {}
#		daily_data = {}
#		
#		# Formatters for date and time.
#		sdf_day = SimpleDateFormat("yyyy-MM-dd")
#		sdf_hour = SimpleDateFormat("HH")
#		sdf_day_hour = SimpleDateFormat("yyyy-MM-dd HH:00:00")
#		
#		# Process historical data to structure it by day and hour.
#		for item in CORE_P.Utils.datasetToDicts(history_data):
#		    for key, converted_tag_name in tag_path_mapping.items():
#		        if converted_tag_name == item['path']:
#					all_data[key].append(item)
#		
#		
#		#######################################################################
#		# Materials stuff
#		#######################################################################
#		materials = []
#		material_index = 0		
#		try:
#			# If we have a tag defined, use that. 
#			if ('line_material' in all_data and all_data['line_material']):
#			#	SystemLogger(True, "JAY", 'DEBUG: Getting materials from Tags!')		
#				materials = CORE_P.Tags.getTagChanges(entry['line_material'], Start, End)
#				
#				if (len(materials)>0 and materials[0]['timestamp']>Start):
#					materials.insert(0, {"value": 'None', "timestamp":Start})
#			
#			# Else, if we have a link to a STARR unit...work out materials from that instead
#			elif(entry['starr_unit_id']):
#			#	SystemLogger(True, "JAY", 'DEBUG: Getting materials from STARR!')		
#				materials = Weight_P.STARR.getMaterialsFromSTARR(entry['starr_unit_id'], Start, End)
#				SystemLogger(True, "JAY", 'DEBUG: ' + str(materials))						
#			
#			# Otherwise...materials are None
#			else:
#			#	SystemLogger(True, "JAY", 'DEBUG: Using default materials!' +str(entry['starr_unit_id']))		
#				materials = [{"value": 'None', "timestamp":Start},{"value": 'None', "timestamp":End}]
#		except:
#			SystemLogger(True, "JAY", CORE_P.Utils.getError())			
#		
#		#######################################################################
#		# Process stuff
#		#######################################################################		
#		all_materials_key = 'All'
#		try:
#			for key, items in all_data.items():
#				material_index = 0		
#				#SystemLogger(True, "JAY", str(key))
#				for item in items:
#				#	SystemLogger(True, "JAY", str(item))
#					timestamp = Date.from(item['timestamp'].toInstant())
#					calendar_instance = Calendar.getInstance()
#					calendar_instance.setTime(timestamp)
#					calendar_instance.set(Calendar.MINUTE, 0)
#					calendar_instance.set(Calendar.SECOND, 0)
#					calendar_instance.set(Calendar.MILLISECOND, 0)
#					
#					day_key = sdf_day.format(timestamp)
#					hour_of_day = calendar_instance.get(Calendar.HOUR_OF_DAY)
#					time_start = sdf_day_hour.format(calendar_instance.getTime())
#					
#					#for tag in ['line_material']:
#					#						if tag in tags and tags[tag]:
#					#						    # Store the first value directly
#					#						    tags[tag] = tags[tag][0]
#					#						else:
#					#						    # Use the last known or default value
#					#						    tags[tag] = last_known_values.get(tag, 'N/A')	
#					
#					# Work out which material to use
#					while ( (material_index < (len(materials)-1))  and (timestamp >= materials[material_index + 1]['timestamp']) ):
#						material_index = material_index + 1 
#						
#					material = materials[material_index]['value']
#					
#					
#					if day_key not in daily_data:
#					   # daily_data[day_key] = {hour: {'time_start': '', 'scale_weight_values': []} for hour in range(24)}
#					    daily_data[day_key] = {hour: {} for hour in range(24)}
#					
#					if material not in daily_data[day_key][hour_of_day]:
#						daily_data[day_key][hour_of_day][material] = {'time_start': '', 'scale_weight_values': []}
#						
#					if all_materials_key not in daily_data[day_key][hour_of_day]:
#						daily_data[day_key][hour_of_day][all_materials_key] = {'time_start': '', 'scale_weight_values': []}
#						
#					if 'time_start' not in daily_data[day_key][hour_of_day][material] or not daily_data[day_key][hour_of_day][material]['time_start']:
#						daily_data[day_key][hour_of_day][material]['time_start'] = time_start
#					if 'time_start' not in daily_data[day_key][hour_of_day][all_materials_key] or not daily_data[day_key][hour_of_day][all_materials_key]['time_start']:
#						daily_data[day_key][hour_of_day][all_materials_key]['time_start'] = time_start
#						
#					if key not in daily_data[day_key][hour_of_day][material]:
#					    daily_data[day_key][hour_of_day][material][key] = []
#					if key not in daily_data[day_key][hour_of_day][all_materials_key]:
#					    daily_data[day_key][hour_of_day][all_materials_key][key] = []
#					    
#					daily_data[day_key][hour_of_day][material][key].append(item['value'])
#					daily_data[day_key][hour_of_day][all_materials_key][key].append(item['value'])
#					
#					if key == 'scale_weight':
#					    daily_data[day_key][hour_of_day][material]['scale_weight_values'].append(item['value'])
#					    daily_data[day_key][hour_of_day][all_materials_key]['scale_weight_values'].append(item['value'])
#					    #daily_data[day_key][hour_of_day][material]['scale_weight_values'].append(item['timestamp'])
#		except:
#			SystemLogger(True, "JAY", CORE_P.Utils.getError())				
#
#	#	SystemLogger(True, "JAY", "Materials:" + str(materials))
#		
#		#SystemLogger(True, "JAY", "Daily Data:" + str(daily_data))
#		#return #DEBUG
#		
## OLD VERSION		
##				if day_key not in daily_data:
##				    daily_data[day_key] = {hour: {'time_start': '', 'scale_weight_values': []} for hour in range(24)}
##				    
##				if 'time_start' not in daily_data[day_key][hour_of_day] or not daily_data[day_key][hour_of_day]['time_start']:
##					daily_data[day_key][hour_of_day]['time_start'] = time_start
##					SystemLogger(LoggerActive, "Weight Tracking", "Time: {}".format(time_start))
##				
##				if key not in daily_data[day_key][hour_of_day]:
##				    daily_data[day_key][hour_of_day][key] = []
##				
##				daily_data[day_key][hour_of_day][key].append(item['value'])
##				
##				if key == 'scale_weight':
##				    daily_data[day_key][hour_of_day]['scale_weight_values'].append(item['value'])
##				    
#		#LoggerActive = True
#	#	SystemLogger(True, 'JAY', str(daily_data.items()))
#		# Aggregate and calculate statistics for each tag.
#		for day, hours in daily_data.items():
#		
#			#for hour, tags in hours.items():
#			for hour, materials in hours.items():
#			
#				for material, tags in materials.items():
#				
#					# Setting set points:
#					for sp_tag in ['filler_sp_tag', 'filler_sp_high_tag', 'filler_sp_low_tag']:
#						if sp_tag in tags and tags[sp_tag]:
#						    # Store the first value directly
#						    tags[sp_tag] = tags[sp_tag][0]
#						else:
#						    # Use the last known or default value
#						    tags[sp_tag] = last_known_values.get(sp_tag, default_sp_values[sp_tag])	
#						    
#					# Setting material:
##					for tag in ['line_material']:
##						if tag in tags and tags[tag]:
##						    # Store the first value directly
##						    tags[tag] = tags[tag][0]
##						else:
##						    # Use the last known or default value
##						    tags[tag] = last_known_values.get(tag, 'N/A')	
#					tags['line_material'] = material
#					    
#					# Working on weight Statistics			    
#					if 'scale_weight_values' in tags and tags['scale_weight_values']:
#						stats = DescriptiveStatistics()
#						stats.clear()
#						
#						count_over_threshold = 0
#						count_under_threshold = 0
#						count_out_of_threshold = 0
#						
#							
#						for value in tags['scale_weight_values']:
#							stats.addValue(value)
#							if value > tags['filler_sp_high_tag']:
#								count_over_threshold += 1
#							if value < tags['filler_sp_low_tag']:
#								count_under_threshold += 1
#							if value < tags['filler_sp_low_tag'] or value > tags['filler_sp_high_tag'] :
#								count_out_of_threshold += 1
#								
#						tags['scale_id']=entry['scale_id']
#						tags['count']=len(tags['scale_weight_values'])
#						tags['standard_deviation'] = stats.getStandardDeviation()
#						tags['variance'] = stats.getVariance()
#						tags['weight_avg'] =  stats.getMean()
#						tags['weight_max'] = stats.getMax()
#						tags['weight_min'] = stats.getMin()
#						tags['weight_range'] = tags['weight_max']-tags['weight_min']
#						tags['percentile25'] = stats.getPercentile(25)
#						tags['percentile50'] = stats.getPercentile(50)
#						tags['percentile75'] = stats.getPercentile(75)
#						tags['weight_sum'] = sum(tags['scale_weight_values'])
#						tags['weight_target'] = tags['count']*tags['filler_sp_tag']
#						tags['weight_diff'] = tags['weight_sum']- tags['weight_target']
#						tags['pct_weight_over'] = (count_over_threshold / float(tags['count'])) * 100 if tags['count'] > 0 else 0
#						tags['pct_weight_under'] = (count_under_threshold / float(tags['count'])) * 100 if tags['count'] > 0 else 0
#						tags['pct_out_of_range'] = (count_out_of_threshold / float(tags['count'])) * 100 if tags['count'] > 0 else 0
#						tags['sp_low'] = entry['filler_sp_low']
#						tags['sp'] = entry['filler_sp']
#						tags['sp_high'] = entry['filler_sp_high']
#						tags['design'] = entry['filler_design']
#						
#					
#					# Clean up to save memory.
#					del tags['scale_weight_values']
#					
#					
#					# Calculate aggregates and maintain last known values for certain tags.
#					for tag, values in tags.items():
#					    if not isinstance(values, list):
#					        values = [values]  # Ensure values is a list, even if it's a single value
#					
#					    if tag == 'scale_weight':
#					        tags[tag] = sum(values) / len(values) if values else None
#					    elif tag in ['filler_reject', 'filler_metal']:
#					        tags[tag] = values.count(1)
#					    elif tag == 'filler_reason_over':
#					        tags[tag] = values.count(1)
#					    elif tag == 'filler_reason_under':
#					        tags[tag] = values.count(2)
#					    elif tag == 'filler_reason_metal':
#					        tags[tag] = values.count(3)
#					        
#					        
#					        
#					 # Update last known values for next iteration
#					for tag in ['filler_sp_tag', 'filler_sp_high_tag', 'filler_sp_low_tag','line_material']:
#					    if tag in tags and tags[tag]:
#					        last_known_values[tag] = tags[tag]    
#					        	                    
#		# Remove keys that have no hourly data or less than 2 bags per hour
#		for day_key in list(daily_data.keys()):  # Iterate over each day
#		    for hour_key in list(daily_data[day_key].keys()):  # Iterate over each hour
#		    	for material_key in list(daily_data[day_key][hour_key].keys()):  # Iterate over each material
#			        hour_data = daily_data[day_key][hour_key][material_key]
#			        # Check if 'count' key exists and if its value is less than 1
#			        if 'count' not in hour_data or hour_data['count'] <= 1:
#			            del daily_data[day_key][hour_key][material_key]  # Delete the hour bucket
#		            
#		    # After processing hours, check if the day has any hours left
#			if not daily_data[day_key]:  # Check if the day is empty
#			    del daily_data[day_key]  # Delete the day if it has no hours
#		
#		# After processing, add daily_data to scale_data under the current scale_id
#		if entry['scale_id'] not in scale_data:
#		    scale_data[entry['scale_id']] = {}
#		scale_data[entry['scale_id']].update(daily_data)  
#		  
#	return scale_data