This repository contains the code used for extracting surface names from the Wikipedia XML dump. The code is largely based on [this](https://github.com/jeffheaton/article-code/blob/master/python/wikipedia/wiki-basic-stream.py)
and [this](https://github.com/CyberZHG/wiki-dump-reader). 

* To use this repository, first install all the requirements and activate the virtual environment.
* Before running the code, ensure that the paths in all the files are correct.
* Then run the index-extractor and obtain the list of indices which will be used for further extraction.
* Run the id-extractor to obtain the article ids and article names for the articles or redirects.
* Run the text-extractor to obtain the sentences and surface names.
