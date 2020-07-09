This repository contains the code used for extracting surface names from the Wikipedia XML dump. The code is largely based on [this](https://github.com/jeffheaton/article-code/blob/master/python/wikipedia/wiki-basic-stream.py)
and [this](https://github.com/CyberZHG/wiki-dump-reader). 

* To use this repository, first install all the requirements and activate the virtual environment.
* Before running the code, ensure that the paths in all the files are correct.
* The feeder script splits the wikipedia dump into chunks to feed to the python scripts.
* To run the id-extractor or index extractor or text-extractor, simply change the corresponding line in the feeder sript.
* The index-extractor outputs the list of indices which will be used for further extraction.
* The id-extractor outputs the article ids and article names for the articles and redirects.
* The text-extractor outputs the sentences and surface names.
* The surface-extractor outputs the frequencies of the surface names for every article. The input to the surface-extractor must be sorted based on the destination entity corresponding to the surface name. Since the csv file would be very large, you might have to use external sorting.