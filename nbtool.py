#!/usr/bin/env python3

import json, sys, re

DEBUG=False

def read_json(ipfile):
    #with open(ipfile, 'r') as f:
    with open(ipfile, encoding='utf-8-sig') as json_file:
        #text = json_file.read()
        #json_data = json.loads(text)
        return json.load(json_file)

def pp_json(json_data):
    #print(json_data)
    print(json.dumps(json_data, indent = 4, sort_keys=True))

def pp_nb(json_data):
    print(f"Number of cells: {len(json_data['cells'])} kernel: {json_data['metadata']['kernelspec']['display_name']} nb_format: v{json_data['nbformat']}.{json_data['nbformat_minor']}")
    pp_json(json_data)

def nb_cells(json_data, type=None):
    return len(json_data['cells'])

def write_nb(opfile, json_data):
    with open(opfile, 'w') as json_file:
        json.dump(json_data, json_file)
          
def get_cell(json_data, cellno):
    return json_data['cells'][cellno]   
          
def nb_dump1sourceLine(ipfile):
    json_data = read_json(ipfile)
    print(f"{ipfile}: #cells={nb_cells(json_data)}")
    for cellno in range(nb_cells(json_data)):
          #print(cellno)
          source=json_data['cells'][cellno]['source']
          if len(source) == 0:
              #print("empty")
              continue
          print(f"  cell[{cellno}]source[0]={source[0]}")

def nb_info(ipfile):
    json_data = read_json(ipfile)
    return f"{ipfile}:\n\t#cells={nb_cells(json_data)}"
          
def die(msg):
    sys.stdout.write(f"die: {msg}\n")
    sys.exit(1)

def main():
    MODE='info'
    PROG=sys.argv[0]
    a=1
          
    if len(sys.argv) == 1:
          die("Missing arguments")
          
    if sys.argv[a] == '-f':
          a+=1
          MODE='filter'

    if sys.argv[a] == '-1':
          a+=1
          MODE='dump1l'

    if MODE=='dump1l':
        for ipfile in sys.argv[a:]:
            nb_dump1sourceLine(ipfile)

    if MODE=='info':
        for ipfile in sys.argv[a:]:
            print(nb_info(ipfile))

    if MODE=='filter':
        for ipfile in sys.argv[a:]:
            #print(nb_info(ipfile))
            new_data = filter_nb( read_json(ipfile), DEBUG )
            opfile=ipfile+'.filtered.ipynb'
            write_nb(opfile, new_data)
            nb_info(opfile)

def findInSource(source_lines, match):
    for line in source_lines:
          if match in line:
              print("True:" + line)
              return True
    return False

def substitute_vars_in_line(source_line, slno, VARS_SEEN):
    new_line=source_line
    vars_seen=[]
    for var in VARS_SEEN:
        if '$__'+var in source_line:
            vars_seen.append('__'+var)
            #if DEBUG:
                #print(json_data['cells'][cellno]['source'][slno])
            #json_data['cells'][cellno]['source'][slno]=json_data['cells'][cellno]['source'][slno].replace('$__'+var, VARS_SEEN[var])
            new_line=new_line.replace('$__'+var, VARS_SEEN[var])
            #if DEBUG:
                #print("=>")
                #print(json_data['cells'][cellno]['source'][slno])
                #print(json_data['cells'][cellno]['source'][slno])

    if new_line != source_line:
        if DEBUG:
            print(f"[line{slno}]: {var} seen in '{source_line}' will replace vars [{__vars_seen}]")
            #print(f"{var} seen in '{source_line}' will replace '$__{var}'")
            #print(f"'{source_line}'\n===> '{new_line}'")
            print(f"===> '{new_line}'")
    return new_line

def next_section(current_sections, level, source_line):
    section_num=""
    #break_line=""
    #start_hl=''
    #end_hl=''
    if level == 0:
        current_sections[0]+=1
        current_sections[1]=1
        current_sections[2]=1
        current_sections[3]=1
        #break_line="\n<br />"
        #start_hl='<b>'
        #end_hl='</b>'
        section_num=f"{current_sections[0]}"
    if level == 1:
        current_sections[1]+=1
        current_sections[2]=1
        current_sections[3]=1
        section_num=f"{current_sections[0]}.{current_sections[1]}"
    if level == 2:
        current_sections[2]+=1
        current_sections[3]=1
        section_num=f"{current_sections[0]}.{current_sections[1]}.{current_sections[2]}"
    if level == 3:
        current_sections[3]+=1
        section_num=f"{current_sections[0]}.{current_sections[1]}.{current_sections[2]}.{current_sections[3]}"

    # Remove '#* '
    source_line=source_line[ source_line.find(' '):].lstrip()
    SE_regex = re.compile(r"([\d,\.]+) ") 
    source_line = SE_regex.sub("", source_line)
    return_line = section_num + ' ' + source_line.rstrip() # Remove new-line
    #return_line = break_line + start_hl + section_num + ' ' + source_line + end_hl
    return (level, section_num, return_line)
          
