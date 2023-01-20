# Standard self contained signal encoding format for CC1101 using protobuf

I tried to reverse engineer the proto.xml from URH, probably overkill, flawed etc. Please advise

Objectives:

Create a message format for signals that is open, clear and understandable for ease of use in other languages after cross compilation.

* Must have defaults for all configurable settings for transmission using CC1101
* Must include demodulation information/rate/delays and whatever in simple format
* Must use Proto Best Practices and style standards as per ProtoV3 to make compatible with gRPC (eventually)


* Need PoC code to interact with message format and a way to generate/edit that file through URH.






