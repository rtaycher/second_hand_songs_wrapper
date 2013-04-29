from __future__ import print_function
import urllib2
import contextlib
import datetime
import voluptuous
from voluptuous import required, coerce
import json
from types import NoneType
from urllib import urlencode
import re


def _valid_url(url):
    u = re.compile('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')
    if u.match(url):
        return True
    else:
        raise ValueError("Not a valid url.")

def is_valid_url(url):
    u = re.compile('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')
    if u.match(url):
        return True
    else:
        return False

def _youtube_url(url):
    if "youtube.com" in url:
        return True
    else:
        raise ValueError("Not a valid youtube url.")

def is_youtube_url(url):
    if "youtube.com" in url:
        return True
    else:
        return False

def _discogs_url(url):
    if "discogs.com" in url:
        return True
    else:
        raise ValueError("Not a valid discogs url.")

def is_discogs_url(url):
    if "discogs.com" in url:
        return True
    else:
        return False

def _shs_url(url):
    if "secondhandsongs.com" in url:
        return True
    else:
        raise ValueError("Not a valid shs url.")

def is_shs_url(url):
    if "secondhandsongs.com" in url:
        return True
    else:
        return False


class SHSResourceUsedUp(Exception):
    pass

class InvalidSHSJsonData(Exception):
    pass


base_url = "http://www.secondhandsongs.com/"


class SHSDataAcess(object):
    cache = None#to be implemented
    hour_start_time = minute_start_time = datetime.datetime.now()
    hour_shs_requests = minute_shs_requests = 0
    max_hour_shs_requests = 1000
    max_minute_shs_requests = 50

    @classmethod
    def getShsResource(cls, uri):
        x = cls.getSHSData(uri)
        return entityTypeToClass[x["entityType"]](x)

    @classmethod
    def getSHSData(cls, url):
        if cls.cache and url in cls.cache:
            return cls.cache[url]
        else:
            now = datetime.datetime.now()
            timedelta_elapsed_past_minute_mark = now - cls.minute_start_time
            if timedelta_elapsed_past_minute_mark < datetime.timedelta(minutes=1):
                if cls.minute_shs_requests >= cls.max_minute_shs_requests:
                    raise SHSResourceUsedUp("Warning fetched max # of queries per minute.")
            else:
                cls.minute_start_time = now
                cls.minute_shs_requests = 0

            timedelta_elapsed_past_hour_mark = now - cls.hour_start_time
            if timedelta_elapsed_past_hour_mark < datetime.timedelta(hours=1):
                if cls.hour_shs_requests >= cls.max_hour_shs_requests:
                    raise SHSResourceUsedUp("Warning fetched max # of queries per hour.")
            else:
                cls.minute_start_time = now
                cls.minute_shs_requests = 0
            headers = {"Accept": "application/json"}
            request = urllib2.Request(url, headers=headers)
            with contextlib.closing(urllib2.urlopen(request)) as urldata:
                data_string = urldata.read()
            data = json.loads(data_string)
            if cls.cache:
                cls.cache[url] = data
            cls.minute_shs_requests += 1
            if "error" in data:
                raise InvalidSHSJsonData(str(data["error"]))
            return data

class SimpleStringifyAndEqualMethods(object):
    def __unicode__(self):
        return unicode(self.__dict__)
    def __repr__(self):
        return repr(self.__dict__)
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                all([v == other.__dict__[k] for (k, v) in self.__dict__.items()]))

def _fetch_shs_data_on_first_access_getter(base_prop_name):
    def getter(self):
        factoryFunction = self._getter_factory_functions[base_prop_name]
        hidden_prop_name = "_" + base_prop_name
        uri_prop_name = base_prop_name + "_uri"
        if not getattr(self, hidden_prop_name):
            if getattr(self, uri_prop_name):
                json_data = SHSDataAcess.getSHSData(getattr(self, uri_prop_name))
                setattr(self, hidden_prop_name, factoryFunction(json_data))
            else:
                return None
        return getattr(self, hidden_prop_name)
    return getter

