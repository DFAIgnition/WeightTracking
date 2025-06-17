
###############################################################################################
# getProjectMenu
###############################################################################################
def getProjectMenu():
	"""
	Called by the CORE_P.Menu module, to build the project menu for this application
	Returns: {'menu_header':menu_header, 'menu_items':menu_items}
		
	"""
	project_name	= system.project.getProjectName()
	menu_header		= 'Menu'
	
	menu_items = [
		{'label': "Overview",		'icon':"material/aspect_ratio",	"target": "/main"},
		{'label': "Weights By Month",		'icon':"material/calendar_today",	"target": "/materials"},
		{'label': "Weights By Day",		'icon':"material/event",	"target": "/weightsbyday"},
		{'label': "Admin",				'icon':"material/settings",		"target": "", "items":[
			{'label': "Filler Setup",		'icon':"material/settings",	"target": "/admin",  'permission_code':'SITEADMIN', 'project_name':project_name},
			{'label': "User Admin",					'icon':"material/settings",		"target": "/useradmin", 		'permission_code':'SITEADMIN', 'project_name':project_name},
			{'label': "Manual Aggregator",			 'icon':"material/calculate",		"target": "/aggregator", 		'permission_code':'SITEADMIN', 'project_name':project_name}
		]},			
	]
	
	return {'menu_header':menu_header, 'menu_items':menu_items}