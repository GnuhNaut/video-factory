import os
import glob
import xml.etree.ElementTree as ET

ET.register_namespace('', "http://www.w3.org/2000/svg")

svg_dir = r"d:\Workspace\Video_factory\StickmanFactory\assets\characters"

def process_svg(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    shapes = []
    for elem in root:
        if elem.tag.endswith(('circle', 'line', 'path')):
            r = elem.get('r')
            fill = elem.get('fill')
            is_eye = (r in ['2', '2.5', '3', '4']) or (fill == '#000000')
            if not is_eye:
                shapes.append(elem)
                
    if not shapes:
        return
        
    black_group = []
    for shape in shapes:
        black_shape = ET.Element(shape.tag, shape.attrib)
        black_shape.set('stroke', '#000000')
        black_shape.set('stroke-width', '14')
        black_shape.set('stroke-linecap', 'round')
        black_shape.set('stroke-linejoin', 'round')
        
        shape.set('stroke', '#FFFFFF')
        shape.set('stroke-width', '8')
        shape.set('stroke-linecap', 'round')
        shape.set('stroke-linejoin', 'round')
        
        black_group.append(black_shape)
        
    for b in reversed(black_group):
        root.insert(1, b)

    has_eyes = any((e.get('r') in ['2', '2.5', '3'] or e.get('fill') == '#000000') for e in root if e.tag.endswith('circle'))
    if not has_eyes:
        heads = [e for e in root if e.tag.endswith('circle') and float(e.get('r', 0)) > 10]
        if heads:
            head = heads[0]
            cx = float(head.get('cx', 100))
            cy = float(head.get('cy', 45))
            eye1 = ET.Element('{http://www.w3.org/2000/svg}circle', {'cx': str(cx - 8), 'cy': str(cy - 3), 'r': '2.5', 'fill': '#000000'})
            eye2 = ET.Element('{http://www.w3.org/2000/svg}circle', {'cx': str(cx + 8), 'cy': str(cy - 3), 'r': '2.5', 'fill': '#000000'})
            root.append(eye1)
            root.append(eye2)
            
    tree.write(filepath, encoding='utf-8', xml_declaration=True)
    print(f"Processed: {filepath}")

for fp in glob.glob(os.path.join(svg_dir, '*.svg')):
    process_svg(fp)