def filter_nb(json_data, DEBUG=False):
    EXCL_FN_regex = re.compile(r"\|?\&?\s*EXCL_FN_.*$") #, re.IGNORECASE)
    include=False
    cells=[]
    VARS_SEEN={}

    toc_cellno=-1
    count_sections=False
    current_sections=[]
    toc_text='<div id="TOC" >\n'

    for cellno in range(nb_cells(json_data)):
          #print(cellno)
          cell_type=json_data['cells'][cellno]['cell_type']
          source_lines=json_data['cells'][cellno]['source']
          if len(source_lines) == 0:
              if DEBUG: print("empty")
              continue
          if '--INCLUDE--SECTION--' in source_lines[0]: 
              include=True
              continue
          if '--EXCLUDE--SECTION--' in source_lines[0]:
              include=False
              continue
          if not include:
              continue

          # Detect TableOfContents Cell No:
          if len(source_lines) > 0 and source_lines[0].find('<div id="TOC"') == 0:
              toc_cellno=cellno
              print(f"ToC cell detected at cellno[{cellno}]")
              count_sections=True
              current_sections.append(0)
              current_sections.append(1)
              current_sections.append(1)
              current_sections.append(1)
              cells.append(cellno)
              continue

          include_cell=True
          for slno in range(len(source_lines)):
              source_line=source_lines[slno]

              # Build up TableOfContents - Count sections headers and retain list for ToC text
              if source_line.find("#") == 0 and count_sections and cell_type == "markdown":
                  toc_line=''
                  level=0
                  if source_line.find("# ") == 0:    (level, section_num, toc_line) = next_section(current_sections, 0, source_line)
                  if source_line.find("## ") == 0:   (level, section_num, toc_line) = next_section(current_sections, 1, source_line)
                  if source_line.find("### ") == 0:  (level, section_num, toc_line) = next_section(current_sections, 2, source_line)
                  if source_line.find("#### ") == 0: (level, section_num, toc_line) = next_section(current_sections, 3, source_line)

                  toc_link = f'<a href="#sec{section_num}" /> {toc_line} </a>'
                  if level == 0:
                      toc_text += f'\n<br /> <div id="TOC{section_num}" > <b> {toc_link} </b></div>\n'
                  else:
                      toc_text += f'* {toc_link}\n'

                  if "." in section_num:
                      top_section_num = section_num[ : section_num.find(".") ]
                  else:
                      top_section_num = section_num 

                  json_data['cells'][cellno]['source'][slno] =\
                          f'<a href="#TOC{top_section_num}" > Return to INDEX </a>\n' + \
                          source_line[ :1+source_line.find(' ') ] + f'<div id="sec{section_num}" > '+toc_line+' </div>'

              if cell_type == "markdown" and \
                 (source_line.find("**RedNote") != -1 or \
                  source_line.find("**BlueNote") != -1 or \
                  source_line.find("**GreenNote") != -1):
                     source_line=source_line.replace("**RedNote", "<div class='red_bold_text'>Note")
                     source_line=source_line.replace("**BlueNote", "<div class='blue_bold_text'>Note")
                     source_line=source_line.replace("**GreenNote", "<div class='green_bold_text'>Note")
                     source_line=source_line.replace("**", "</div>")
                     json_data['cells'][cellno]['source'][slno] = source_line

              # Pragma FOREACH (use singular form of variable e.g. __POD_IP which will be populated form __POD_IPS)
              if source_line.find("FOREACH __") == 0:
                  rest_line=source_line[ len("FOREACH __"): ].lstrip()
                  space_pos=rest_line.find(" ")
                  if space_pos > 1:
                      VAR_NAME=rest_line[:space_pos]
                      VAR_NAME_S=VAR_NAME+'S'

                      cmd_line=rest_line[space_pos:].lstrip()
                      new_line=''

                      #print(f"Vars seen so far={VARS_SEEN.keys()}")
                      if not VAR_NAME_S in VARS_SEEN:
                          print(f"Vars seen so far={VARS_SEEN.keys()}")
                          die(f"Var <{VAR_NAME_S}> not seen")
                      values=VARS_SEEN[VAR_NAME_S].split()
                      for value in values:
                          new_line+=cmd_line\
                              .replace('\$__', '$__')\
                                  .replace('\<', '<')\
                                  .replace('\>', '>')\
                                  .replace('$__'+VAR_NAME, value)+'\n'
                      #new_line=substitute_vars_in_line(cmd, slno, VARS_SEEN)

                      json_data['cells'][cellno]['source'][slno]=new_line
                      if new_line != source_line: print(new_line)
                  continue

              # Pragma $__ variables ...
              # If $__variables seen in source then we modify the source to replace $_var by it's value
              for var in VARS_SEEN:
                  if '$__'+var in source_line:
                      new_line=substitute_vars_in_line(source_line, slno, VARS_SEEN)
                      #if DEBUG:
                      #    print(f"{var} seen in {source_line} will replace '$__{var}'")
                      #    print(json_data['cells'][cellno]['source'][slno])
                      #json_data['cells'][cellno]['source'][slno]=json_data['cells'][cellno]['source'][slno].replace('$__'+var, VARS_SEEN[var])
                      #if DEBUG:
                      #    print("=>")
                      #    print(json_data['cells'][cellno]['source'][slno])
                      json_data['cells'][cellno]['source'][slno]=new_line
                      
                      #if not findInSource(source_lines, "SET_VAR_"):

              # Pragma | EXCL_FN_(HIDE_|HIGHLIGHT*)
              if "EXCL_FN_" in source_line:
                  if DEBUG:
                      orig=json_data['cells'][cellno]['source'][slno]
                  json_data['cells'][cellno]['source'][slno] = \
                      EXCL_FN_regex.sub("", json_data['cells'][cellno]['source'][slno])
                  if DEBUG:
                      new=json_data['cells'][cellno]['source'][slno]
                      if new != orig:
                          print(f"{orig.rstrip()} => {new.rstrip()}")
           
              # Pragma #EXCLUDE (cell):
              if source_line.find("#EXCLUDE") == 0:
                  include_cell=False
                  continue

              # Pragma WAIT:
              if source_line.find("WAIT")     == 0:
                  include_cell=False
                  continue

              # Pragma RETURN:
              if source_line.find("RETURN")     == 0:
                  json_data['cells'][cellno]['source'][slno]=''
                  continue

              # NOT Pragma SET_VAR:
              if source_line.find("SET_VAR_") == -1: continue

              # Pragma SET_VAR:
              include_cell=False

              # If SET_VAR seen in source, we exclude **this cell** and set the variable
              VAR_NAME=source_line[len("SET_VAR_"):].rstrip()
              if " " in VAR_NAME: VAR_NAME=VAR_NAME[:VAR_NAME.find(" ")]
              VAR_VALUE="var_value"
              VARS_SEEN[VAR_NAME]=VAR_VALUE
              if DEBUG: print(f"SET_VAR {VAR_NAME}={VAR_VALUE}")
              #print(f"VAR_NAME={VAR_NAME}")
              #outputs = json_data['cells'][cellno]['outputs']
              if json_data['cells'][cellno]['outputs']:
                  for opno in range(len(json_data['cells'][cellno]['outputs'])):
                      if 'text' in json_data['cells'][cellno]['outputs'][opno]:
                          for textno in range(len(json_data['cells'][cellno]['outputs'][opno]['text'])):
                               VAR_SET='VAR __'+VAR_NAME+'='
                               if json_data['cells'][cellno]['outputs'][opno]['text'][textno].find(VAR_SET)==0:
                                   VAR_VALUE=json_data['cells'][cellno]['outputs'][opno]['text'][textno][len(VAR_SET):].rstrip()
                                   if DEBUG: print(f"VAR {VAR_NAME}={VAR_VALUE}")
                                   VARS_SEEN[VAR_NAME]=VAR_VALUE
                                   #print(VAR_VALUE)

                                   #json_data['cells'][cellno]['outputs'][opno]['texts'][textno].replace('$'+VAR_NAME, VAR_VALUE)
              #if "SET_VAR" in source_line:
          if include_cell:
              cells.append(cellno)
          
    #            #if source_lines[0].find("SET_VAR_") == -1:
    #             if not findInSource(source_lines, "SET_VAR_"):
    #                 cells.append(cellno)
    #                 continue
           
    # Patch TableOfContents:
    toc_text+='</div>'
    if DEBUG:
        print(f"ToC set to <{toc_text}>")
    json_data['cells'][toc_cellno]['source'] = [ toc_text ]

    print(f"cells to include[#{len(cells)}]=[{cells}]")
    cells.reverse()
    
    for cellno in range(nb_cells(json_data)-1, -1, -1):
        #print(cellno)
        if not cellno in cells:
            #print(f"del(cells[{cellno}])")
            del(json_data['cells'][cellno])

    print(f"cells to include[#{len(cells)}]=[{cells}]")
    return json_data

if __name__ == "__main__":
    main()
