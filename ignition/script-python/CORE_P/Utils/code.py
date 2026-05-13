import inspect
from time import sleep
from java.lang import System
from java.net import URLEncoder
import json
import urllib
import re
import sys
import traceback

###############################################################################################
# boolToBit
###############################################################################################
def boolToBit(a):
	"""
	Take a boolean (true/false), and return a 1 or a 0 (for storing in database)
	Arguments:
		self: A reference to the component that is invoking this function.
	"""
	if (a is True):
		return 1
	else:
		return 0 

###############################################################################################
# errorPopup 
###############################################################################################
def errorPopup(a):
	"""
	Displays a standard error popup box (Views->CORE_V/Utils/ErrorPopup), with useful things like including the 
	error string of any thrown exceptions, and the line number and function this was called from
	
	Arguments:
		a: an extra bit of descriptive text to display with the error message
	"""
	
	exc_type, exc_obj, tb = sys.exc_info()
	
	if tb is None:
		lineno = ''
	else:
		lineno = tb.tb_lineno
		    
	system.perspective.openPopup("error",'CORE_V/Utils/ErrorPopup', 
			params = {'error':a + "\n\n" + str(sys.exc_info()[1]) + '\n\n' + str('')+ str(sys._getframe().f_back.f_code.co_filename)+ ': Line ' + str(lineno) + " (" + str(sys._getframe().f_back.f_lineno) + ")" },    
			showCloseIcon = True, resizable = False
	)
	
###############################################################################################
# getError - same as what is shown in errorPopup, but for whatever other use you want it for
###############################################################################################
def getError():
	"""
	Gets the useful error info that you get in errorPopup, but just returns it as a text string
	for whatever other use you want it for (generally something like outputting the error to the logs)
	
	Arguments:
		None
	"""
	exc_type, exc_obj, tb = sys.exc_info()
	
	if tb is None:
		lineno = ''
	else:
		lineno = tb.tb_lineno
		    
	return str(sys.exc_info()[1]) + '\n' + str('')+ str(sys._getframe().f_back.f_code.co_filename)+ ': Line ' + str(lineno) + " (" + str(sys._getframe().f_back.f_lineno) + ")" 
			
	
###############################################################################################
# warningPopup - displays a standard warning message
###############################################################################################
def warningPopup(a):
	"""
	Displays a standard warning popup box (Views->CORE_V/Utils/WarningPopup). Kinda like the 
	errorPopup, but less dramatic (orange instead of red, no error codes). Call it to let the 
	user know they might be doing something wrong
	
	Arguments:
		a: the descriptive text to display indicating what the problem was
	"""
	system.perspective.openPopup("warning",'CORE_V/Utils/WarningPopup', 
			params = {'error':a },    
			showCloseIcon = True, resizable = False
	)
    	
###############################################################################################
# successPopup - displays a standard success message
###############################################################################################
def successPopup(a):
	"""
	Like the error and warning popups, but green - use it to notify the user of good things. 
	(Because it's always good to give user feedback so they know where they stand). 
	Note, another less intrusive way to do this is to use the 'showSuccess' function - this 
	lets you show success by, for example, momentarily changing the text of a save button 
	to 'Saved!', to indicate success without making the user click something extra.
	
	Arguments:
		a: the descriptive text to display indicating what wonderful thing just happened
	"""
	
	system.perspective.openPopup("success",'CORE_V/Utils/SuccessPopup', 
			params = {'error':a },    
			showCloseIcon = True, resizable = False
	)

###############################################################################################
# helpPopup - displays a standard success message
###############################################################################################
def helpPopup(message,title='Help'):
	"""
	This is the popup called byt the Headers/Subheader view, if you pass in a help text parameter. 
	(This is the grey header bar commonly used in our applications). But you can use it too if you want :-)
	It will show a little question mark icon on the far right of the header bar, then pop up the error message if it is clicked. 
	
	Arguments:
		message: text string
		title: optional text string, the title line of the popup
	"""
	system.perspective.openPopup("help",'CORE_V/Utils/HelpPopup', 
			params = {'message':message, 'title':title},    
			showCloseIcon = True, resizable = False, overlayDismiss = True , modal = True
	)
	
