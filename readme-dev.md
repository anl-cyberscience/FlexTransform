# Developer Documentation

## Introduction  
Flexible Transform, or *FlexT*, is a tool that enables dynamic translation between formats. Here is an outline of the process logic. The user provides the source file in a specified format, as well as configuration files that have information about the syntax and semantics of the source format and destination format. *FlexT*, then uses ontology logic to map the information contained within the source file source file to the destination format.

Though most of the underlying logic is generic, there are some components of the *FlexT* engine that need to be written separately for each format, which is where the developers come in.  This document is intended to help such developers understand what is required to successfully translate one format into another.  

<figure>
<a href="FlexTransform/resources/images/dev-figure1.png">
<img src = "FlexTransform/resources/images/dev-figure1.png" />
</a>
<figcaption>
Figure 1 - Architecture of FlexTransform.
</figcaption>
</figure>

## Required Inputs  
- Source File
- Source Format Configuration
- Destination Format Configuration
- Destination File Name & Path

## Configuration File
The configuration files has several sections inside it, which are briefly listed in the list below, with further information provided in the following sections.  Out of these, the SYNTAX and SCHEMA sections are mandatory without which the command will fail. Rest of the sections is optional.  The information inside each section would be in the format of `Attribute = value`. 

    - Syntax
    - Schema
- At least one of the below sections is required:
    - CSV

[Example Configuration File](FlexTransform/resources/sampleConfigurations/cfm13.cfg)
### Syntax 




“FieldName” : {
    “attribute2” : “value2”,  
    “attribute3” : “value3”,
    ...
}
```



[Example XML Parser](FlexTransform/SyntaxParser/XMLParsers/CFM13.py)