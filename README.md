UpdateRepo
==========

Utility derived from createrepo to update a Yum Repository by just updating the sqlite DBs and ignoring the XML metadata files.

Intention
---------

If you want to create standard [yum](http://yum.baseurl.org/) repositories *[createrepo](http://createrepo.baseurl.org/)* is the tool of choice. 
The problem is that if you want to add new RPMs to your repository, *createrepo* reads in the XML metadat files and regenerates the sqlite DBs again instead of reusing them.
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

	./updaterepo.py