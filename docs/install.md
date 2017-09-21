# Dependencies
## Install
FlexTransform (FlexT) is run using Python3. This means that **Python3** is required to be installed to properly run FlexT.
Once Python3 is installed FlexT can be installed via *pip3*, but it requires the python package *lxml* which itself has 
UNIX dependencies. The required dependencies for *lxml* are **libxml** and **libxslt** as well as their associated 
development packages. For Debian based systems the following command can be used

```bash
$ sudo apt-get install libxml2-dev libxslt-dev python-dev
```
*pip* command:
```shell
$ pip install FlexTransform
```

## Getting Started
When using FlexT from the command lines there are certian arguments that are required to be passed in to perform the 
conversiion.
```bash
--src-config CONFIG
```  
This argument is used to pass in the file that contains the parser configuration file for the source file.
```bash
--src SRC
```  
This argument is the source file that will be transformed.
```bash
--dst-config CONFIG
```
This argument is used to pass in the file that contains the parser configuration file for the destination file.
```bash
--dst DST
```
This argument is used to pass in the path to where the file will be stored.

These arguments will be all you need to get started with FlexT when using one of the supported schemas. If an unsupported 
schema is going to be used, users can pass in arguments for either the source schema, destination schema, or both.

```bash
--source-schema-IRI
```
Used to pass in the ontology IRI file for the source file.

```bash
--destination-schema-IRI
```
Used to pass in the ontology IRI file for the destination file.

```bash
flext --src /Path/to/file --src-config /Path/to/file --dst /Path/to/file --dst-config /Path/to/file
```
This is the most basic format for transforming a file that is currently supported. 