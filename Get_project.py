'''
produces list of packages matching the criteria : > k downloads a month

'''

import requests, time

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


def get_project(k):
	#Get list of all npm packages from replicate database
	r = requests.get('https://replicate.npmjs.com/_all_docs?limit=500')
	#r = requests.get('https://replicate.npmjs.com/_all_docs') # URL with all package names

	pkgs = set()
	if r.ok : 
		pagedata  = r.json()
		#n_pkg = pagedata['total_rows']
		n_pkg = 500
		print ('Obtained ',n_pkg, ' NPM packages, Processing........\n')

		# Get downloads for last month
		i = 0

		for item in pagedata['rows']:
			i += 1
			printProgressBar(i, n_pkg)
			# Stop overloading
			if i%500 == 0: 
				time.sleep(1)
			elif i % 10000 == 0:
				time.sleep(10)

			pkg = item['key']
			url = 'https://api.npmjs.org/downloads/point/last-month/'+pkg # URL with download counts
			d = requests.get(url)
			if d.ok:
				dl = d.json()
				if int(dl['downloads']) > k: 
					print('')
					pkgs.add(pkg)
	print()
	return pkgs


if __name__ == '__main__':
	pkgs = get_project(100)
	print(pkgs)






