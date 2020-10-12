SimAlign - Demo
------
Simple flask app to show word alignments. Uses flask as webserver, gunicorn server for production, d3.js for visualization. 


Usage
------
Install requirements (not sure whether they are complete). Install simalign (https://github.com/cisnlp/simalign). 

If `CIS=False` in `app/utils.py`, it is easier to test locally (as no BERT models are loaded into memory and also then simalign is not required). 
If you are testing it on CIS servers (like delta). Then you can set `CIS=True`.

Create local secreats (do not put true secrets into the github repo before deploying) like this: 
```bash
export FLASK_SECRET_KEY="neverguessing"
export CAPTCHA_SITE_KEY='createonline'
export CAPTCHA_SECRET_KEY='createonline'
```
You need to create the captcha keys online or you set it to something meaningless (then captcha does not work which is probably not so important at the moment). 

Then set 
`export FLASK_APP=align.py`
and run 
`flask run`. 

Hopefully it should work then. 



Deployment Process
------
to be done



TODOs
------
* add embedding similarities and other information
* add google analytics (GRPD issues...)
* add requirements.txt
* remove unused css
* add caching
* defer loading of javascript
* design logo and improve favicon
* add release script
* update simalign library and reduce environment



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
