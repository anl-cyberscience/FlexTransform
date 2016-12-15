import os
from FlexTransform import FlexTransform

if __name__ == '__main__':

    # THESE LOCATIONS MATTER!!
    dir_location = "/Users/mhend/Downloads/test/"
    src_config_location = "/Users/mhend/git/FlexTransform/FlexTransform/resources/sampleConfigurations/cfm13.cfg"
    dst_config_location = "/Users/mhend/git/FlexTransform/FlexTransform/resources/sampleConfigurations/stix_tlp.cfg"
    # if output path is absolute, follows that path and creates if necessary.
    # If it's relative, then uses the dir containing files as root, creates if necessary
    output_folder_path = "FlexT output"

    if not os.path.isdir(dir_location):
        print("File path either doesn't exist or isn't a location, exiting")
        exit(1)

    for root, dirs, files in os.walk(dir_location):
        # Are there files in directory?
        if not files:
            print("Directory is empty, exiting")
            exit(1)
        # Is output path abs or relative?
        if not os.path.isabs(output_folder_path):
            output_folder_path = os.path.join(root, output_folder_path)
        if not os.path.isdir(output_folder_path):
            os.makedirs(output_folder_path)

        flexT = FlexTransform.FlexTransform()
        with open(src_config_location, 'r') as input_file:
            flexT.AddParser("src", input_file)
        with open(dst_config_location, 'r') as input_file:
            flexT.AddParser("dst", input_file)

        for name in files:
            if name.startswith("."):
                continue
            iname = os.path.join(root, name)
            oname = os.path.join(output_folder_path, name)
            print(iname, oname)
            with open(iname, "r") as input_file:
                with open(oname, "w") as output_file:
                    try:
                        print("Starting processing file: {}".format(iname))
                        flexT.TransformFile(input_file, "src", "dst", targetFileName=output_file)
                    except Exception as e:
                        print(e)
                        print("Exception in found in file, skipping it: {}".format(iname))
        break