class ShsData(SimpleStringifyAndEqualMethods):
    def _initialize_fields_from_json_data(self, json_type_and_schema, json_data, extraKeys=True):

        vars_to_add = voluptuous.Schema(json_type_and_schema, extra=extraKeys)(json_data)
        proper_keys = [str(x) for x in json_type_and_schema]
        for (key, value) in vars_to_add.iteritems():
            if key in proper_keys:
                setattr(self, key, value)

    def  _initialize_url_fields(self, attrNamesToFactoryFunctions, json_data):
        for (name, factoryFunction) in attrNamesToFactoryFunctions.items():
            self._getter_factory_functions[name] = factoryFunction
            uri = None
            try:
                uri = json_data[name]
            except KeyError:
                pass
            setattr(self, name + "_uri", uri)
            setattr(self, "_" + name, None)

class ShsDataWithResourceFetch(ShsData):
    @classmethod
    def get_from_resource_id(cls, resource_id):
        if cls == ShsDataWithResourceFetch.__class__:
            raise NotImplementedError("not implemented for base shs object")
#        print("resource url is:" + cls.base_resource_url + str(resource_id), file=sys.stderr)
        return cls(SHSDataAcess.getSHSData(cls.base_resource_url + str(resource_id)))


def isPartialDate(string):
    """A string representation of a date in YYYY-MM-DD, YYYY-MM, or YYYY format"""
    try:
        datetime.datetime.strptime(string, "%Y-%m-%d")
    except ValueError, _:
        try:
            datetime.datetime.strptime(string, "%Y-%m")
        except ValueError, _:
                datetime.datetime.strptime(string, "%Y")
    return string

class ShsPerformer(ShsData):
    def __init__(self, json_data):
        self.entityType = None #Always 'artist'
        self.name = None #Name of the performer
        self.artist = None #Artist of which this performer is an alias. Omitted when the performer is obvious from the context
        self._initialize_fields_from_json_data({
#                                                required("entityType"): u"artist",
                                                "entityType": u"artist", # counterexample song=1000 performer has only name
                                                "name": unicode,
                                                "artist": coerce(ShsArtist)},
                                                json_data, extraKeys=False)
        self.json_data = json_data

class ShsRelation(ShsData):
    def __init__(self, json_data):
        self.relationName = None #enumeration: has as member / is member of / family of / related
        self.comments = None #Specific details about the relationship, e.g. 'sister'
        self.artist = None #Related artist
        self._initialize_fields_from_json_data({"relationName": voluptuous.any("member",
                                                                               "is member of",
                                                                               "family of",
                                                                               "related"),
                                                "comments": voluptuous.any(unicode,
                                                                           NoneType),
                                                "artist": coerce(ShsArtist)},
                                                json_data)
        self.json_data = json_data

class ShsPicture(ShsData):
    base_resource_url = base_url + "picture/"

    def __init__(self, json_data):
        self.entityType = None #Always 'picture'
        self.title = None
        self.url = None
        self._initialize_fields_from_json_data({required("entityType"): u"picture",
                                                "name": unicode,
                                                "url": unicode},
                                                json_data)
        self.json_data = json_data




class ShsArtist(ShsDataWithResourceFetch):
    """http://www.secondhandsongs.com/wiki/API/Artist"""
    base_resource_url = base_url + "artist/"

    #URI of list of performance    Performances by the artist
    performances_data = property(_fetch_shs_data_on_first_access_getter("performances"))
    #URI of list of work    Works credited to the artist
    creditedWorks_data = property(_fetch_shs_data_on_first_access_getter("creditedWorks"))
    #URI of list of release    Releases by the artist    
    releases_data = property(_fetch_shs_data_on_first_access_getter("releases"))

    def __init__(self, json_data):
        self.entityType	 = None #string	artist / joint-artist
        self.commonName	 = None #string	The name by which the artist is mostly referred to
        self.picture	 = None #picture	(artist only) Picture of the artist
        self.birthDate	 = None #partial date	(artist only) Birth date of the artist
        self.deathDate	 = None #partial date	(artist only) Death date of the artist
        self.homeCountry = None #	string	(artist only) Country mostly associated with the artist
        self.comments	 = None #string	(artist only) Comments
        self.aliases	 = None #list of string	List of other names used by this artist
        self.relations	 = None #list of relation	(artist only) Related artists
        self.members	 = None #list of artist	(joint artist only) Artists that are part of the joint artist

        self.performances_uri = None
        self.creditedWorks_uri = None
        self.releases_uri = None

        self._getter_factory_functions = dict()

        self._initialize_fields_from_json_data({required("entityType"): voluptuous.any(u"artist"
                                                                                       , u"joint-artist"),
                                                required("uri"):basestring,
                                                "commonName": unicode,
                                               "picture": coerce(ShsPicture),
                                               "birthDate": isPartialDate,
                                               "deathDate": isPartialDate,
                                               "homeCountry": unicode,
                                               "comments": unicode,
                                               "aliases": [unicode],
                                               "relations": [coerce(ShsRelation)],
                                               "members": [coerce(ShsArtist)],
        },
                                        json_data)

        self._initialize_url_fields({"performances": lambda xs: [ShsPerformance(x) for x in xs],
                                     "creditedWorks": lambda xs: [ShsWork(x) for x in xs],
                                     "releases": lambda xs: [ShsRelease(x) for x in xs]},
                                    json_data)
        self.json_data = json_data

    def __unicode__(self):
        return unicode(self.__dict__)
    def __repr__(self):
        return repr(self.__dict__)
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                all([v == other.__dict__[k] for (k, v) in self.__dict__.items()
                     if k not in ["performances", "creditedWorks", "releases"]]))


