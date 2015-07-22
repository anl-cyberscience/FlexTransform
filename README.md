Flexible Transform
=====

The problem
-----
Most cyber defense systems incorporate some form of cyber threat intelligence (CTI) collection and analysis.  However, different systems and CTI sharing communities have implemented a variety of representations to transmit this data (e.g. STIX, OpenIOC, custom CSV). This presents a challenge when an organization using one format has the opportunity to join sharing communities where the members share data in different formats.  Similarly, merging communities with different CTI formats can seem nearly insurmountable, and proceeds at the pace of the slowest member in each community to adopt a different format.  

While simple translators can be written to convert data from one format to another, challenges to this approach include:

- An exponential increase in the effort required to support new formats
- Potential loss of meaning and context (semantics) between formats.

These challenges lead to islands of sharing defined not by communities, but by sharing formats, leaving smaller organizations unable to participate at all, isolated and defenseless.


The solution
-----
Flexible Transform (FlexT) is a tool that enables dynamic translation between formats. FlexT accomplishes this by digesting CTI data down to its semantic roots (meaning and context). As seen in Figure 1, making this the core of the translation simplifies the process. This allows the use of new formats with improved scalability and ensures that the original meaning and context of CTI data is preserved.

<figure>
<a href="FlexTransform/resources/images/figure1a.png">
<img src = "FlexTransform/resources/images/figure1a.png" />
</a>
<a href="FlexTransform/resources/images/figure1b.png">
<img src = "FlexTransform/resources/images/figure1b.png" />
</a>
<figcaption>
Figure 1 - On the left, the scaling problem with developing pairwise translators for all supported formats.  On the right, the advantage of using an intermediate semantic representation.
</figcaption>
</figure>

A "format" in FlexT is broken down into three components:

- **Syntax** - A specification of valid document characters and their composition, e.g. CSV, XML, JSON.
- **Schema** - A specification of the valid terms, the data they can convey, and restrictions on their use, e.g. STIX, OpenIOC, IODEF.
- **Semantics** - A definition of the meaning of terms, e.g. SourceIPAddress is the session originating IPv4 address.

Using FlexT, organizations are empowered to participate in sharing communities using any type of CTI, in any format.  When coupled with a toolset such as CFM's Last Quarter Mile Toolset (LQMToolset), participants can not only share and ingest, they can take automated action based on that intelligence with an array of security endpoint devices. 


Features
-----
- **Multiple interfaces**: Use FlexT as a library or from the command-line tool
- **Accurate translation**: Convert the format without losing context or meaning
- **Easy extensibility**: To support a new schema, simply define a mapping JSON file and immediately convert to/from any other supported format


Currently Supports
-----
- Structured Threat Information eXpression (STIX)  with multiple profiles 
- All CFM XML schemas 
  - CFM 1.3 Legacy Format
  - CFM 2.0 Format
- Key/Value indicator schema


Coming Soon
-----
- Additional Data Formats
  - OpenIOC
  - FlexText 
- REST Web-based interface

Get Involved!
-----
There are many threat indicator formats to use, and many organizations have "grown their own".  Feel free to test out FlexT and provide feedback, submit code, or develop and share JSON configuration files.

Get involved and help turn CTI into actionable defense! Contact us via <a href="mailto:CFMteam@anl.gov">CFMteam@anl.gov</a>
