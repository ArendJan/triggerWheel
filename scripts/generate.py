#!/usr/local/bin/python3

rel_freecad_directory = "../"
document_name = "triggerwheel"
import sys
import yaml
sys.path.append("/usr/lib/freecad-python3/lib/")
sys.path.append("/")
try:
    import FreeCAD
    import importDXF
    import Draft
    import Part
    import Mesh
    # import importSVG

except ValueError:
    print("FreeCAD library not found.")
    exit()

def getFilePath(body, name, build_path, type):
    type_path = (build_path / type)
    if not type_path.exists():
       os.mkdir(type_path)
       
    attachment_path = "" 
    if name == "attachments":
        if not (type_path / "attachments").exists():
            os.mkdir((type_path / "attachments"))
        attachment_path = "attachments"

    label_postfix = ""
    if (body.Label != "Body"):
        label_postfix = "_" + body.Label
        label_postfix = label_postfix.replace("_body", "") # fix for layer bodies
    
    return str((type_path / attachment_path / (str(name) + label_postfix + "." + type)).resolve())
    
    
def exportSTL(body, name, build_path):
    pathOut = getFilePath(body, name, build_path, "stl")

    # Code as shown in FreeCAD console when generating stl file:
    __objs__ = []
    __objs__.append(body)

    if hasattr(Mesh, "exportOptions"):
        options = Mesh.exportOptions(pathOut)
        Mesh.export(__objs__, pathOut, options)
    else:
        Mesh.export(__objs__, pathOut)

    del __objs__
    
def exportSTEP(body, name, build_path):
    pathOut = getFilePath(body, name, build_path, "step")

    __objs__ = []
    __objs__.append(body)
    
    if hasattr(Part, "exportOptions"):
        options = Part.exportOptions(pathOut)
        Part.export(__objs__, pathOut, options)
    else:
        Part.export(__objs__, pathOut)

    del __objs__
    
    
def exportDXF(body, name, build_path):   
    FreeCAD.getDocument(name).recompute()    

    __objs__ = []
    pathOut = getFilePath(body, name, build_path, "dxf")

    __objs__.append(FreeCAD.getDocument(document_name).getObject(body.Name))
    import importDXF
    if hasattr(importDXF, "exportOptions"):
        options = importDXF.exportOptions(pathOut)
        importDXF.export(__objs__, pathOut, options)
    else:
        importDXF.export(__objs__, pathOut)
    
    del __objs__
    # sv0 = Draft.make_shape2dview(body, FreeCAD.Vector(0, 0, 1))
    
    # # Code as shown in FreeCAD console when generating dxf file:
    # __objs__ = []
    # __objs__.append(FreeCAD.getDocument(name).getObject(sv0.Name))

    # if hasattr(importDXF, "exportOptions"):
    #     options = importDXF.exportOptions(pathOut)
    #     importDXF.export(__objs__, pathOut, options)
    # else:
    #     d = importDXF.export(__objs__, pathOut)

    # del __objs__
    
tooth_count_spreadsheet_cell = "E2"
missing_count_spreadsheet_cell = "F2"

# tooth_count: ${{ matrix.tooth }}
# missing_count: ${{ matrix.missing }}
# tooth_length: ${{ matrix.tooth_length || 5 }}
# tooth_duty_cycle: ${{ matrix.tooth_duty_cycle || 50 }}
# tooth_radius: ${{ matrix.tooth_radius || 0 }}
# diameter: ${{ matrix.diameter || 200 }}
# thickness: ${{ matrix.thickness || 10 }}
# hole_diameter: ${{ matrix.hole_diameter || 5 }}
# slit_width: ${{ matrix.slit_width || 1 }}
# slit_depth: ${{ matrix.slit_depth || 2 }}
# slit_count: ${{ matrix.slit_count || 36 }}
# slit_offset: ${{ matrix.slit_offset || 0 }}


settings_map = {
    "tooth_count": "E2",
    "missing_count": "F2",
    "tooth_length": "D2",
    "tooth_duty_cycle": "I2",
    "tooth_radius": "G2",
    "thickness": "H2",
    "diameter": "B2",
    "hole_diameter": "C2",
    "slit_width": "C14",
    "slit_depth": "B14",
    "slit_count": "D14",
    "slit_offset": "E14",
}

def set_settings(doc, freecadFile):
    SPREADSHEET_NAME = "Spreadsheet"
    try:
        sheet = doc.getObject(SPREADSHEET_NAME)
        if not sheet or sheet.TypeId != 'Spreadsheet::Sheet':
            raise AttributeError
    except AttributeError:
        print(f"Spreadsheet {SPREADSHEET_NAME} not found in {freecadFile.stem}")
        pass
    try:
        # tooth_count_file = freecadFile.parent / "TOOTH_COUNT.txt"
        # if tooth_count_file.exists():
        #     with open(tooth_count_file, 'r') as f:
        #         tooth_count = f.read().strip()
        #         sheet.set(tooth_count_spreadsheet_cell, tooth_count)
        
        # missing_count_file = freecadFile.parent / "MISSING_COUNT.txt"
        # if missing_count_file.exists():
        #     with open(missing_count_file, 'r') as f:
        #         missing_count = f.read().strip()
        #         sheet.set(missing_count_spreadsheet_cell, missing_count)
        config_file = "/tmp/settings.yaml"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                for key, value in config.items():
                    if key in settings_map:
                        sheet.set(settings_map[key], str(value))
    except Exception as e:
        print(f"Error setting spreadsheet value: {e}")
    doc.recompute()



def renderFile(freecadFile):
    doc = FreeCAD.open(str(freecadFile))
    set_settings(doc, freecadFile)
    bodies = list()
    for obj in doc.Objects:
        # if obj.isDerivedFrom("PartDesign::Body"):
        if obj.Name.startswith("PolarPatte"):
            bodies.append(obj)
    # bodies.append()
    # for obj in doc.Objects:
    #     print(f"Found object: {obj.Name} of type {obj.TypeId}")
    #     # Fix for motor clamp lock, the chamfer one is the final one
    #     # if obj.isDerivedFrom("PartDesign::Body") or obj.isDerivedFrom("Part::Chamfer") or obj.isDerivedFrom("Part::Fillet") or obj.Name.startswith("Array") :
    #     bodies.append(obj)
    for body in bodies:
        try:
            print(f"Processing body: {body.Name} of type {body.TypeId}")
            build_dir = (freecadFile.parent / "../build").resolve()
            if not build_dir.exists():
                os.mkdir(build_dir)
            exportDXF(body, freecadFile.stem, build_dir)
            exportSTL(body, freecadFile.stem, build_dir)
            exportSTEP(body, freecadFile.stem, build_dir)
        except Exception as e:
            print(f"Error processing body {body.Name}: {e}")
    FreeCAD.closeDocument(freecadFile.stem)


import os
import shutil
from pathlib import Path

dir_path = Path(os.getcwd())
print(dir_path)
print(os.listdir(dir_path))
freecad_directory = (dir_path / rel_freecad_directory).resolve()
print(freecad_directory)
print(os.listdir(freecad_directory))

# clean build directory
if (freecad_directory.parent / "build").exists():
    shutil.rmtree(freecad_directory.parent / "build")

print(os.listdir(freecad_directory))
# render all freecad files
for filename in os.listdir(freecad_directory):
    f = freecad_directory / filename
    if f.suffix == ".FCStd":
        print(f.stem)

        renderFile(f)