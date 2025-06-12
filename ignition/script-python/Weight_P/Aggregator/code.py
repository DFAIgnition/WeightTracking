import system
import time
from java.text import SimpleDateFormat
from java.util import Date, Calendar
from org.apache.commons.math3.stat.descriptive import DescriptiveStatistics
import json 


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
	
	# This seems to be the list of Fillers/scales (either the specified one, or all of the scales/fillers on the given site
	entries = system.db.runNamedQuery("Weight_Q/DB_Query/Get_All", {'site_id': site_id, 'scale_id': scale_id})
		
	all_tags = []
	tag_path_mapping = {}
	entry_sp_values = {}
	loop_count = 0
	#SystemLogger(LoggerActive, "Weight Tracking", "Entries: {}".format(entries.getRowCount()))
	SystemLogger(True, "Weight Tracking", "Start:" + str(Start) + ", End:" + str(End) + ", site_id:" + str(site_id) + ", scale:" + str(scale_id))
	
	
	#----------------------------------------------------------------------------
	# Go through each filler and map tag names from the entries.
	#----------------------------------------------------------------------------
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
						   # (entry['line_material'], 			'line_material'),
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
		
		
		#----------------------------------------------------------------------------
		# Get the list of material changes, either from a Tag, or from STARR, or a default list on Material = None
		#----------------------------------------------------------------------------
		materials = []
		material_index = 0		
		try:
			# If we have a tag defined, use that. 
			if ('line_material' in all_data and all_data['line_material']):
				materials = CORE_P.Tags.getTagChanges(entry['line_material'], Start, End)
				
				if (len(materials)>0 and materials[0]['timestamp']>Start):
					materials.insert(0, {"value": 'None', "timestamp":Start})
			
			# Else, if we have a link to a STARR unit...work out materials from that instead
			elif(entry['starr_unit_id']):
				materials = Weight_P.STARR.getMaterialsFromSTARR(entry['starr_unit_id'], Start, End)

			# Otherwise...materials are None
			else:
			#	SystemLogger(True, "JAY", 'DEBUG: Using default materials!' +str(entry['starr_unit_id']))		
				materials = [{"value": 'None', "timestamp":Start},{"value": 'None', "timestamp":End}]
		except:
			SystemLogger(True, "JAY", CORE_P.Utils.getError())			
		
		#----------------------------------------------------------------------------
		# Work out the set points/targets for this material. Will be either from a tag value, or from a material default, or a line default
		#----------------------------------------------------------------------------
		material_config = {} # Hold the materials config		
		sp_low_index = 0
		sp_index = 0
		sp_high_index = 0
		for row in materials:
			
			# Work through the filler_sp_tag dataset until we get to the time relevant to this material/po block
			if ('filler_sp_low_tag' in all_data and all_data['filler_sp_low_tag']):
				while (((sp_low_index+1) < len(all_data['filler_sp_low_tag'])) and (all_data['filler_sp_low_tag'][sp_low_index+1]['timestamp'] <= row['timestamp'])):
					sp_low_index += 1
				row['setpoint_low'] = all_data['filler_sp_low_tag'][sp_low_index]['value']
				
			# Work through the filler_sp_tag dataset until we get to the time relevant to this material/po block
			if ('filler_sp_tag' in all_data and all_data['filler_sp_tag']):
				while (((sp_index+1) < len(all_data['filler_sp_tag'])) and (all_data['filler_sp_tag'][sp_index+1]['timestamp'] <= row['timestamp'])):
					sp_index += 1
				row['setpoint'] = all_data['filler_sp_tag'][sp_index]['value']
				
			# Work through the filler_sp_tag dataset until we get to the time relevant to this material/po block
			if ('filler_sp_high_tag' in all_data and all_data['filler_sp_high_tag']):
				while (((sp_high_index+1) < len(all_data['filler_sp_high_tag'])) and (all_data['filler_sp_high_tag'][sp_high_index+1]['timestamp'] <= row['timestamp'])):
					sp_high_index += 1
				row['setpoint_high'] = all_data['filler_sp_high_tag'][sp_high_index]['value']				
			
			# If there are any of the setpoints we didn't manage to get from tags...
			if (('setpoint_low' not in row) or ('setpoint' not in row) or ('setpoint_high' not in row) ):
				# If we don't know what material we have, revert to default values (if we have them)
				if (row['value'] == 'None'):
					if ('setpoint_low' not in row):
						row['setpoint_low']		= entry['filler_sp_low'] or 0
					if ('setpoint' not in row):
						row['setpoint'] 		= entry['filler_sp'] or 0
					if ('setpoint_high' not in row):
						row['setpoint_high']	= entry['filler_sp_high'] or 0
				else:
					
					# Pull the material data out of the database if we haven't yet
					if str(row['value']) not in material_config:
						tmp = CORE_P.Utils.datasetToDicts(system.db.runNamedQuery(project=system.project.getProjectName(), path='Weight_Q/DB_Query/Get_Material', parameters={'material_number':row['value']}))
						if (len(tmp)>0):
							material_config[str(row['value'])] = tmp[0]

					# Then, use either the item limits, or total limits, depending on the line type
					if (str(row['value']) in material_config and material_config[str(row['value'])]):
						if entry['fill_type'] == 'item':
							if ('setpoint_low' not in row):						
								row['setpoint_low']		= material_config[str(row['value'])]['item_lower_limit'] or 0
							if ('setpoint' not in row):
								row['setpoint'] 		= material_config[str(row['value'])]['item_target_weight'] or 0
							if ('setpoint_high' not in row):
								row['setpoint_high']	= material_config[str(row['value'])]['item_upper_limit'] or 0
						elif entry['fill_type'] == 'case':
							if ('setpoint_low' not in row):						
								row['setpoint_low']		= material_config[str(row['value'])]['lower_limit'] or 0
							if ('setpoint' not in row):
								row['setpoint'] 		= material_config[str(row['value'])]['target_weight'] or 0
							if ('setpoint_high' not in row):
								row['setpoint_high']	= material_config[str(row['value'])]['upper_limit'] or 0
	
					else:
						# Defaults, if we couldn't find material info
						if ('setpoint_low' not in row):
							row['setpoint_low']		= entry['filler_sp_low'] or 0
						if ('setpoint' not in row):
							row['setpoint'] 		= entry['filler_sp'] or 0
						if ('setpoint_high' not in row):
							row['setpoint_high']	= entry['filler_sp_high'] or 0	
		
	#	SystemLogger(True, "JAY", 'Material Config: ' + str(material_config))		
		
		#----------------------------------------------------------------------------
		# Process all the tag data in hourly blocks, further broken down into materials/po_numbers
		# all_data = the set of tag data relating to all the tags configured for this filler/scale
		#----------------------------------------------------------------------------		
		all_materials_key = 'All' # This is what will end up in the material column of the database table for the sum of all weights for the hour (not split out by material)
		try:
			for tagname, items in all_data.items():
				material_index = 0		
				#SystemLogger(True, "JAY", str(key))
				for item in items:

					timestamp = Date.from(item['timestamp'].toInstant())
					calendar_instance = Calendar.getInstance()
					calendar_instance.setTime(timestamp)
					calendar_instance.set(Calendar.MINUTE, 0)
					calendar_instance.set(Calendar.SECOND, 0)
					calendar_instance.set(Calendar.MILLISECOND, 0)
					
					day_key = sdf_day.format(timestamp)
					hour_of_day = calendar_instance.get(Calendar.HOUR_OF_DAY)
					time_start = sdf_day_hour.format(calendar_instance.getTime())

					
					# Work out which material to use
					while ( (material_index < (len(materials)-1))  and (timestamp >= materials[material_index + 1]['timestamp']) ):
						material_index = material_index + 1 
					
					material 		= str(materials[material_index]['value'])
					po_number 		= None # Get po number. Will only exist if we are using a STARR link, not a material tag
					if ('po_number' in materials[material_index]): 
						po_number 	= materials[material_index]['po_number']
					materials_key	= str(material) + "_" + str(po_number)
					setpoint 		= materials[material_index]['setpoint']
					setpoint_high 	= materials[material_index]['setpoint_high']
					setpoint_low 	= materials[material_index]['setpoint_low']
					
					
					if day_key not in daily_data:
					   # daily_data[day_key] = {hour: {'time_start': '', 'scale_weight_values': []} for hour in range(24)}
					    daily_data[day_key] = {hour: {} for hour in range(24)}
					
					if materials_key not in daily_data[day_key][hour_of_day]:
						daily_data[day_key][hour_of_day][materials_key] = {'time_start': time_start, 'scale_weight_values': [], 'material':material, 'po_number':po_number, 'setpoint':[], 'setpoint_high':[], 'setpoint_low':[], 'over_threshold':[], 'under_threshold':[], 'out_of_threshold':[]}
						
					if all_materials_key not in daily_data[day_key][hour_of_day]:
						daily_data[day_key][hour_of_day][all_materials_key] = {'time_start': time_start, 'scale_weight_values': [], 'material':all_materials_key, 'po_number':None, 'setpoint':[], 'setpoint_high':[], 'setpoint_low':[], 'over_threshold':[], 'under_threshold':[], 'out_of_threshold':[]}
						
					if tagname not in daily_data[day_key][hour_of_day][materials_key]:
					    daily_data[day_key][hour_of_day][materials_key][tagname] = []
					    
					if tagname not in daily_data[day_key][hour_of_day][all_materials_key]:
					    daily_data[day_key][hour_of_day][all_materials_key][tagname] = []
					    
					daily_data[day_key][hour_of_day][materials_key][tagname].append(item['value'])
					daily_data[day_key][hour_of_day][all_materials_key][tagname].append(item['value'])
					
					# Keep track of the scale weights. This is the key bit...
					if tagname == 'scale_weight':
					    daily_data[day_key][hour_of_day][materials_key]['scale_weight_values'].append(item['value'])
					    daily_data[day_key][hour_of_day][all_materials_key]['scale_weight_values'].append(item['value'])
					    
					    # Keep track of the setpoints and targets, and what was out of range
					    for a in [all_materials_key, materials_key]:
							daily_data[day_key][hour_of_day][a]['setpoint'].append(setpoint)
							daily_data[day_key][hour_of_day][a]['setpoint_high'].append(setpoint_high)
							daily_data[day_key][hour_of_day][a]['setpoint_low'].append(setpoint_low)
						    
							if item['value'] > setpoint_high:
								daily_data[day_key][hour_of_day][a]['over_threshold'].append(item['value'])
							if item['value'] < setpoint_low:
								daily_data[day_key][hour_of_day][a]['under_threshold'].append(item['value'])
							if item['value'] < setpoint_low or item['value'] > setpoint_high :
								daily_data[day_key][hour_of_day][a]['out_of_threshold'].append(item['value'])
							#	count_out_of_threshold += 1

					    
					    #daily_data[day_key][hour_of_day][material]['scale_weight_values'].append(item['timestamp'])
		except:
			SystemLogger(True, "JAY", CORE_P.Utils.getError())				

		
		#----------------------------------------------------------------------------
		# Aggregate and calculate statistics for hourly block
		#----------------------------------------------------------------------------
		material_config = {} # Hold the materials config
		for day, hours in daily_data.items():
		
			#for hour, tags in hours.items():
			for hour, materials_keys in hours.items():
			
				for materials_key, tags in materials_keys.items():
				
