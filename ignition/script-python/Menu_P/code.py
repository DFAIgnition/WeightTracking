
###############################################################################################
# getProjectMenu
###############################################################################################
def getProjectMenu():
	"""
	Called by the CORE_P.Menu module, to build the project menu for this application
	Returns: {'menu_header':menu_header, 'menu_items':menu_items}
		
	"""
	project_name	= system.project.getProjectName()
	menu_header		= 'WEIGHT'
	
	menu_items = [
		{'label': "Weight Tracking",		'icon':"material/linear_scale",	"target": "/main"},
		{'label': "Admin",				'icon':"material/settings",		"target": "", "items":[
			{'label': "Filler Setup",		'icon':"material/settings",	"target": "/admin",  'permission_code':'SITEADMIN', 'project_name':project_name},
			{'label': "User Admin",					'icon':"material/settings",		"target": "/useradmin", 		'permission_code':'SITEADMIN', 'project_name':project_name},
			{'label': "Aggregator Manual",			 'icon':"material/calculate",		"target": "/aggregator", 		'permission_code':'SITEADMIN', 'project_name':project_name}
		]},			
	]
	
	return {'menu_header':menu_header, 'menu_items':menu_items}