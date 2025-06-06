def getMaterialsFromSTARR(starr_unit_id, start_dt, end_dt):
	# This should return a list of dicts, of the form:
	# [{"value": 'None', "timestamp":Start},{"value": 'None', "timestamp":End}]
	# where value is the material number (or 'None'), and timestamp is the time that material started running. 
	
	payload = {'unit_id': starr_unit_id, 'start_dt':start_dt, 'end_dt':end_dt}
	state_list = system.util.sendRequest(project='STARR', messageHandler='getUnitStatesByUnit', payload=payload)
	
	output = [{"value": 'None', "timestamp":start_dt, 'po_number':None}]
	
	for state in state_list:
		if state['state_id']==1:
			output.append({"value": state['material_number'] or 'None', "po_number": state['po_number'] or None, "timestamp":state['start_dt']})
	
	return output