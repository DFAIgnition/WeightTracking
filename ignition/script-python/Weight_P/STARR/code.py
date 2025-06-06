def getMaterialsFromSTARR(starr_unit_id, start_dt, end_dt):
	# This should return a list of dicts, of the form:
	# [{"value": 'None', "timestamp":Start},{"value": 'None', "timestamp":End}]
	# where value is the material number (or 'None'), and timestamp is the time that material started running. 
	
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