#					#----------------------------------------------------------------------------
#					# Work out the set points for this material
#					#----------------------------------------------------------------------------
#					for sp_tag in ['filler_sp_tag', 'filler_sp_high_tag', 'filler_sp_low_tag']:
#						if sp_tag in tags and tags[sp_tag]:
#						    # Store the first value directly
#						    tags[sp_tag] = tags[sp_tag][0]
#						else:
#							# If we don't have a tag configured for this setpoint, use the Material defaults instead
#							if (tags['material'] and tags['material'] != 'All'):
#								# Pull the material data out of the database if we haven't yet
#								if tags['material'] not in material_config:
#									tmp = CORE_P.Utils.datasetToDicts(system.db.runNamedQuery(project=system.project.getProjectName(), path='Weight_Q/DB_Query/Get_Material', parameters={'material_number':tags['material']}))
#									if (len(tmp)>0):
#										material_config[str(tags['material'])] = tmp[0]
#									else:
#										material_config[str(tags['material'])] = None
#								
#								# Then, use either the item limits, or total limits, depending on the line type
#								if (material_config[str(tags['material'])]):
#									if entry['fill_type'] == 'item':
#										if (sp_tag == 'filler_sp_tag'):
#											tags[sp_tag] = material_config[str(tags['material'])]['item_target_weight']
#										elif (sp_tag == 'filler_sp_high_tag'):
#											tags[sp_tag] = material_config[str(tags['material'])]['item_upper_limit']
#										elif (sp_tag == 'filler_sp_low_tag'):
#											tags[sp_tag] = material_config[str(tags['material'])]['item_lower_limit']
#									elif entry['fill_type'] == 'case':
#										if (sp_tag == 'filler_sp_tag'):
#											tags[sp_tag] = material_config[str(tags['material'])]['target_weight']
#										elif (sp_tag == 'filler_sp_high_tag'):
#											tags[sp_tag] = material_config[str(tags['material'])]['upper_limit']
#										elif (sp_tag == 'filler_sp_low_tag'):
#											tags[sp_tag] = material_config[str(tags['material'])]['lower_limit']
#								else:
#									tags[sp_tag] = last_known_values.get(sp_tag, default_sp_values[sp_tag])			
#							# Use the last known or default value
#							else:
#								tags[sp_tag] = last_known_values.get(sp_tag, default_sp_values[sp_tag])	
					    						
					#----------------------------------------------------------------------------
					# Working on weight Statistics			    
					#----------------------------------------------------------------------------
					if 'scale_weight_values' in tags and tags['scale_weight_values']:
						stats = DescriptiveStatistics()
						stats.clear()
						
						count_over_threshold = 0
						count_under_threshold = 0
						count_out_of_threshold = 0
						
							
						for value in tags['scale_weight_values']:
							stats.addValue(value)