###############################################################################################
# showSuccess
###############################################################################################
def showSuccess(self, new_text=""):
	"""
	Make an element (commonly a button), briefly flash green to show success.
	Takes the element in question (usually 'self'), and an optional text string (such as 'Saved!'), to 
	 briefly change the button text to. All colors and text are reverted back once done
	(Because it's always good to give user feedback so they know where they stand, rather than just have nothing change on screen). 
	
	Arguments:
		self: reference to the object to alter
		new_text: text string to temporarily change the button text to
	"""
	# Check that we're not already doing this...
	if (self.props.style.classes == 'CORE_S/Buttons/SaveSuccessful'):
		return
	
	tmp_classes = self.props.style.classes
	try:
		tmp_text = self.props.text  
	except:	
		tmp_text =''
		
	if ('enabled' in self.props):
		tmp_enabled = self.props.enabled
		self.props.enabled = False
	
	self.props.style.classes = "CORE_S/Buttons/SaveSuccessful"
	if (new_text != ""):
		self.props.text = new_text
	sleep(0.5)
	try:
		self.props.text = tmp_text
	except:
		pass
	self.props.style.classes = tmp_classes
	if ('enabled' in self.props):
		self.props.enabled = tmp_enabled
	return
	
###############################################################################################
# showFailure
###############################################################################################
def showFailure(self, new_text=""):
	"""
	Make an element (commonly a button), briefly flash red to show failure.
	Takes the element in question (usually 'self'), and an optional text string (such as 'Failed!'), to 
	 briefly change the button text to. All colors and text are reverted back once done
	(Because it's always good to give user feedback so they know where they stand, rather than just have nothing change on screen). 
	
	Arguments:
		self: reference to the object to alter
		new_text: text string to temporarily change the button text to
	"""
	# Check that we're not already doing this...
	if (self.props.style.classes == 'CORE_S/Buttons/SaveFailed'):
		return
				
	tmp_classes = self.props.style.classes
	tmp_text = self.props.text  
	
	if ('enabled' in self.props):
		tmp_enabled = self.props.enabled
		self.props.enabled = False
	
	self.props.style.classes = "CORE_S/Buttons/SaveFailed"
	if (new_text != ""):
		self.props.text = new_text
	sleep(0.5)
	self.props.text = tmp_text
	self.props.style.classes = tmp_classes
	if ('enabled' in self.props):
		self.props.enabled = tmp_enabled
	return	

###############################################################################################
# flash
###############################################################################################
def flash(self, new_text=""):
	"""
	Make an element briefly flash green to show success. Similar to 'showSuccess', but without trying to 
	change the button text (so you could use this for non-button elements)
	(Because it's always good to give user feedback so they know where they stand, rather than just have nothing change on screen). 
	
	Arguments:
		self: reference to the object to flash
		new_text: deprecated, don't use this
	"""
	tmp_classes = self.props.style.classes
	self.props.style.classes = "CORE_S/Icons/Flash"
	sleep(0.5)
	self.props.style.classes = tmp_classes
	return

###############################################################################################
# datasetToDicts - convert an Ignition dataset into an array of dictionaries, to make it easier to work with
# input: a dataset, such as one returned from a database query
###############################################################################################
def datasetToDicts(data):
	"""
	Convert an Ignition dataset into an array of dictionaries, to make it easier to work with
	(Mainly coz I really hate working with datasets - arrays of dicts are much simpler)
		
	Arguments:
		data: a dataset, such as one returned from a database query
	"""
	output = []
	cols = data.getColumnNames()
	for row in range(data.getRowCount()):
		tmprow = {}
		for col in cols:
			tmprow[str(col)] = (data.getValueAt(row,col))
		output.append(tmprow)
	return output
	

