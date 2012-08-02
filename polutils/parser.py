import re
from os.path import basename
from lxml import etree
from StringIO import StringIO

class ItemParser(object):
    
    # Parsed items
    items = {}
    
    def __init__(self, files=None, fields=None, convert_hex=False, 
                 rename_fields=None, detect_lang=False, lang_sep="_"):
        # Desired fields
        self.fields = fields
        
        # XML files to be parsed
        self.files = files
        self.convert_hex = convert_hex
        self.hex_fields = ['type', 'resource-id', 'valid-targets', 'slots', 
                           'races', 'jobs', 'element', 'flags', 'skill']
    
        self.lang_fields = ['name', 'description', 'log-name-singular', 'log-name-plural']
        self.rename_fields = rename_fields
        self.detect_lang = detect_lang
        self.lang_sep = "-"
        
    def parse(self, lang=None):
        for file in self.files:
            self.parse_file(file, lang=lang)
        return self.items
    
    def parse_file(self, file, lang=None):
        if lang is None and self.detect_lang:
             # Determine lang by prefix of file
            m = re.match(r"^([a-z]+)[\-_\s\.].*", basename(file), re.IGNORECASE)
            if m:
                lang = m.group(1)
                if lang not in ('en', 'de', 'jp', 'fr'):
                    lang = None
        try:
            f = open(file, 'r')
        except IOError as e:
            sys.exit("Could not open file for reading: %s" % file)
            
        xml = f.read()
        f.close()
        return self.parse_xml(xml, lang)
        
    def parse_xml(self, xml, lang=None):
        tree = etree.parse(StringIO(xml))
        context = etree.iterparse(StringIO(xml), events=('start', 'end'))
        
        items = self.items
        
        item = {}
        skip = True
        
        for action, elem in context:
            if elem.tag == 'thing-list':
                continue
            
            # Begin new item
            if elem.tag == 'thing' and elem.attrib.get('type') == 'Item':
                if action == 'start':
                    skip = False
                    item = {}
                elif action == 'end':
                    if item['id'] in items:
                        items[item['id']].update(item)
                    else:
                        items[item['id']] = item
                
            # Skip until beginning of item
            if skip:
                continue
            
            # Reached graphic, which is the end
            if elem.tag == 'thing' and elem.attrib.get('type') == 'Graphic' and action == 'start':
                skip = True
                continue
            
            if elem.tag == 'field' and action == 'start':
                continue
            
            name = elem.attrib.get('name')
            
            if not name:
                continue
            
            if elem.text is None:
                text = ""
            else:
                text = elem.text
            
            if isinstance(text, str):
                text = text.strip()
                    
            if self.convert_hex and name in hex_fields:
                text = int(text, 16)
                
            if self.rename_fields and name in self.rename_fields:
                name = self.rename_fields[name]
                
            if lang and name in self.lang_fields:
                item[lang + self.lang_sep + name] = text
            else:
                item[name] = text
                
        self.items = items
        return self.items
                                             