<img src="static/favicon.png" alt="logo" width="30"/> ParCourE
=====

This repository contains code for ParCourE, the Parallel Corpus Explorer. It is a WebApp to browse a word aligned multiparallel corpus.
You can view one instance of ParCourE that runs a word aligned version of the Parallel Bible Corpus by Mayer and Cysouw (2014) [here](http://parcoure.cis.lmu.de/).


## Setup
In this guide we will showcase how to set ParCourE up for a parallel corpus. We will download a parallel corpora in [XCES](https://en.wikipedia.org/wiki/XCES#:~:text=XCES%20is%20an%20XML%20based,corpora%2C%20parallel%20corpora%20and%20other.) format, more specifically a small version of bible corpus from [Opus](https://opus.nlpl.eu/) and set up ParCourE for it. 

### 1. Environment

- Using Anaconda you can create an environment having the required dependencies using following commands:
`conda env create --file dependencies.yaml`

- Switch to the newly created environment:
`conda activate parcoure`

If you don't use Anaconda you will have to install the dependencies listed in `dependencies.yaml` file in your environment of choice.

### 2. Download Corpus

<!-- TODO which files? -->
Download the following files from [the opus website](https://opus.nlpl.eu/bible-uedin.php) and extract them. Alternatively, you can of course download the corpora of your choice in languages of your choice.
- [de-en.xml.gz](https://object.pouta.csc.fi/OPUS-bible-uedin/v1/xml/de-en.xml.gz)
- [de-pes.xml.gz](https://object.pouta.csc.fi/OPUS-bible-uedin/v1/xml/de-pes.xml.gz)
- [en-pes.xml.gz](https://object.pouta.csc.fi/OPUS-bible-uedin/v1/xml/en-pes.xml.gz)
- [en.zip](https://object.pouta.csc.fi/OPUS-bible-uedin/v1/xml/en.zip)
- [de.zip](https://object.pouta.csc.fi/OPUS-bible-uedin/v1/xml/de.zip)
- [pes.zip](https://object.pouta.csc.fi/OPUS-bible-uedin/v1/xml/pes.zip)

After extraction, put the language specific data files and inter language alignment files in one direcotry. In this example we put `` English.xml English-WEB.xml Farsi.xml German.xml en-pes.xml de-en.xml de-pes.xml`` files in a directory called ``CES_Corpus``.

### 3. Elasticsearch

<!-- TODO is setting Elasticsearch up so straight forward? -->
Install Elasticsearch from [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started-install.html) and start the server. Then add
its address to the config file (see below). Elasticsearch uses port number 9200 by default. If you change it you have to also modify it
in config file. Also make sure that Elasticsearch is accessible from ParCourE's machine.

Check if Elasticsearch is accessable (use your id address instead of localhost if you have installed Elasticsearch on another server): 

```bash
$> curl localhost:9200

{
  "name" : "hostName",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "-IGDqOQOSwWnVY-RVHSedg",
  "version" : {
    "number" : "7.9.2",
    "build_flavor" : "default",
    "build_type" : "tar",
    "build_hash" : "dsdfsac4e49417f2da2f244e3e97b4e6e",
    "build_date" : "2019-08-11T00:44:31.62642",
    "build_snapshot" : false,
    "lucene_version" : "5.4.2",
    "minimum_wire_compatibility_version" : "11.8.0",
    "minimum_index_compatibility_version" : "4.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}

```

### 4. Word Aligner

Install Simalign (It is mandatory for the input alignment page to work):
```pip install --upgrade git+https://github.com/cisnlp/simalign.git#egg=simalign```

For alignment of your parallel corpus you can use any word alignment tool you prefer. [Here](http://parcoure.cis.lmu.de/) we used [SimAlign](https://github.com/cisnlp/simalign) for as many languages as possible and [eflomal](https://github.com/robertostling/eflomal) for the remainign languages. 

Some popular word aligners are: 
- [fast_align](https://github.com/clab/fast_align)
- [eflomal](https://github.com/robertostling/eflomal)
- [SimAlign](https://github.com/cisnlp/simalign) 

Currently, to use aligners other than fast_align and eflomal, you should extract word alignments manually 
and put them in `alignments_dir`. 

### 5. Configurations

Set the following in the file `config.ini`: 
 - ces_corpus_dir: A directory containing the downloaded corpus files in CES format. The toy example will include the following files, from the extracted files above: 
    de-en.xml
    de-pes.xml
    en-pes.xml
    English-WEB.xml
    English.xml
    Farsi.xml
    German.xml
 - ces_alignment_files: a comma separated list of files that correspond to sentence alignments. in our case it is `de-pes.xml,de-en.xml,en-pes.xml`
 - parcoure_data_dir: Provide ParCourE with a ABSOLUTE directory path where it can keep its data and configuration files
 - elasticsearch_address: IP and port of Elasticsearch.
 - fast_align_path: Something like "/my_installation_path/fast_align/build/". If you set extra_aligner_path ParCourE will use it for word alignment, otherwise it will use fast_align by default.
 - extra_aligner_path: (optional) Something like "/my_installation_path/eflomal/". If you don't set it, ParCourE will use fast_align to extract word alignments.  <!-- TODO why does it use fast_align and not eflomal by default? -->
 - worker_count: Increasing this number will allow ParCourE to use more CPU cores to extract word alignments resulting in faster word alignment extraction during setup.


### 6. Prepare ParCourE
Run the `prepare.sh` script giving the config file as its parameter. The script will perform the following:
- Convert the corpus to the format the ParCourE understands. Since at this stage ParCourE is creating the new corpora files, "file not found warnings" are negligible
- Index the corpus with Elasticsearch
- Create word level alignments
- Precompute statistics
- Precompute lexicon

```bash
bash ./prepare.sh
```

*optional step*: check the `elasticSearch/indexing.log` file to see if all files have been indexed correctly.

### 7. Run ParCourE
- Set FLASK_SECRET_KEY which is a hard to guess secret string in `execute.sh`
- run ParCourE
```bash
bash ./execute.sh
```
- check out the result at http://localhost:8000/


## References
For more details see the paper: 
```
@article{imani-etal-2021-parcoure,
    title = "{P}ar{C}our{E}: A Parallel Corpus Explorer for a Massively Multilingual Corpus",
    author = {Imani, Ayyoob and 
      Jalili Sabet, Masoud  and
      Dufter, Philipp  and
      Cysouw, Michael  and
      Sch{\"u}tze, Hinrich},
    year = "2021",
    note = "to be published"
}
```


## Feedback
Feedback and Contributions more than welcome! Just reach out to @ayyoobimani, @masoudjs, @pdufter or create an issue or pull-request.


<!--
---------------
## FAQ
-->



## License
Copyright (C) 2020, Ayyoob Imani, Masoud Jalili Sabet, Philipp Dufter

A full copy of the license can be found in LICENSE.

