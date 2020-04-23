SimAlign - Demo
------
Simple flask app to show word alignments. Uses flask as webserver, gunicorn server for production, d3.js for visualization. 



TODOs
------
* add embedding similarities and other information
* add google analytics (GRPD issues...)
* add requirements.txt


DONE
------
* add captcha
* prepare deployment
* get rid of xperchar and do it smarter
* highlight edges when hovering
* add favicons
* add metadata and information
* input validation in form




DEPLOYMENT
------
* Dual Stack :: -> ok
* do not set secret keys in repository! -> ok now
* Port 80  -> 8080 for now
* Access log -> ok
* Flask in Produktion -> Gunicorn, ok
* set proper cachedir for transformer models
* Parameterize  -> ok
* clean setup in terms of requirements.txt etc.
* Resource Requirements
