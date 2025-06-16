import xml.etree.ElementTree as ET
class SMSLoader:
    def __init__(self, sms_xml_file):
        self.sms_xml_file = sms_xml_file
        
    def load_sms(self):
        '''
        Load the XML file and extract the SMS messages
        '''
        try:
            tree = ET.parse(self.sms_xml_file)
            root = tree.getroot()
            return root.findall("sms")
        except Exception as e:
            print(f"Error loading SMS XML file: {e}")
            return []