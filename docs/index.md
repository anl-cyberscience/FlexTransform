# Flexible Transform
[![Build Status](https://travis-ci.org/anl-cyberscience/FlexTransform.svg?branch=master)](https://travis-ci.org/anl-cyberscience/FlexTransform)
[![PyPI version](https://badge.fury.io/py/FlexTransform.svg)](https://badge.fury.io/py/FlexTransform)
[![PyPI](https://img.shields.io/pypi/pyversions/FlexTransform.svg)](https://github.com/anl-cyberscience/FlexTransform)

Flexible Transform (FlexT) enables dynamic translation between Cyber Threat Intelligence reports (CTI), accomplishing this by digesting CTI data down to its semantic roots (meaning and context).

###Overview
###The Problem
Most cyber defense systems incorporate some form of cyber threat intelligence (CTI) collection and analysis. However, different
systems and CTI sharing communities have implemented a variety of representations to transmit these data (e.g., STIX, OpenIOC, custom CSV).
This diversity of formats presents a challenge when an organization using one format has the opportunity to join sharing
communities where the members share data in different formats. Similarly, merging communities with different CTI formats
can seem a nearly insurmountable challenge, and proceeds at the pace of the slowest member in each community to adopt 
a different format.

Although simple translators can be written to convert data from one format to another, challenges to this approach include the following:

An exponential increase in the effort required to support new formats.
Potential loss of meaning and context (semantics) between formats.

The obstacles posed by these challenges lead to the formation of “islands of sharing” defined not by the communities themselves 
but by the sharing formats. This pattern leaves smaller organizations, which tend to be unable to participate at all, isolated and defenseless. 



<img src="https://cfm.gss.anl.gov/wp-content/uploads/2015/07/FlexT-Diagram1.png" alt="Drawing" height="1000px;"/>



###The Solution
FlexT is a tool that enables dynamic translation between formats. FlexT accomplishes this translation by “digesting” CTI 
data down to its semantic roots (meaning and context). As Figure 1 shows, making this objective the core of the translation 
effort simplifies the process. This approach allows the use of new formats with improved scalability and ensures that the 
original meaning and context of CTI data are preserved.

A “format” in FlexT is broken down into three components:

`Syntax` – A specification of valid document characters and their composition (e.g., CSV, XML, JSON).
`Schema` – A specification of the valid terms, the data they can convey, and restrictions on their use (e.g., STIX, OpenIOC, IODEF ).
`Semantics` – A definition of the meaning of terms (e.g., SourceIPAddress is the session originating IPv4 address).

Using FlexT, organizations are empowered to participate in sharing communities using any type of CTI, in any format. When 
coupled with a toolset such as Cyber Fed Model’s (CFM’s) Last Quarter Mile Toolset (LQMToolset), participants can not only 
share and process CTI, they can take automated action based on that intelligence with an array of security endpoint devices.

###Features
|Feature | Enabling users to|
:-----: | :-------:
Multiple Interfaces | Content from cell 2
Accurate translation | Content in the second column
Easy extensibility | When supporting a new schema, simply define a mapping JSON file and immediately convert to/from any other supported format.


<img src="https://cfm.gss.anl.gov/wp-content/uploads/2015/07/FlexT-Diagram2.png" alt="Drawing" height=""/>