import pymongo, json, sys
'''
Scrape MongoDB of issues for updating current status

'''

#progress bar
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '%'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

flag = input('Do You Want to Update the Whole status file? (y/*) :')

try:
	with open('status.json', 'r') as f:
		status = json.load(f)
except:
	status = {'pkglist':[], 'repodict':{}, 'issue_count':{}, 'deleted_pkgs':[]}
	

client = pymongo.MongoClient(host="da1.eecs.utk.edu")

db = client ['NPM_Popular_Package_Download']
coll = db['Issues']
l = coll.count()
j = 0

issue_dict = {}
repodict  = {}
pkglist = []

for r in coll.find():
	r.pop('_id', None)
	j += 1
	printProgressBar(j, l, prefix = 'Progress:', suffix = 'Complete', length = 50, decimals = 2)
	url = r['issue']['repository_url'].replace('https://api.github.com/repos/','')
	try:
		if issue_dict[url] < int(r['issue']['number']):
			issue_dict[url] =  int(r['issue']['number'])
	except:
		issue_dict[url] =  int(r['issue']['number'])

	if flag.lower() == 'y':
		pkg = r['packages']
		if url not in repodict.keys():
			repodict[url] = pkg
			pkglist = list(set(pkglist + pkg))



if flag.lower() == 'y':
	status['pkglist'] = pkglist
	status['repodict']	= repodict

status['issue_count'] = issue_dict

with open('status.json', 'w') as f:
	status = json.dump(status, f)