###############################################################################################
# dictToDataset - The reverse of the above - turn an array of dicts back into datasets, because
# that is what some of the Ignition components (such as system.dataset.toExcel) are expecting
###############################################################################################
def dictToDataset(data, columns=None):
	"""
	The reverse of datasetToDicts - if you need to turn your lovely data into a proper Dataset
	(coz that is what some of the Ignition components (such as system.dataset.toExcel) are expecting). 
		
	Arguments:
		data: an array of dicts
		columns: optional, the column names you want in your Dataset (defaults to using all the keys of the first dict)
	"""
	try:		
		if columns is None:
			columns=[]
			
		dataset = []
		if len(data)>0:
			if len(columns) == 0:
				columns = data[0].keys()
		
			for row in data:
		 		new_row = []		
		 		for column in columns:
		 			if column in row:
		 				new_row.append(row[column])
		 			else:
		 				new_row.append(0) # Handle missing data
				dataset.append(new_row)
		
		return system.dataset.toDataSet(columns,dataset)
	except:
		CORE_P.Utils.errorPopup("Error in CORE dictToDataset:" + str(data) + str(columns))

###############################################################################################
# pythonify
###############################################################################################
def pythonify(original):
	"""
	A more generalised version of datasetToDicts, copies an ignition datastructure that might 
	include mixed lists and dicts, and turns them into normal python structures so I can get 
	my head around them (the ignition versions seem to be immutable in certain circumstances, 
	so I go crazy trying to work out why my changes are not sticking)
		
	Arguments:
		original: the object you want converted
	"""
	if hasattr(original, 'items'):  # Check if it behaves like a dictionary
	    copy_dict = {}
	    for key, value in original.items():
	        copy_dict[key] = pythonify(value)
	    return copy_dict
	elif isinstance(original, list) or hasattr(original, '__iter__'):  # Check if it behaves like a list
	    return [pythonify(item) for item in original]
	else:
	    return original


###############################################################################################
# logChanges
###############################################################################################
def logChanges(self, page, details,  # Required parameters
				username=None, txId=None, site_id=None, plant_id=None, line_id=None): # Optional parameters
	"""
	Standard way of logging config changes done on admin screens. 	We should be using this for any operations that change 
	data in an application database, so we can keep track of who is doing what. Believe me, this will save you lots of 
	headaches one day when something goes wrong and all the users claim they never touched anything :-)
	
	Note, don't need to pass in the project name or the username, we get those from the system
	
	You can query the system.dbo.logging table to find data, or just go to the Admin->Audit Log page (and log in as a dev team user): 
	http://10.232.14.213:8088/data/perspective/client/Admin/audit_log
	 
		 
	Example call:
		CORE_P.Utils.logChanges(self, 
								 'EnterIPTData',
								 'Deleting sample ' + str(self.view.params.sample['sample_id']) + ', sample_dt: etc etc ',
								 txId=txId,
								 site_id=self.view.params.site_id,
								 plant_id=self.view.params.plant_id,
								 line_id=self.view.params.line_id,
							)
	
	Arguments:
		self: 		the standard 'self' object, from which we get the currently logged in user. 
	 		  		if calling from a script or something with no user, you can pass in self='', and manually 
			  		pass in a username instead, eg, username='system'
		page: 		the page the action happened on (varchar(32))
		details: 	a text string explaining what was done, eg, 'Saved changes to instrument "NIR 1" at Garden City'
				 	Be descriptive enough to be useful... :-)
		txId: 		optional parameter - if it is included, the change will be saved as part of the 
			  		given transaction id (so, will be rolled back if your transaction fails and doesn't get commited.
		site_id: 	optional, but should be passed in wherever relevant (to make changes easier to find when searching the log)
		plant_id: 	optional, but should be passed in wherever relevant (to make changes easier to find when searching the log)
		line_id: 	optional, but should be passed in wherever relevant (to make changes easier to find when searching the log)
	 
		
	
		data: an array of dicts
		columns: optional, the column names you want in your Dataset (defaults to using all the keys of the first dict)
	"""

	# Use either the currently logged in user (as pulled from the 'self' object'), 
	# or the manually specified username
	if (not username):
		username = self.session.props.auth.user.userName
	
	# Trim details to make sure they fit in th db column...
	details = details[0:511]
	
	parameters = {
		'project_name': system.project.getProjectName(),
		'site_id':		site_id,
		'plant_id':		plant_id,		
		'line_id':		line_id,
		'page':			page,
		'username': 	username,
		'ip_address': 	system.net.getIpAddress(),
		'hostname': 	system.net.getHostName(),
		'details': 		 details
	}
	if (txId is None):
		system.db.runNamedQuery(system.project.getProjectName(), 'CORE_Q/Logging/logConfigChange', parameters, getKey=0)
	else:
		system.db.runNamedQuery(system.project.getProjectName(), 'CORE_Q/Logging/logConfigChange', parameters, tx=txId, getKey=0)
	
	return


