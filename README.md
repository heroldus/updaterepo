UpdateRepo
==========

Utility derived from *createrepo* to update a *yum* repository by just updating the sqlite DBs and ignoring the XML metadata files.

Intention
---------

If you want to create standard [yum](http://yum.baseurl.org/) repositories *[createrepo](http://createrepo.baseurl.org/)* is the tool of choice. 
The problem is that if you want to add new RPMs to your repository, *createrepo* reads in the XML metadata files and regenerates the sqlite DBs again instead of reusing them.
This solution does not care about XML metadata (RHel 5.6 and newer does not need them) and just adds new packages to the sqlite DBs which is much faster. Also a cache directory is not required.

Installation
------------

To use *updaterepo* you need the following dependencies:

- *yum* : already installed on RHel / Centos. For debian: 

	sudo apt-get install yum
	 
- *createrepo* :
 
	sudo [yum|apt-get] install createrepo

Usage
-----

	./updaterepo.py /path/to/your/repository
	
Performance
-----------

### Delete Update Performance ###

Create a repository with 15 rpms (ca. 500kb per rpm) using:

	createrepo --update -v -d --skip-stat -c /tmp/empty-cache-dir .
	
Remove 2 rpms:

	rm blabla*.rpm
	
Update repository with createrepo:

	time createrepo --update -v -d --skip-stat -c /tmp/empty-cache-dir .
	
	real	0m0.406s
	user	0m0.248s
	sys 	0m0.090s
	
Same update with updaterepo.py

	time updaterepo.py .
	
	real	0m0.254s
	user	0m0.172s
	sys 	0m0.079s
	
**Result: Nearly 40% faster.**