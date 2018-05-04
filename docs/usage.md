## Usage
Currently, FlexT supports Command-Line access as well as functioning as a Python Library, while future development will add a RESTful API with a local web server. 
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

