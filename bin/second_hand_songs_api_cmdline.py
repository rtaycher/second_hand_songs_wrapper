#!/usr/bin/env python
#

from __future__ import print_function
import sys
import voluptuous
from docopt import docopt
import second_hand_songs_wrapper as s

# [ -d <d>... | --dereference <d>... ]
def main(args=sys.argv[1:]):
    usage_string = """
    Usage:
        second_hand_songs_api_cmdline.py --getShsArtistById <id> [-a|--allFields] [<dereferece_attr>...] 
        second_hand_songs_api_cmdline.py --getShsPerformanceById <id> [<dereferece_attr>...] 
        second_hand_songs_api_cmdline.py --getShsWorkById <id> [<dereferece_attr>...] 
        second_hand_songs_api_cmdline.py --getShsReleaseById <id> [<dereferece_attr>...] 
        second_hand_songs_api_cmdline.py --getShsLabelById <id> [<dereferece_attr>...] 
        second_hand_songs_api_cmdline.py --searchWork <title> [ --credits <credits_> ] [ --page <page> ] [ --pageSize <pageSize>] [<dereferece_attr>...] 
        second_hand_songs_api_cmdline.py --searchPerformance <title> [ --performer <performer> ] [ --date <date> ] [<dereferece_attr>...] 
        second_hand_songs_api_cmdline.py -h | --help
        second_hand_songs_api_cmdline.py --version
    
    Options:
        -a, --allFields            Fetch extra data for uri fields, currently applies only to getShsArtistById
        <dereferece_attr>...       Access a field/key, works across multiple fields
    """
    d_args_dict = docopt(usage_string, argv=args, version=s.__version__)
    schema = voluptuous.Schema({}, extra=True)
    try:
        d_args_dict = schema(d_args_dict)
    except voluptuous.SchemaError as e:
        exit(e)

    performer = d_args_dict["--performer"]
    date = d_args_dict["--date"]
    page = d_args_dict["--page"]
    pageSize = d_args_dict["--pageSize"]
    if d_args_dict["--getShsArtistById"]:
        o = s.ShsArtist.get_from_resource_id(d_args_dict["<id>"])
        if(d_args_dict["--allFields"]):
            o.performances_data
            o.creditedWorks_data
            o.releases_data
    elif d_args_dict["--getShsPerformanceById"]:
        o = s.ShsPerformance.get_from_resource_id(d_args_dict["<id>"])
    elif d_args_dict["--getShsWorkById"]:
        o = s.ShsWork.get_from_resource_id(d_args_dict["<id>"])
    elif d_args_dict["--getShsReleaseById"]:
        o = s.ShsRelease.get_from_resource_id(d_args_dict["<id>"])
    elif d_args_dict["--getShsLabelById"]:
        o = s.ShsLabel.get_from_resource_id(d_args_dict["<id>"])
    elif d_args_dict["--searchWork"]:
        credits_ = d_args_dict["--credits_"]
        o = s.second_hand_search(d_args_dict["title"], type_=s.work,
                                 credits_=credits_, page=page, pageSize=pageSize)
    elif d_args_dict["--searchPerformance"]:
        o = s.second_hand_search(d_args_dict["title"], type_=s.performance,
                                 performer=performer, date=date, page=page,
                                  pageSize=pageSize)
    else:
        raise Exception("Need to pick a way to search for data.")


    if d_args_dict["<dereferece_attr>"]:
        new_object = o
        for attr_deref in d_args_dict["<dereferece_attr>"]:
            new_object = getattr(new_object, attr_deref)
        print(new_object)
    else:
        print(o)


if __name__ == "__main__":
    main()
