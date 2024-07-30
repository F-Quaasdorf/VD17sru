import requests
import unicodedata
from lxml import etree
import pandas as pd

def vd17_sru(query):    
    base_url = "http://sru.k10plus.de/vd17" #Auch für VD18 nutzbar: http://sru.k10plus.de/vd18
    parameters = {
        "recordSchema": "marcxml",
        "operation": "searchRetrieve",
        "version": "2.0",
        "maximumRecords": "100",
        "query": query
    }
    
    session = requests.Session()
    records = []
    start_record = 1
    first_request = True
    
    while True:
        parameters["startRecord"] = start_record
        response = session.get(base_url, params=parameters)
        if first_request:
            print(response.url)
            first_request = False
            
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break
        
        xml_root = etree.fromstring(response.content)
        
        new_records = xml_root.findall('.//zs:record', namespaces={"zs": "http://docs.oasis-open.org/ns/search-ws/sruResponse"})
        
        for record in new_records:
            record_data = record.find('zs:recordData', namespaces={"zs": "http://docs.oasis-open.org/ns/search-ws/sruResponse"})
            if record_data is not None:
                marc_record = record_data.find('record', namespaces={"": "http://www.loc.gov/MARC21/slim"})
                if marc_record is not None:
                    records.append(etree.tostring(marc_record, encoding='unicode'))
        
        if len(new_records) < 100:
            break
        
        start_record += 100
    
    return records

def parse_record(record):    
    namespaces = {
        "marc": "http://www.loc.gov/MARC21/slim"
    }
    xml = etree.fromstring(unicodedata.normalize("NFC", record))
    
    def get_single_text(xpath_expr):
        try:
            return xml.xpath(xpath_expr, namespaces=namespaces)[0].text
        except IndexError:
            return "N.N."
    
    def get_multiple_texts(xpath_expr):
        return [elem.text for elem in xml.xpath(xpath_expr, namespaces=namespaces)] or ["N.N."]
    
    meta_dict = {
        "IDN": get_single_text("//marc:controlfield[@tag='001']"),
        "VD-Nummer": get_single_text("//marc:datafield[@tag='024']/marc:subfield[@code='a']"),
        "Verfasser": get_single_text("//marc:datafield[@tag='100']/marc:subfield[@code='a']"),
        "Titel": get_single_text("//marc:datafield[@tag='245']/marc:subfield[@code='a']"),
        "Erscheinungsort": get_multiple_texts("//marc:datafield[@tag='264']/marc:subfield[@code='a']"),
        "Erscheinungsjahr": get_single_text("//marc:datafield[@tag='264']/marc:subfield[@code='c']"),
        "Sprache": get_multiple_texts("//marc:datafield[@tag='041']/marc:subfield[@code='a']"),
        "Einrichtung": get_multiple_texts("//marc:datafield[@tag='924']/marc:subfield[@code='b']")
    }
    
    return meta_dict

def to_df(records):    
    return pd.DataFrame(records)

# Fetch records
records = vd17_sru("pica.tit=de statu imperii") # Query via PICA

# Parse records
parsed_records = [parse_record(record) for record in records]

# Convert to DataFrame
df = to_df(parsed_records)

# Print DataFrame
pd.set_option('display.max_columns', None)
print(df)

# Save to CSV
df.to_csv("DataFrame.csv", encoding="utf-8")