###############################################################################################
# valid
###############################################################################################		
def valid(key, dictionary):
	"""
	Simple shortcut to check that a key exists in a dictionary, and that it has something useful in it
	"""
	if ((key in dictionary) and (dictionary[key] is not None) and (dictionary[key] != '')):
		return True
	else:
		return False

###############################################################################################
# is_int
###############################################################################################
def is_int(s):
	"""
	Simple shortcut to check if a variable is an integer
	"""
	try: 
		int(s)
		return True
	except:
		return False
        
###############################################################################################
# is_float
###############################################################################################
def is_float(s):
	"""
	Simple shortcut to check if a variable is a float
	"""
	try: 
		float(s)
		return True
	except:
		return False


###############################################################################################
# Call an API, to get data from another application
###############################################################################################
def call_api(self, path, parameters):
	"""
	Used to call an API to get data from a different project (a way of making data from one project 
	available to another, given that Ignition can only inherit from one project (CORE), while
	still allowing all the logic/code for an application to be contained within that project
	
	See IPT->WebDev->getSummaryReporting for an example API
	
	Arguments:
		self: 
			A reference to the component that is invoking this function. If you are calling this 
			from a server side script, or from the script console, can pass in '' instead and it 
			will default to http://localhost:8088
		path: 
			The path to the WebDev code you want to call - eg, /system/webdev/IPT/getSummaryReporting
			(you can get this by right-clicking on the resource and going 'Copy Mounted Path')
		parameters: 
			The data you want to pass through, as a dict
			
	Returns: 
		Whatever your function wants to return, as JSON. Eg:
			import json	
			return {'json': json.dumps(results)}
			
	"""	
	# If we're running on a remote server (eg, the production server), this should give us the address
	# Otherwise, we default to localhost, so things work in our dev environments
	try:
		address = self.session.props.gateway.address
	except:
		address = ''
	
	if (not address):
		address = 'http://localhost:8088'
	
	address = address + path
	
	# URL encode all values in the params dict
	encoded_params = {}
	for key, value in parameters.items():
	    if value is not None:
	        encoded_params[key] = urllib.quote(str(value)) # Convert value to string before encoding	
				
	# Create a client
	client = system.net.httpClient()
	
	# Make the API request
	response = client.get(address, params=encoded_params)
	
	# Return the json response
	return response.json
	
###############################################################################################
# Call an API, to get data from another application
###############################################################################################
def hitcount(self):
	"""
	Records a page view in the system.dbo.hitcount table
	
	Note, you should never really need to call this, if you're using the standard setup - 
	it's called automatically from inside the standard header (specifically, the onchange event of CORE_V/Docks/Header/MainHeader->root->SiteDropdown->value)
	when a new page is loaded, or a new site is selected. 
	
	You can view the data from it in the Admin app, eg: 
	http://10.232.14.213:8088/data/perspective/client/Admin/hitcount
			
	Arguments:
		self: any perspective object, really. Just need to get the page and session info from it 
	"""
	#logger = system.util.getLogger("HITCOUNT")	
	project_info 	= system.perspective.getProjectInfo()
	
	# Make sure we only get the first part of the page (excluding any parameters which are passed in). 
	# Eg, "/insights/10/1/1/2023-08-27 00%3A00%3A00.0/2023-08-28 00%3A00%3A00.0" should just be read as "/insights"
	path = self.page.props.path
	parts = re.split(r'/', path, maxsplit=3)
	if len(parts) >= 3:
		path = '/'.join(parts[:2])

	parameters = {
		'project':		project_info["name"],
		'page_url':		path,
		'site_id':		self.session.custom.core_page_data[ self.page.props.pageId ].site_id,
		'screen_width':	self.page.props.dimensions.screen.width,
		'screen_height':self.page.props.dimensions.screen.height,
		'username':		self.session.props.auth.user.userName
	}

	results = system.db.runNamedQuery(project=system.project.getProjectName(), path='CORE_Q/Hitcount/insertHitcount', parameters=parameters)
	
