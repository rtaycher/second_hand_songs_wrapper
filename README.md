A simple wrapper for [secondhandsongs](http://www.secondhandsongs.com/) database [api](http://www.secondhandsongs.com/wiki/API/Main) of info on various versions and covers of songs.Instead of manually constructing search strings, fetching json, and building models it creates models from functions to fetch certain kinds of data.

Note: The SHS API is still in beta testing! Luckily the library uses data validation(the very nice [voluptuous library](http://pypi.python.org/pypi/voluptuous/)) so it will break by throwing exceptions rather then give back strange results when the api changes. The api does not currently specify a version perhaps because it is in beta.

The classes are based on the data types listed on the [api page](http://www.secondhandsongs.com/wiki/API/Main). The fields match the dictionary keys in the json response, they are also initialized one by one to None before setting them dynamically from the fetched json data to allow static tools such as eclipse/pydev's autocomplete to work on them.
Except for performances, creditedWorks, and releases keys of a ShsArtist. The json api returns the uri where to fetch the data for these keys instead of actual data. The wrapper library stores the uri under performances_uri, creditedWorks_uri, and releases_uri fields and fetches the actual data only when first requested under performances_data, creditedWorks_data, and releases_data. ShsArtist has no performances, creditedWorks, or releases fields.


Each model class has a get_from_resource_id factory function to grab the resource associated with that id:

ex.:second_hand_songs.ShsArtist.get_from_resource_id(360) returns data about "Iggy Pop"

Of course most resources aren't identified by resource_id but by uri so you can also download a resource directly with :

second_hand_songs.getShsResource(uri)

You can also search for a performance or work:

ex.:second_hand_songs.second_hand_search("blackbird", performer="beatles")


