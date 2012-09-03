#!/usr/bin/env python
import second_hand_songs_wrapper as s
from __future__ import print_function
from docopt import docopt
import voluptuous
import sys

def main(args=sys.argv[1:]):
    usage_string =  """
    Usage:
    second_hand_songs_api_cmdline.py --getShsArtistById <id>
    second_hand_songs_api_cmdline.py --getShsPerformanceById <id>
    second_hand_songs_api_cmdline.py --getShsWorkById <id>
    second_hand_songs_api_cmdline.py --getShsReleaseById <id>
    second_hand_songs_api_cmdline.py --getShsLabelById <id>
    second_hand_songs_api_cmdline.py --searchWork <title> [ --credits <credits_> ] [ --page <page> ] [ --pageSize <pageSize>]
    second_hand_songs_api_cmdline.py --searchPerformance <title> [ --performer <performer> ] [ --date <date> ]
    second_hand_songs_api_cmdline.py -a | --allFields
    second_hand_songs_api_cmdline.py -d | --dereference Access a field/key, works across multiple fields
    second_hand_songs_api_cmdline.py -h | --help
    second_hand_songs_api_cmdline.py --version
    """
    d_args_dict = docopt(usage_string, argv=args, version="0.1")

    schema = voluptuous.Schema({},extra=True)
    try:
        d_args_dict = schema(d_args_dict)
    except voluptuous.SchemaError as e:
        exit(e)
    
    performer = d_args_dict["--performer"]
    date = d_args_dict["--date"]
    page = d_args_dict["--page"]
    pageSize = d_args_dict["--pageSize"]    
    if d_args_dict["--getShsArtistById"]:
        o = s.ShsArtist.get_from_resource_id(d_args_dict["id"])
        if(d_args_dict["-a"] or d_args_dict["--allFields"]):
            o.performances_data
            o.creditedWorks_data
            o.releases_data
    elif d_args_dict["--getShsPerformanceById"]:
        o = s.ShsPerformance.get_from_resource_id(d_args_dict["id"])
    elif d_args_dict["--getShsWorkById"]:
        o = s.ShsWork.get_from_resource_id(d_args_dict["id"])
    elif d_args_dict["--getShsReleaseById"]:
        o = s.ShsRelease.get_from_resource_id(d_args_dict["id"])
    elif d_args_dict["--getShsLabelById"]:
        o = s.ShsLabel.get_from_resource_id(d_args_dict["id"])
    elif d_args_dict["--searchWork"]:
        credits_ = d_args_dict["--credits_"]
        o = s.second_hand_search(d_args_dict["title"], type_=s.work, credits_, page, pageSize)
    elif d_args_dict["--searchPerformance"]:
        o = s.second_hand_search(d_args_dict["title"], type_=s.performance, performer=performer,
                                date=date, page=page, pageSize=pageSize)
    else:
        raise Exception("Need to pick a way to search for data.")
    if d:
        new_object = o
        for attr_deref in d:
            new_object = getattr(new_object, attr_deref)
        print(attr_deref)
    else:
        print(o)
        
    
if __name__ == "__main__":
    main()