#	logger.warn('HitCount: ' + str(project_name) + ' - ' + str(path) + ' - ' + str(site_id) + ' - ' + str(width) + ' - '  + str(height) + ' - '  + str(user) + str(self.session.props))		
	return 
###############################################################################################
# Logger function to log to console, gateway log and perspective as needed
###############################################################################################
def logger(name, text, level='Error', min_level='Debug', active=True, gui=True, session_id = None, page_id = None):
    """
    Logs a message and, if gui is True, sends it to a Perspective view.
    
    :param name: Name of the logger.
    :param text: Log message text.
    :param level: Level of the log message ('Debug', 'Info', 'Warn', 'Error').
    :param min_level: Minimum log level for the message to be logged.
    :param active: If False, logging is skipped.
    :param gui: If False, Perspective messaging is skipped.
    :param session_id: Used to send message to view
    :param page_id: Used to send message to view
    """
    
    if not active:
        return
        
    message = text

    # If logging an error, capture the active exception and traceback if an exception exists.
    exc_value = sys.exc_info()[1]
    if level == 'Error' and exc_value:
        message += '\n\n' + str(exc_value) + "\n\n" + traceback.format_exc()

    # Define log levels and log only if the level meets the minimum threshold.
    log_levels = ['Trace', 'Debug', 'Info', 'Warn', 'Error']
    if level in log_levels and log_levels.index(level) >= log_levels.index(min_level):
		logger_obj = system.util.getLogger(name)
		log_methods = {
		    'Trace': logger_obj.trace,
		    'Debug': logger_obj.debug,
		    'Info': logger_obj.info,
		    'Warn': logger_obj.warn,
		    'Error': logger_obj.error
		}
		log_method = log_methods.get(level, logger_obj.info)
		log_method(message)
		print(message)  # Also output to console
		
		# If Perspective IDs are available, send the message to a Perspective view.
		if session_id and page_id and gui:
			payload = {"message": message}
			system.perspective.sendMessage("LoggerMessageToPerspective", payload,sessionId=session_id, pageId=page_id)
        
###############################################################################################
# Function to retriev perspective and page id / Used in logger to send messages to a page
###############################################################################################       
def get_perspective_ids():
    """
    Walks the call stack to find a variable named 'self' that has
    'session' and 'page' attributes. If found, returns the corresponding
    session and page IDs. Otherwise, returns (None, None).
    """
    frame = inspect.currentframe()
    try:
        while frame:
            local_vars = frame.f_locals
            if 'self' in local_vars:
                maybe_self = local_vars['self']
                # Check if this 'self' looks like a Perspective context.
                if hasattr(maybe_self, 'session') and hasattr(maybe_self, 'page'):
                    return maybe_self.session.props.id, maybe_self.page.props.pageId
            frame = frame.f_back
    finally:
        # Clean up the frame to avoid reference cycles.
        del frame
    return None, None

###############################################################################################
# Function to retrieve the associated label from a dropdown (because ignition inexplicable 
# doesn't provide a built in way to do this for some reason)
###############################################################################################  
def get_dropdown_label(dropdown):
	"""
	Finds the display label for a selected value from a dropdown options list.
	
	Args:
	    dropdown: the dropdown in question.
	
	Returns:
	    The display label corresponding to the selected value, or the value itself
	    if options are simple, or None if not found or invalid input.
	"""
	selected_value = dropdown.props.value
	options_list = dropdown.props.options
	
	if options_list is None or selected_value is None:
	    return None # Or a default string like "No Selection"
	
	for option in options_list:
		if 'value' in option and str(option['value']) == str(selected_value):
			return option.get('label', selected_value)
		elif option == selected_value:
			return option  
	
	return None
