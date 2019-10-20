# python3 Monitor.py
'''
1. Identifies the npm packages that are matching the criteria : >10k monthly downloads
2. Read  status 
3. Get New Issues for the packages --- save in MongoDB
4. Get New Pull Requests --- save in MongoDB
5. Get New authors --- save in MongoDB
6. Update status 
7. Call processor script
'''
import pymongo, json, gzip
from Get_project import get_project
from Update_status import update_status 

if __name__ == '__main__':
	# Get list of packages matching the criteria
	update = input('Do You want to Update the Project List? (y/*)')
	if update == 'y':

		project_list = get_project(10000)
		# save project names in a file
		print ('Saving package list .......\n')
		with gzip.open('./data/pkglist.csv.gz', 'wt') as f:
			f.write(','.join(project_list))
	else:
		print ('Using Old List ......... \n')
		with gzip.open('./data/pkglist.csv.gz', 'rt') as f:
			project_list = (f.read()).split(',')



	print('Updating Current Status ............\n')
	update_status('./data/status.json', project_list)


