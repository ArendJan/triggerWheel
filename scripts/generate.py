#!/usr/local/bin/python3

rel_freecad_directory = "../"

import sys

sys.path.append("/usr/lib/freecad-python3/lib/")
sys.path.append("/")
try:
    import FreeCAD
    import importDXF
    import Draft
    import Part
    import Mesh
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
    sv0 = Draft.make_shape2dview(body, FreeCAD.Vector(0, -1, 0))
    FreeCAD.getDocument(name).recompute()    
    pathOut = getFilePath(body, name, build_path, "dxf")
    
    # Code as shown in FreeCAD console when generating dxf file:
    __objs__ = []
    __objs__.append(FreeCAD.getDocument(name).getObject(sv0.Name))

    if hasattr(importDXF, "exportOptions"):
        options = importDXF.exportOptions(pathOut)
        importDXF.export(__objs__, pathOut, options)
    else:
        d = importDXF.export(__objs__, pathOut)

    del __objs__
    
    
def renderFile(freecadFile):
    doc = FreeCAD.open(str(freecadFile))
    bodies = list()
    for obj in doc.Objects:
        # Fix for motor clamp lock, the chamfer one is the final one
        if obj.isDerivedFrom("PartDesign::Body") or obj.isDerivedFrom("Part::Chamfer"):
            bodies.append(obj)
    for body in bodies:
        build_dir = (freecadFile.parent / "../build").resolve()
        if not build_dir.exists():
           os.mkdir(build_dir)
        exportDXF(body, freecadFile.stem, build_dir)
        exportSTL(body, freecadFile.stem, build_dir)
        exportSTEP(body, freecadFile.stem, build_dir)
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