class ShsPerformance(ShsDataWithResourceFetch):
    """http://www.secondhandsongs.com/wiki/API/Performance"""
    base_resource_url = base_url + "performance/"
    def __init__(self, json_data):
        self.entityType	 = None #string	performance / recording (in case it is recorded)
        self.title	 = None #string	title of the performance
        self.performer	 = None #performer	performer
        self.date	 = None #partial date	Performance or recording date. NOT the release date (see releases)
        self.releases	 = None #list of release	Releases on which the performance has been released
        self.works	 = None #list of work	Performed works. Usually just one work, except for medleys
        self.originals	 = None #list of work	In case of a cover: original performances per work. Each work has an additional attribute 'original' referring to the original performance and an attribute 'isRootWork' (which is true if the work is not an adaptation)
        self.covers	 = None # list of performance	In case of an original: list of covers
        self.derivedWorks = None #	list of work	In case of a cover: list of works derived from the work of the performance
        self.external_uri = None #	 	youtube videos
        self._initialize_fields_from_json_data({required("entityType"): voluptuous.any(u"performance",
                                                                                        u"recording"),
                                                required("uri"):basestring,
                                                "title": unicode,
                                               "performer": coerce(ShsPerformer),
                                               "date": isPartialDate,
                                               "releases":[coerce(ShsRelease)],
                                               "works": [coerce(ShsWork)],
                                               "originals": [coerce(ShsWork)],
                                               "covers": [coerce(ShsPerformance)],
                                               "derivedWorks": [coerce(ShsWork)],
                                               "external_uri": [unicode]},
                                        json_data)

        self.json_data = json_data

class ShsWork(ShsDataWithResourceFetch):
    """http://www.secondhandsongs.com/wiki/API/Work"""
    base_resource_url = base_url + "work/"
    def __init__(self, json_data):
        self.entityType	 = None    #string	song / poem / film / proza
        self.title	 = None    #string	title of the work
        self.language	 = None    #string	language of the work
        self.credits	 = None    #list of artist	credited artists
        self.originalCredits = None	#list of artist	artists credits for the works on which this work is based
        self.original	 = None    #performance	original performance
        self.basedOn	 = None    #list of work	works on which this work is based
        self.derivedWorks	 = None    #list of work	works derived from this work
        self.versions	 = None    #list of performance	versions of this work
        self._initialize_fields_from_json_data({required("entityType"): voluptuous.any(u"song",
                                                                                        u"poem",
                                                                                        u"film",
                                                                                        u"proza"),
                                        required("uri"):basestring,
                                        "title": unicode,
                                       "language": _voluptuous_any_or_null(unicode),
                                       "credits": [coerce(ShsArtist)],
                                       "originalCredits": [coerce(ShsArtist)],
                                       "original": coerce(ShsPerformance),
                                       "basedOn": [coerce(ShsWork)],
                                       "derivedWorks": [coerce(ShsWork)],
                                       "versions": [coerce(ShsPerformance)]},
                                json_data)
        self.json_data = json_data

