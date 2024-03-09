
Descritpion
    This software helps the user to create a part, 3D-printed with the Composite Fiber Co-extrusion procedure, with integrated sensors.
    Therefore it reads FEM Simulation data created by Siemens NX and recommends multiple sensor paths. The paths can be interactively changed
    or altered to the users liking. The selected sensor paths will be exported to a .dxf file and imported into NanoCAD, where the user can 
    generate the GCode necessary to produce the part on an Anisoprint 3D-Printer.

Motivation
    This project was developed as part of the windEiS cooperation project between BRIGHT Testing GmbH and the TU of Munich. 

Features
    - Reading model, compression and tensile stress data
    - Displaying the areas of the model with the highest stresses 
    - Recommendation of a sensor paths
    - Editing of the sensor paths in a paint like software
    - Adding sensor paths unrelated to compression and tensile stresses
    - Exporting model geometry and sensor paths to dxf files for GCode creation

Build Status
    No current bugs/error known.
    Open points:    
            - Automation of tension data output from Siemens NX (necessary tools are currently not supported by macros)
            - Automation of model geometry data output from Siemens NX (different geometry requires different actions to be undertaken)
            - Automation of GCode generation in NanoCAD (necessary tools are currently not supported for use in command line and different 
              geometry requires different actions to be undertaken)

Installation
    There are several Python packages used. run 'pip install -r requirements.txt' to install all.
    Siemens NX with Simcenter is required to create the necessary data: Modelcontours, Splines and stress data.
    NanoCAD is required to generate the GCode

How to use?
    Create the necessary data by simulating the part in Siemens NX using a structural and a thermal simulation. 
    The structural simulation will result in the MinPrincipal.csv file containing the compression stress per element and
    the MaxPrincipal.csv file containing the tensile stress per element as well as the coordinates of the elements. By 
    performing a thermal simulation the necessary fiber orientation for optimal force flow can be optained as a .dxf file. 
    The model contour also needs to be exported as a .dxf file. You should create have a folder containing only the following 
    four documents:
    - ...MinPrincipal.csv   (containing the compression stress per element)
    - ...MaxPrincipal.csv   (containing the tensile stress per element and the coordinates of the elements)
    - ...Contour.dxf        (containing the contour of the part)
    - ...Splines.dxf        (containing the desried fibers as splines)

    Run the main.py file. Everything else will be described in the software. 
    For further information see ./docs/directions or the corresponding Master Thesis.
    For a example run the main.py file and select the ./sample ordner as path and put in 150 as length, 20 as height and width

License

    Free, see License.