#							if value > tags['filler_sp_high_tag']:
#								count_over_threshold += 1
#							if value < tags['filler_sp_low_tag']:
#								count_under_threshold += 1
#							if value < tags['filler_sp_low_tag'] or value > tags['filler_sp_high_tag'] :
#								count_out_of_threshold += 1
								
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
						
						# Things related to targets and setpoints...
						if(materials_key == 'All'):
							# If this is an 'All' block, we need to work out averages for the set points 
							# as there can be different setpoints for different materials now)
							sp_low_stats = DescriptiveStatistics()
							sp_low_stats.clear()
							for value in tags['setpoint_low']:
								sp_low_stats.addValue(value)
							tags['sp_low'] = sp_low_stats.getMean()
							
							sp_high_stats = DescriptiveStatistics()
							sp_high_stats.clear()
							for value in tags['setpoint_high']:
								sp_high_stats.addValue(value)
							tags['sp_high'] = sp_high_stats.getMean()		
							
							sp_stats = DescriptiveStatistics()
							sp_stats.clear()
							for value in tags['setpoint']:
								sp_stats.addValue(value)
							tags['sp'] = sp_stats.getMean()	
						else:	
							
							if 'setpoint_low' in tags and len(tags['setpoint_low'])>0:
								tags['sp_low'] = tags['setpoint_low'][0]
							else:
								tags['sp_low'] = 0
							if 'setpoint_high' in tags and len(tags['setpoint_high'])>0:
								tags['sp_high'] = tags['setpoint_high'][0]
							else:
								tags['setpoint_high'] = 0
							if 'setpoint' in tags and len(tags['setpoint'])>0:
								tags['sp'] = tags['setpoint'][0]
							else:
								tags['setpoint_high'] = 0
						
						#SystemLogger(True, "JAY", 'Count: ' + str(tags['count']) + ', Set Point ' + str(tags['sp']) + ', ' + str(materials_key) + ', Setpoint: ' + str(tags['setpoint']))			
								
						tags['weight_target'] = tags['count']*tags['sp']
						tags['weight_diff'] = tags['weight_sum']- tags['weight_target']
						
						tags['pct_weight_over'] = (len(tags['over_threshold']) / float(tags['count'])) * 100 if tags['count'] > 0 else 0
						tags['pct_weight_under'] = (len(tags['under_threshold']) / float(tags['count'])) * 100 if tags['count'] > 0 else 0
						tags['pct_out_of_range'] = (len(tags['out_of_threshold']) / float(tags['count'])) * 100 if tags['count'] > 0 else 0
												
