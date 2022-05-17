import json
import os
import meshio
import numpy as np
from pathlib import Path
import meshplot as mp
import igl
import matplotlib.pyplot as plt

import xml.etree.ElementTree as ET
import xml.dom.minidom

def read_volume_mesh(path, input_dimension, output_dimension):
    """

    :param path:
    :return:
    """

    mesh = meshio.read(path, file_format="gmsh")
    vertices = mesh.points
    elements = mesh.get_cells_type("tetra")

    if output_dimension == "m":
        vertices = vertices / 1000

    # print("number of elements:", len(elements))

    # tet_physical = mesh.cell_data["gmsh:physical"]
    # domains = np.unique(tet_physical[0])

    # print("the model has this many parts:", domains)

    return vertices, elements

def xmlElementWriter(xmlElement, fileName):
    """
    Write the given XML-element to a file that has the given fileName

    :param xmlElement: xml.etree.ElementTree.Element instance, The XML-element that contains all of the data that is being written, including desired child XML-elements.
    :param fileName: string, The name of the file that is being generated. Note that if this fileName already exists, then that file will be overwritten without warning.
    :return:
    """
    xmlElementText = ET.tostring(xmlElement)  # Convert the XML-element 'xmlElement' to a string variable
    xmlText = xml.dom.minidom.parseString(xmlElementText)  # Get the text that composes the xml-element.
    xmlString = xmlText.toprettyxml(
        encoding='ISO-8859-1')  # Make the text pretty by adding line breaks and indentations

    # Write the xml file.
    with open(fileName,
              mode='wb') as fl:  # Open/create a new file that uses the 'fileName' variable to define the file's name.
        fl.write(xmlString)  # Write 'xmlString' to the file

    return


def getNodeXmlElement(nodeId, nodeCoordinates):
    """
    Create a 'node' xml-element that is populated with the given data.

    The xml-element that is returned is something similar to this:
        <node id="1">0., 0., 0.</node>

    :param nodeId: int, The integer that is used to identify the node in the finite element mesh.
    :param nodeCoordinates: array 1x3, The coordinates of the node in the finite element mesh.
    :return:
    """
    # Convert 'nodeId' to a string value.
    # Notice how overwriting the original value in 'nodeId' with a string value.
    nodeId = str(nodeId)
    # Define a dictionary with a key called 'id'.
    attributeData = {'id': nodeId}
    element = ET.Element('node',
                         attributeData)  # Create an xml-element with a tag of 'node' and attributes defines with the 'attributeData' dictionary.
    # Notice here how the values in braces {} are converted into strings automatically.
    # The values outside the braces remain part of the string.
    element.text = f'{nodeCoordinates[0]}, {nodeCoordinates[1]}, {nodeCoordinates[2]}'  # Define the text value for the 'barNodesChild' xml-element.

    return element

def getSurfaceXmlElement(nodeId, surfaceDefinition):
    # """
    # Create a 'node' xml-element that is populated with the given data.
    #
    # The xml-element that is returned is something similar to this:
    #     <node id="1">0., 0., 0.</node>
    #
    # :param nodeId: int, The integer that is used to identify the node in the finite element mesh.
    # :param nodeCoordinates: array 1x3, The coordinates of the node in the finite element mesh.
    # :return:
    # """
    # Convert 'nodeId' to a string value.
    # Notice how overwriting the original value in 'nodeId' with a string value.
    nodeId = str(nodeId)
    # Define a dictionary with a key called 'id'.
    attributeData = {'id': nodeId}
    element = ET.Element('tri3',
                         attributeData)  # Create an xml-element with a tag of 'node' and attributes defines with the 'attributeData' dictionary.
    # Notice here how the values in braces {} are converted into strings automatically.
    # The values outside the braces remain part of the string.
    element.text = f'{ surfaceDefinition[0]}, {surfaceDefinition[1]}, {surfaceDefinition[2]}'  # Define the text value for the 'barNodesChild' xml-element.

    return element


def getElemXmlElement(elementId, elementDefinition):
    """
    Create a 'elem' xml-element that is populated with the given data.

    The xml-element that is returned is something similar to this:
        <elem id="1">4, 3, 10, 9, 8, 7, 11, 12</elem>

    :param elementId: int, The integer that is assigned to the xml-attribute "id=elementId"
    :param elementDefinition: array 1xn, An array of 'n' integers. These integers are used as the 'elem' xml-element's text, which is a comma separated list.
    :return: xml.etree.ElementTree.Element instance, An xml-element that is populated with the given data.
    """
    # Two operations are happening in this line in the following order:
    #   1) str(elementId)   elementId is converted to a string.
    #       Notice how the results of this operation are not used to define a variable, rather they are used as the input for the next operation.
    #   2) {'id':str(elementId)}    A dictionary with one entry is generated. We are giving that entry a key of 'id'.
    #       Notice how the results of the previous operation are supplying the value for the entry.
    elementData = {'id':str(elementId)}
    xmlElement = ET.Element('elem', elementData) # Define the xml-element.

    # Specify the text for 'xmlElement'
    txt = '' # Initialize an empty string
    for i in range(len(elementDefinition)):
        txt = txt + f'{elementDefinition[i]}, '
    txt = txt.rstrip(', ')
    xmlElement.text = txt
    return xmlElement
