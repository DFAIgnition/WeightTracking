##########################################################################
# This should return a list of dicts, of the form:
# [{"value": 'None', "timestamp":Start},{"value": 'None', "timestamp":End}]
# where value is the material number (or 'None'), and timestamp is the time that material started running. 
##########################################################################
def getMaterialsFromSTARR(starr_unit_id, start_dt, end_dt):
	
	# Get a couple of days buffer at the start...we want to know what the last material run on the line was, so need to look back beyond the given start dt
	adjusted_start_dt = CORE_P.Time.adjustTimestamp(start_dt, offset_hours=-48)
	
	payload = {'unit_id': starr_unit_id, 'start_dt':adjusted_start_dt, 'end_dt':end_dt}
	state_list = system.util.sendRequest(project='STARR', messageHandler='getUnitStatesByUnit', payload=payload)
	
	output = [{"value": 'None', "timestamp":start_dt, 'po_number':None}]
	
	for state in state_list:
		if state['state_id']==1:
		
			if (state['start_dt']<=start_dt):
				# Only record the details of the last run state that started before the given start_dt
				output[0] = {"value": state['material_number'] or 'None', "po_number": state['po_number'] or None, "timestamp":state['start_dt']}
			else:
				# Then after that, record every new run state
				output.append({"value": state['material_number'] or 'None', "po_number": state['po_number'] or None, "timestamp":state['start_dt']})
	
	return output
	
##########################################################################
# Update aggregates and rejects tables when STARR data changes	
##########################################################################
def STARR_Material_Changed(payload):
	#logger = system.util.getLogger("JAY")
	#logger.warn('DEBUG: Got message from STARR' + str(payload))


	# This message handler should be called whenever a STARR Run state has its Material manually changed
	# (Including, I guess, if a non-run state is changed to a Run state, and the material is manually set)
	unit_id		= int(payload['unit_id'])
	start_dt	= payload['start_dt']
	end_dt		= payload['end_dt']	
	if (not end_dt): # Default to NOW if the Run state is still in progress
		end_dt = CORE_P.Time.currentTimestamp()
	
	#-----------------------------------------------------------------------
	# First, check if this unit is actually used for Weights 
	#-----------------------------------------------------------------------
	parameters = {'starr_unit_id':unit_id}
	scales = CORE_P.Utils.datasetToDicts(system.db.runNamedQuery(
		project=system.project.getProjectName(), 
		path='Weight_Q/DB_Query/Get_Scales_By_STARR_Unit', 
		parameters=parameters))
	
	#logger.warn('DEBUG: Found these scales:' + str(scales))	
	if len(scales)==0:
		return # Nothing to do here
	
	#-----------------------------------------------------------------------
	# Adjust the start and end - start needs to round back to previous hour start, 
	# and end needs to be the end of the hour during which the next run state starts
	# (or two days after the end of this run state, or current, whichever is earliest)
	#-----------------------------------------------------------------------	
	start_dt = CORE_P.Time.adjustTimestamp(start_dt, rounding='hourdown')
	#logger.warn('DEBUG: Adjusted start dt:' + str(start_dt))
	
	# Get the start of the next Run start after the end of this run state, within 48 hours. 
	parameters = {'unit_id':unit_id, 'start_dt':end_dt}
	next_run_state = CORE_P.Utils.datasetToDicts(system.db.runNamedQuery(
					project=system.project.getProjectName(), 
					path='Weight_Q/DB_Query/Get_STARR_Next_Run_State', 
					parameters=parameters))		
	
	if (len(next_run_state) == 0):
		# No next run state found! Adjust to 2 days after end date, rounded up to end of hour
		end_dt = CORE_P.Time.adjustTimestamp(end_dt, offset_hours=48, rounding='hourup')
	else:
		end_dt = CORE_P.Time.adjustTimestamp(next_run_state[0]['start_dt'], rounding='hourup')

	#logger.warn('DEBUG: Adjusted end dt:' + str(end_dt))
	#logger.warn('DEBUG: next_run_state:' + str(next_run_state))
	
	#-----------------------------------------------------------------------
	# Call the recalc function, if we found any scales which use this STARR Unit
	#-----------------------------------------------------------------------
	processed_lines = {}
	for scale in scales:
	#	logger.warn('DEBUG: Updating scale:' + str(scale))
		#system.util.invokeAsynchronous(Weight_P.Aggregator.GetBucketsGlobal, args=(start_dt, end_dt,scale['site_id'],scale['scale_id']))
		system.util.invokeAsynchronous(Weight_P.Aggregator.RecalcAggregates, args=(start_dt, end_dt,scale['site_id'],scale['scale_id']))
		
		# Only need to process each line once (even though it might have multiple fillers/scales
		if (str(scale['line_id']) not in processed_lines):
			system.util.invokeAsynchronous(Weight_P.Aggregator.ProcessRejects, args=(start_dt, end_dt,scale))
			processed_lines[str(scale['line_id'])] = 1
	return		
	