# Flexible Transform
[![PyPI version](https://badge.fury.io/py/flextransform.svg)](https://badge.fury.io/py/flextransform) [![Build Status](https://travis-ci.org/anl-cyberscience/FlexTransform.svg?branch=master)](https://travis-ci.org/anl-cyberscience/FlexTransform)

Flexible Transform (FlexT) enables dynamic translation between formats, accomplishing this by digesting CTI data down to its semantic roots (meaning and context).  
## Install
FlexT requires **Python3** & is available via *pip*, but it requires the python package [*lxml*](http://lxml.de/) which has unix dependencies such as *libxml2* and *libxslt* (as well as associated development packages).  For systems that employ ```apt-get``` such as Debian & Ubuntu, the following command can be used.
```bash
sudo apt-get install libxml2-dev libxslt-dev python-dev
```
*pip* command:
```shell
$ pip install FlexTransform
```
## Usage
Currently, FlexT supports Command-Line access as well as functioning as a Python Library, while future development will add a RESTful API with a local web server.   
### Command Line
```shell
$ flext --src inputFile.txt --src-config srcConfig.cfg --dst outputFile.xml --dst-config dstConfig.cfg
```
+ Required arguments 
    + `src` - Source file
    + `src-config` - Source file parser configuration
    + `dst` - Destination file
    + `dst-config` - Destination file parser configuration
+ Optional arguments
    + `src-metadata` - Source metadata file
    + `tbox-uri` - The rui location of the tbox file
    + `source-schema-IRI` - Ontological IRI for the source
    + `destination-schema-IRI` - Ontological IRI for the destination
    
### Python Library
FlexT accepts File-like objects, so in addition to allowing for the ```open``` command, you can also use python objects like ```StringIO```.
```python
from FlexTransform import FlexTransform
flexT = FlexTransform.FlexTransform()

with open("/Users/cfm/FlexT/FlexTransform/resources/sampleConfigurations/cfm13.cfg", "r") as input_cfg:
        flexT.AddParser("cfm13", input_cfg)
with open("/Users/cfm/FlexT/FlexTransform/resources/sampleConfigurations/stix_tlp.cfg", "r") as output_cfg:
        flexT.AddParser("stix", output_cfg)

with open("/Users/cfm/input.xml", "r") as input_file:
        with open("/Users/cfm/output.xml", "w") as output_file:
                flexT.TransformFile(input_file, "cfm13", "stix", targetFileName=output_file)
```
## Contributing
### Bug Reports & Feature Requests
Please use the issue tracker to report any bugs or file feature requests.
### Developing
Additional functionality is always being added, but we welcome any PRs to improve the project.
