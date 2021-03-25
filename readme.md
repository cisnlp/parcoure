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
-------------------------------------------------------------------------------------------
In this guide We will download a parallel corpora in CES format and set up ParCourE over it. 
we will download a small version of bible corpus from opus(www.opus.com) and setup ParCourE over it.

setup python environment
-----

- install python dependencies:
Using Anaconda you can create an environment having the required dependencies using following commands:

`conda env create --file dependencies.yaml`

- Switch to the newly created environment:
`conda activate ParCourE`

if you don't use Anaconda you will have to install the dependencies listed in dependencies.yaml file in your environment of choice.

Download corpus
-----

Download the following files from here and extract them. You can of course download the corpora of your choice in languages of your choice.

Setup Elasticsearch
-----
Install Elasticsearch from https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html and run it, then add
its address to the config file (see below). Elasticsearch uses port number 9200 by default, if you change it you have to also modify it
in config file. Also make sure that Elasticsearch is accessible from ParCourE's machine.


edit the config.ini file
-----
set the following: 
 - ces_corpus_dir: A directory containing the downloaded corpus files in CES format. The toy example will include the following files, from the extracted files above: 
    de-en.xml
    de-pes.xml
    en-pes.xml
    English-WEB.xml
    English.xml
    Farsi.xml
    German.xml
 - ces_alignment_files: Aomma separated list of files that correspond to sentence alignments. in our case it would be `de-pes.xml,de-en.xml,en-pes.xml`
 - parcoure_data_dir: Provide ParCourE with a directory  where it can keep its data and configuration files
 - elasticsearch_address: Ip and port of Elasticsearch.
 


prepare ParCourE
------
-Export the absolute path to the config.ini file. for example if you have downloaded ParCourE to your user's directory. It sould be something like "/home/my_user/parcoure/config.ini"

`export CONFIG_PATH="/absolute/path/to/config.ini"`

run the prepare script giving the config file as its parameter. The script will take the following steps:
- Convert the corpus to the format the ParCourE understands. Since at this stage ParCourE is creating the new corpora files, "file not found warnings" are negligible
- Index the corpus with elastic search
- Create word level alignments
- Extract lexicon
- Extract statistics

`python -m prepare -c config.ini`



Run ParCourE
-----
- Set FLASK_SECRET_KEY which is a hard to guess secret string in app/run.sh file