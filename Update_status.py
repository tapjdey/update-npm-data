'''
Reads and Updates the current status of the NPM packages
status file --- 
pkglist : list of current packages satisfying the criteria
deleted_pkgs : list of packages no longer satisfying the criteria
repodict : GitHub repository of all current and old packages -- key: GitHub repo, value : package names
issue_count : no. of issues already collected for all current and old packages -- key: package names, value: number of issues
'''
import gzip, requests, sys, re, pymongo, json, time, datetime
from requests.auth import HTTPBasicAuth

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

def get_ghome(status, pkglist):
	# Add missing info from replicate database
	miss_pkgs = list(set(pkglist) - set(status['pkglist']))

	# GitHub home page of the package
	repodict = {}
	for pkg in miss_pkgs:
		if pkg in status['deleted_pkgs']:
			status['deleted_pkgs'].remove(pkg)
			continue
		r = requests.get('https://replicate.npmjs.com/'+pkg)
		if r.ok :
			#print ('reading ',pkg)
			obj = r.json()
			#print (obj.keys())
			ghome = ''
			if 'homepage' in obj.keys(): 
				ghome = obj['homepage']
				#print(ghome)
			else:				
				try:
					latest = obj['dist-tags']['latest']
				except:
					latest = max(obj['versions'].keys())

				v = obj['versions'][latest]
				try: 
					ghome = v['repository']['url']
					if type(ghome) != str:
						raise Exception(0)
				except: 
					try:
						 ghome = v['homepage']
						if type(ghome) != str:
							raise Exception(0)
					except:
						try:
							ghome = v['repository']
							if type(ghome) != str:
								raise Exception(0)
						except:
							pass
			


			if ghome == '':
				#print ('not found')
				pass
			else:
				try:
					ghome = re.sub(r'#.*', '', ghome)
				except:
					pass
				#print (ghome)
				try: 
					ghome2 = ghome.replace('www.','').split('.')[1]
					try:
						if ghome.replace('www.','').split('.')[2] =='js':
							ghome2 = ghome2 + '.js'
					except: pass
				except: 
					pass            
				#print ('kklll', ghome2)
				m = re.sub('^com[/:]','',ghome2)
				m = m.split('/tree')[0]
				if '/' not in m:
					try:
						ghome2 = ghome.replace('www.','').split('.')[2]
						try:
							if ghome.replace('www.','').split('.')[2] =='js':
								ghome2 = ghome2 + '.js'
						except:
							pass
						m = re.sub('^com[/:]','',ghome2)
						m = m.split('/tree')[0]
						if '/' not in m:
							pass
					except:
						pass
				if m in repodict.keys():
					repodict[m].append(pkg)
				else:
					repodict[m] = [pkg]
	#print(repodict)
	status['repodict'].update(repodict)
	status['deleted_pkgs'] = list(set(status['deleted_pkgs']).union(set(status['pkglist']) - set(pkglist)))
	status['pkglist'] = list(pkglist)

	return status

def ghSetup():
###################################################
    global gleft, client, db, coll, baseurl, headers, collName, gc

###################################################
    gc = 0
    client = pymongo.MongoClient (host="da1.eecs.utk.edu")
    db = client ['NPM_Popular_Package_Download']
#popular pkgs
    coll = db['Issues']
    collput = db['pullReq']

    gleft = 0
    baseurl = 'https://api.github.com/repos'
    headers = {'Accept': 'application/vnd.github.v3.star+json'}
    headers = {'Accept': 'application/vnd.github.v3+json'}
#do for followers following starred subscriptions orgs gists repos events received_events 
    collName = 'issues?state=all'
    
    return

def wait (left):
  global gc
  while (left < 20):
    l = requests .get('https://api.github.com/rate_limit', auth=(login[gc%len(login)],passwd[gc%len(passwd)]))
    if (l.ok):
      left = int (l.headers.get ('X-RateLimit-Remaining'))
      reset = int (l.headers.get ('x-ratelimit-reset'))
      now = int (time.time ())
      dif = reset - now
      if (dif > 0 and left < 20):
        sys.stderr.write ("waiting for " + str (dif) + "s until"+str(left)+"s\n")
        time .sleep (dif)
    time .sleep (0.5)
  return left  