#						tags['weight_diff'] = tags['weight_sum']- tags['weight_target']
#						tags['sp_low'] = entry['filler_sp_low']
#						tags['sp'] = entry['filler_sp']
#						tags['sp_high'] = entry['filler_sp_high']
#						tags['weight_target'] = tags['count']*tags['filler_sp_tag']
#						tags['pct_weight_over'] = (count_over_threshold / float(tags['count'])) * 100 if tags['count'] > 0 else 0
#						tags['pct_weight_under'] = (count_under_threshold / float(tags['count'])) * 100 if tags['count'] > 0 else 0
#						tags['pct_out_of_range'] = (count_out_of_threshold / float(tags['count'])) * 100 if tags['count'] > 0 else 0
												
						#tags['design'] = entry['filler_design']
						
					
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
# END OF ProcessWeek
	
###############################################################
# insertOrUpdateBucketData
###############################################################
def insertOrUpdateBucketData(scale_data, start_dt, end_dt):

	LoggerActive = False
	try:
		for scale_id, days_data in scale_data.items():
			#SystemLogger(True, "JAY", "scale_id:" + str(scale_id) )
			
			# Delete the old versions of the rowsrows
			txId = system.db.beginTransaction(timeout=5000)
			parameters = {'scale_id':scale_id, 'start_dt':start_dt, 'end_dt':end_dt}
			system.db.runNamedQuery(project=system.project.getProjectName(), path='Weight_Q/DB_Delete/Delete_Aggregate_Rows', parameters=parameters, tx=txId)
			
			# Then add in all the new ones
			for day, hours_data in days_data.items():
				#SystemLogger(True, "JAY", "day:" + str(day))	
				for hour, material_data in hours_data.items():
			#		SystemLogger(True, "JAY", "hour:" + str(hour))					
					for material, bucket in material_data.items():
						#SystemLogger(True, "JAY", "sp_low:" + str(bucket.get('sp_low')))						
																		
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
										    'material': bucket.get('material', None),
										    'po_number': bucket.get('po_number', None),
										    'sp_high': round(bucket.get('sp_high', 0.0),2),
										    'sp': round(bucket.get('sp', 0.0),2),
										    'sp_low': round(bucket.get('sp_low', 0.0),2),
										    'sp_high_plc': 0, #round(bucket.get('filler_sp_high_tag', 0.0),2),
										    'sp_plc': 0, #round(bucket.get('filler_sp_tag', 0.0),2),
										    'sp_low_plc': 0, #round(bucket.get('filler_sp_low_tag', 0.0),2),
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
		weekStart.add(Calendar.DATE, 1)
		weekStart.set(Calendar.HOUR_OF_DAY, 0)
		weekStart.set(Calendar.MINUTE, 0)
		weekStart.set(Calendar.SECOND, 0)
		weekStart.set(Calendar.MILLISECOND, 0)	
				
		
		weekEnd = createWeekCalendar(startCal, i + 1)
		
		 # Adjust weekEnd to include up to midnight
		weekEnd.add(Calendar.DATE, 1)
		weekEnd.set(Calendar.HOUR_OF_DAY, 0)
		weekEnd.set(Calendar.MINUTE, 0)
		weekEnd.set(Calendar.SECOND, 0)
		weekEnd.set(Calendar.MILLISECOND, 0)
		
		weekEnd = weekEnd if weekEnd.before(endCal) else endCal
		weekEnd.set(Calendar.MINUTE, 0)
		weekEnd.set(Calendar.SECOND, 0)
		weekEnd.set(Calendar.MILLISECOND, 0)
		
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
		weekStart.add(Calendar.DATE, 1)
		weekStart.set(Calendar.HOUR_OF_DAY, 0)
		weekStart.set(Calendar.MINUTE, 0)
		weekStart.set(Calendar.SECOND, 0)
		weekStart.set(Calendar.MILLISECOND, 0)		
		
		weekEnd = createWeekCalendar(startCal, i + 1)
		
		 # Adjust weekEnd to include up to midnight
		weekEnd.add(Calendar.DATE, 1)
		weekEnd.set(Calendar.HOUR_OF_DAY, 0)
		weekEnd.set(Calendar.MINUTE, 0)
		weekEnd.set(Calendar.SECOND, 0)
		weekEnd.set(Calendar.MILLISECOND, 0)
		
		weekEnd = weekEnd if weekEnd.before(endCal) else endCal
		weekEnd.set(Calendar.MINUTE, 0)
		weekEnd.set(Calendar.SECOND, 0)
		weekEnd.set(Calendar.MILLISECOND, 0)
		
		SystemLogger(LoggerActive, "Weight Tracking", "{}, {}, {}, {}".format(weekStart.getTime(), weekEnd.getTime(), site_id, scale_id))
		
		scale_data = ProcessWeek(weekStart.getTime(),weekEnd.getTime(), site_id, scale_id)
		insertOrUpdateBucketData(scale_data,weekStart.getTime(), weekEnd.getTime())
		
		
