import second_hand_songs_wrapper as s
from nose.tools import assert_equal, assert_raises#@UnresolvedImport

from voluptuous import InvalidList

def testShsArtist():
    assert_equal(s.ShsArtist.get_from_resource_id(1000).commonName, u"Little Richard")

def testShsLabel():
    with assert_raises(InvalidList):
        s.ShsLabel.get_from_resource_id(123)
    assert_equal(s.ShsLabel.get_from_resource_id(125).name, u"Globe")

def testShsPerformance():
    assert_equal(s.ShsPerformance.get_from_resource_id(123).title, u"I'm Waiting for the Man")

def testShsRelease():
    assert_equal(s.ShsRelease.get_from_resource_id(123).title, u"Fifth Dimension")

def testShsWork():
    assert_equal(s.ShsWork.get_from_resource_id(1000).title, u"Oh, me")