class ShsRelease(ShsDataWithResourceFetch):
    """http://www.secondhandsongs.com/wiki/API/Release"""
    base_resource_url = base_url + "release/"
    def __init__(self, json_data):
        self.entityType	 = None   #string	audio album / audio single / internet / video
        self.title	 = None   #string	Title of the release
        self.type	 = None   #string	Release type. More specific than entityType
        self.date	 = None   #partial date	Release date
        self.label	 = None   #label	The label of the release
        self.catalogNr = None   	#string	Catalog number
        self.ean	 = None       #string	EAN code
        self.picture	 = None       #picture	Picture of the release art
        self.tributes	 = None   #list of artist	Tributed artists
        self.performances = None	#list of performance	Release tracks
        self.external_uri = None	#Discogs

        self._initialize_fields_from_json_data({required("entityType"): voluptuous.any(u"audio album",
                                                                                        u"audio single",
                                                                                        u"internet",
                                                                                        u"video"),
                                                required("uri"):basestring,
                                                "title": unicode,
                                               "type": unicode,
                                               "date": isPartialDate,
                                               "label": coerce(ShsLabel),
                                               "catalogNr": unicode,
                                               "ean": _voluptuous_any_or_null(unicode),
                                               "picture": coerce(ShsPicture),
                                               "tributes": [coerce(ShsArtist)],
                                               "performances": [coerce(ShsPerformance)],
                                               "external_uri": [unicode], },
                                        json_data)
        self.json_data = json_data

class ShsLabel(ShsDataWithResourceFetch):
    """http://www.secondhandsongs.com/wiki/API/Label"""
    base_resource_url = base_url + "label/"
    def __init__(self, json_data):
        self.name = None	#string	Name of the label
        self._initialize_fields_from_json_data({required("entityType"): "label",
                                                required("uri") : basestring,
                                                required("name"): unicode,
                                                "picture" : _voluptuous_any_or_null(coerce(ShsPicture))
                                                },

                                        json_data)
        self.json_data = json_data

performance, work = "performance", "work"

search_url = base_url + "/search"

def _voluptuous_any_or_null(*args):
        return voluptuous.any(*(args + tuple([None])))

def second_hand_search(title, type_=work, performer=None,
                        date=None, credits_=None, page=None, pageSize=None):

    args = {"title" : title, "type_" : type_, "performer" : performer,
                        "date" : date, "credits" : credits_, "page" : page}

    args_for_url = dict((k, v) for (k, v) in args.items() if (k not in ["type_"])
                        and v)
    result = []

    def noop(x):
        return x

    required_if_performance = voluptuous.required if type_ == performance else noop
    required_if_work = voluptuous.required if type_ == work else noop


    voluptuous.Schema({"title": basestring,
                       "type_": _voluptuous_any_or_null(performance, work),
                       "performer": _voluptuous_any_or_null(basestring) if type_ == performance else None,
                       "date": _voluptuous_any_or_null(basestring) if type_ == performance else None,
                       "credits": _voluptuous_any_or_null(basestring) if type_ == work else None,
                      "page": _voluptuous_any_or_null(int),
                      "pageSize": _voluptuous_any_or_null(int)})(args)
    if page:
        #page specific search
        url = search_url + "/" + type_ + "?" + urlencode(args_for_url)
    else:
        #fetch all pages
        url = search_url + "/" + type_ + "?" + urlencode(args_for_url)
        while True:
            try:
                json_data = SHSDataAcess.getSHSData(url)
            except SHSResourceUsedUp , e:
                print("Warning: temporarily out of resources. " + str(e.message))
                break
#                except InvalidSHSJsonData, e:
#                    print("Warning: InvalidSHSJsonData " + str(e.message))
#                    break                        
            result = result + json_data["resultPage"]
            try:
                url = json_data["next"]
            except KeyError, e:
                #
                break

        return [entityTypeToClass[x["entityType"]](x) for x in result]


entityTypeToClass = {"performance" : ShsPerformance, "recording": ShsPerformance,
                     "artist": ShsArtist, "joint-artist": ShsArtist,
                     "song": ShsWork,
                     "poem": ShsWork,
                     "film": ShsWork,
                     "proza":ShsWork,
                     "audio album": ShsRelease,
                     "audio single":ShsRelease,
                      "internet": ShsRelease,
                      "video":ShsRelease,
                      "label": ShsLabel}