def RecalcAggregates(Start, End, site_id=0, scale_id=0):
	scale_data = ProcessWeek(Start,End, site_id, scale_id)
	insertOrUpdateBucketData(scale_data,Start,End)

###############################################################
# UpdateRejects
# This will be called every hour by a scheduled task
###############################################################
def UpdateRejects():
	
	end_dt = CORE_P.Time.currentTimestampToHour()
	start_dt = CORE_P.Time.adjustTimestamp(end_dt, offset_hours=-(24))
	
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
	# Don't process times in the future (or where the current hour isn't yet finished
	if (end_dt>CORE_P.Time.adjustTimestamp(rounding='hourdown')):
		end_dt = CORE_P.Time.adjustTimestamp(rounding='hourdown')
	
	# Get all the materials from STARR, if we have them	
	materials=[]
	if (line['line_material']):	
		materials = CORE_P.Tags.getTagChanges(line['line_material'], start_dt, end_dt)
		if (len(materials)>0 and materials[0]['timestamp']>hour_start):
			materials.insert(0, {"value": 'None', "timestamp":hour_start})
	elif(line['starr_unit_id']):	
		materials = Weight_P.STARR.getMaterialsFromSTARR(line['starr_unit_id'], start_dt, end_dt)
	
	if (len(materials)>0):
		material = materials[0]['value']
		po_number = materials[0]['po_number']
	materials_index = 0
	
	# First, we need to clear out old rows (can't just update existing, now that we're recording materials as well, 
	# because a material might be changed so that old row needs deleting)
	txId = system.db.beginTransaction(timeout=60000)
	parameters = {'line_id':line['line_id'], 'start_dt':start_dt, 'end_dt':end_dt}
	system.db.runNamedQuery(project=system.project.getProjectName(), path='Weight_Q/DB_Delete/Delete_Reject_Rows', parameters=parameters, tx=txId)
	
	hours = []
	# Go through the time range in one hour blocks, creating an entry for each hour
	# with a list of materials, 'All', and any materials that occurred during that time. 
	try:
		while (hour_start < end_dt):
	
			hour_end = CORE_P.Time.adjustTimestamp(hour_start, offset_hours=1)
			
			# -------------------------------------------------------
			# Do the full hour, not split into materials
			# -------------------------------------------------------
			a = time.time()
			hour = {'time_start':start_dt,'material':'All', 'metal_count':0, 'weight_count':0}

			# Get the metal reject count
			if (line['metal_reject_tag']):	
				if (line['metal_reject_tag_type'] == 'c'):
					hour['metal_count'] = CORE_P.Tags.getTotalizerUsage(line['metal_reject_tag'], hour_start, hour_end)
				elif (line['metal_reject_tag_type'] == 'b'):
					hour['metal_count'] = CORE_P.Tags.countHigh(line['metal_reject_tag'], hour_start, hour_end)

			# Get the weight reject count
			if (line['weight_reject_tag']):
				if (line['weight_reject_tag_type'] == 'c'):
					hour['weight_count'] = CORE_P.Tags.getTotalizerUsage(line['weight_reject_tag'], hour_start, hour_end)
				elif (line['weight_reject_tag_type'] == 'b'):
					hour['weight_count'] = CORE_P.Tags.countHigh(line['weight_reject_tag'], hour_start, hour_end)

			# Save hour to database
			parameters = {
			    'line_id':		line['line_id'],
				'time_start':	hour_start,
				'metal_count':	hour['metal_count'], 
				'weight_count':	hour['weight_count'], 
				'material':		hour['material'] 
			}
			system.db.runNamedQuery(project=system.project.getProjectName(), path='Weight_Q/Rejects_Q/UpsertReject', parameters=parameters, tx=txId)
			
			# -------------------------------------------------------
			# Then, do the materials bit (if there is a material tag or STARR link defined)
			# -------------------------------------------------------
			start = hour_start
			if (materials_index+1) < len(materials):
				end = materials[materials_index+1]['timestamp']
				if (end > hour_end):
					end = hour_end
			
			if(len(materials)>0):
				material = materials[materials_index]['value']
				po_number = materials[materials_index]['po_number']
				key = str(material) + '_' + str(po_number)		# Key is used to collate data points into material/po_number groupings
					 
				# If there were no material changes detected, then the counts will be the same as the All count...
				if ((start == hour_start) and (end == hour_end)):
					if ( materials[materials_index]['value'] != 'None'):
						parameters['material'] = materials[materials_index]['value']
						parameters['po_number'] = materials[materials_index]['po_number']
						system.db.runNamedQuery(project=system.project.getProjectName(), path='Weight_Q/Rejects_Q/UpsertReject', parameters=parameters, tx=txId)
				
				else:
				
					# Go through each change of materials in this hour, and build up a set of reject counts
					# Need to do it this slightly complicated way, because we could see more than one run 
					# of the same material within a one hour window.
					i=0
					vals={}
					
					while end <= hour_end:
						
						# If we have a material, go get the reject counts for it
						if (material != 'None'):
							if key not in vals:
								vals[key] = {'metal_count':	0,'weight_count':	0, 'po_number':po_number, 'material':material}
								 
							if (line['metal_reject_tag']):	
								if (line['metal_reject_tag_type'] == 'c'):
									vals[key]['metal_count'] = vals[key]['metal_count'] +  CORE_P.Tags.getTotalizerUsage(line['metal_reject_tag'], start, end)
								elif (line['metal_reject_tag_type'] == 'b'):
									vals[key]['metal_count'] = vals[key]['metal_count'] +  CORE_P.Tags.countHigh(line['metal_reject_tag'],start, end)
							
							if (line['weight_reject_tag']):
								if (line['weight_reject_tag_type'] == 'c'):
									vals[key]['weight_count'] = vals[key]['weight_count'] +  CORE_P.Tags.getTotalizerUsage(line['weight_reject_tag'], start, end)
								elif (line['weight_reject_tag_type'] == 'b'):
									vals[key]['weight_count'] = vals[key]['weight_count'] + CORE_P.Tags.countHigh(line['weight_reject_tag'], start, end)
						
						# If we've hit the end, stop working on this hour
						if (end == hour_end):
							break
						
						# Otherwise, move on to the next segment
						start = end
						if (materials_index+1) < len(materials):
							materials_index = materials_index + 1
							if (materials_index+1) < len(materials):
								end = materials[materials_index+1]['timestamp']
							else:
								end = hour_end
								
							if (end > hour_end):
								end = hour_end
								
							material = materials[materials_index]['value']
							po_number = materials[materials_index]['po_number']
							key = str(material) + '_' + str(po_number)		# Key is used to collate data points into material/po_number groupings
							
						else:
							end = hour_end
							
					# Go through each material found for this hour, and save it to the database 
					for val in vals:
						parameters = {
								    'line_id':		line['line_id'],
									'time_start':	hour_start,
									'metal_count':	vals[val]['metal_count'], 
									'weight_count':	vals[val]['weight_count'], 
									'material':		vals[val]['material'],
									'po_number':	vals[val]['po_number']
								}
						system.db.runNamedQuery(project=system.project.getProjectName(), path='Weight_Q/Rejects_Q/UpsertReject', parameters=parameters, tx=txId)
			

			
			# Move on to the next hour
			hour_start = hour_end
		
		system.db.commitTransaction(txId)
		system.db.closeTransaction(txId)			
	except:
		system.db.rollbackTransaction(txId)	
		system.db.closeTransaction(txId)	
		print CORE_P.Utils.getError()
	
	end = time.time()	

		