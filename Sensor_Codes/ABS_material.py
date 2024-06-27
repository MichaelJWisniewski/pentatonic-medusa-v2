import json

# Load the FTIR spectra data from JSON file
with open('C:\\Users\\ov-user\\Documents\\Neurologic\\Akash\\AK07_2.0\\Sensor_Codes\\Sensor_Codes\\Realistic_Materials_IR_Spectra.json') as f:
    ftir_data = json.load(f)

materials = ftir_data['materials']['plastics']

class MaterialObject:
    def __init__(self, name, ftir_signal):
        self.name = name
        self.ftir_signal = ftir_signal

def generate_object(material):
    # Extract FTIR signal for the material
    ftir_signal = material['peaks']
    # Create and return an object with this material
    return MaterialObject(material['name'], ftir_signal)

# Generate objects for each material
objects = [generate_object(material) for material in materials]

# Find the ABS material
abs_material = next((obj for obj in objects if obj.name == 'ABS'), None)

if abs_material:
    # Convert ABS material to a dictionary
    abs_material_dict = {
        "name": abs_material.name,
        "ftir_signal": abs_material.ftir_signal
    }
    
    # Convert to JSON
    abs_material_json = json.dumps(abs_material_dict, indent=4)
    
    print(abs_material_json)
else:
    print("ABS material not found.")