def get (url, ic=None):
	global gleft, gc
	gleft = wait (gleft)
	entry_list = []
	ic_max = ic

	r = requests .get (url, headers=headers, auth=(login[gc%len(login)], passwd[gc%len(passwd)]))
	gc += 1
	time .sleep (0.5)
	if r.ok :
		gleft = int(r.headers.get ('X-RateLimit-Remaining'))
		links = r.headers.get ('Link')
		try:
			rj = r.json()
		except Exception as e:
			sys.stderr.write('Error in JSON --- '+str(e)+'\n')
			rj = []
		if ic is not None:
			for entry in rj:
				number = int(entry['number'])
				if number > ic:
					entry_list.append(entry)
					if number > ic_max : ic_max = number
		else:
			return rj
	else:
		sys.stderr.write('Connection Error --- '+str(url)+'\n')

	return links, entry_list, ic_max

def collect_issue(n, ic):
	global login, passwd
	n = n.strip()
	ghSetup()

	with open('passfile','r') as f:
		pdict = json.load(f)

	login = pdict['login']
	passwd = pdict['passwd']

	if '.js' in n:
		r = requests.get('https://github.com/' + n)
		if r.ok: 
			pass
		else:
			r = requests.get('https://github.com/' + n.replace('.js',''))
			if r.ok:
				n =  n.replace('.js','')
			else:
				sys.stderr.write (n + ';Repo Not Found\n')

	url1 = baseurl + '/' + n + '/' + collName

	links, data, ic_max = get(url1, ic)

	if data == []:
		return data, ic
	else:
		# Collect while you get data
		page_data = ['']
		while page_data != []:
			#print ('dl',len(data))
			#print (links)
			if links is None:
				break
			links = links.split(',')
			if '; rel="next"' in  links[0]:
				url = links[0] .split(';')[0].replace('<','').replace('>','').strip()
			elif '; rel="next"' in  links[1]:
				url = links[1] .split(';')[0].replace('<','').replace('>','').strip()
			else:
				break
			#print (url)
			links, page_data, ic_page  = get(url, ic)
			if ic_page > ic_max:
				ic_max = ic_page
			data = data + page_data
			

		return data, ic_max


def update_status(statusfile, pkglist):
	# Read current status
	try:
		with open(statusfile, 'r') as f:
			status = json.load(f)
	except:
		status = {'pkglist':[], 'repodict':{}, 'issue_count':{}, 'deleted_pkgs':[]}

	# Get GitHub Home pages and update status
	update = input('Do You want to Update the GitHub Home Pages? (y/*)')
	if update == 'y':


		print ('Getting GitHub Home pages of packages............\n')
		new_status = get_ghome(status, pkglist)

		with open(statusfile, 'w') as f:
			json.dump(new_status, f)


	# Get Issue Counts for repos
	tot = len(status['repodict'].keys())
	count = 0
	print ('Collectng Issues for packages ......... \n')

	PRurl = []

	#f1 = open('issues','w')
	#f2 = open('PR', 'w')

	for k in status['repodict'].keys():
		count += 1
		printProgressBar(count, tot)
		if any(v in pkglist for v in status['repodict'][k]):
			if k in status['issue_count'].keys():
				ic = int(status['issue_count'][k])
			else:
				ic = -1
			# Collect New Issues
			data, ic_max = collect_issue(k, ic)

			new_status['issue_count'].update({k : ic_max})
			i = 0
			for e in data:
				i += 1
				if e == '': continue
				entry = {'packages': status['repodict'][k], 'issue': e, 'number': i }
				if 'pull_request' in e.keys():
					PRurl.append(e['pull_request']['url']+','+','.join(status['repodict'][k]) )
				coll .insert (i, check_keys=False)
				#json.dump(entry, f1)
				#f1.write('\n\n')
	
	#f1.close()		
	print ('Writing New Status File ...........\n')		
		

	with open(statusfile, 'w') as f:
		json.dump(new_status, f)

	print('Collecting Pull Requests ............. \n')
	#print(len(PRurl))
	count = 0
	tot = len(PRurl)
	for u in PRurl:
		count += 1
		printProgressBar(count, tot)
		u = u.split(',')
		url = u[0]
		pkgs = u[1:]

		#print(url)

		t = get(url)
		e = {'pullReq':t, 'packages':pkgs}
		collput .insert (e, check_keys=False)
		#json.dump(e, f2)
		#f2.write('\n\n')

	
	#f2.close()

	return


	
