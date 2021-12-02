import json

programme = open("moduleProgramme.json")
programme = json.load(programme)
output = []
for data in programme:
    options = {"value": data, "label": data}
    courseName = data.lower()
    if "faculty" not in options:
        options["faculty"] = []

    if "accountancy" in courseName or "business" in courseName or "nanyang technopreneurship centre" in courseName:
        options["faculty"].append("Nanyang Business School (NBS)")

    if "electrical" in courseName:
        options["faculty"].append("School Electrical and Electronic Engineering (EEE)")    
    if ("civil engineering" in courseName or "environmental engineering" in courseName or "information engineering" in courseName or
        "maritime studies"in courseName):
        options["faculty"].append("School of Civil and Environmental Engineering (CEE)")    
    if "aerospace engineering" in courseName or "engineering" in courseName or "mechanical engineering" in courseName:
        options["faculty"].append("School of Mechanical and Aerospace Engineering (MAE)")
    if "bioengineering" in courseName or "chemical" in courseName:
        options["faculty"].append("School of Chemical and Biomedical Engineering (SCBE)")
    if "computer" in courseName or "data science" in courseName:
        options["faculty"].append("School of Computer Science and Engineering (SCSE)")
    if "materials engineering" in courseName:
        options["faculty"].append("School of Materials Science and Engineering (MSE)")
    
    if ("chinese" in courseName or "english" in courseName or "history" in courseName
        or "linguistics" in courseName or "philosophy" in courseName or "english literature" in courseName
        or "humanities" in courseName):
        options["faculty"].append("School of Humanities (SOH)")
    if ("economics" in courseName or "psychology" in courseName or "sociology" in courseName or "public policy" in courseName
        or "media analytics" in courseName or "drama" in courseName or "social sciences"  in courseName):
        options["faculty"].append("School of Social Sciences (SSS)")
    if "communication studies" in courseName:
        options["faculty"].append("Wee Kim Wee School of Communication and Information (WKWSCI)")
    if "art, design & media" in courseName:
        options["faculty"].append("School of Art, Design and Media (ADM)")

    if "biomedical" in courseName or "biological" in courseName:
        options["faculty"].append("School of Biological Sciences (SBS)")
    if ("data science" in courseName or "mathematical" in courseName or "physics" in courseName
        or "chemistry" in courseName or "mathematics" in courseName):
        options["faculty"].append("School of Physical and Mathematical Sciences (SPMS)")    
    if "environmental earth systems science" in courseName:
        options["faculty"].append("The Asian School of the Environment (ASE)")

    if "renaissance engineering" in courseName:
        options["faculty"].append("Renaissance Engineering Programme (REP)")

    if "science, technology & society" in courseName:
        options["faculty"].append("Institute of Science and Technology for Humanity (NISTH)")

    if ("sport science and management" in courseName or "early childhood education" in courseName
    or "education studies" in courseName or "early childhood education" in courseName
    or "music" in courseName or 'special needs education' in courseName
    or 'science of learning' in courseName): 
        options["faculty"].append("National Institute of Education (NIE)")

    if "medicine" in courseName:
        options["faculty"].append("Lee Kong Chian School of Medicine (LKCM)")

    if "university scholars programme" in courseName or "liberal arts" in courseName:
        options["faculty"].append("University Scholars Programme (USP)")

    if "c n yang scholars programme" in courseName:
        options["faculty"].append("C N Yang Scholars Programme")

    if 'design and systems thinking' in courseName:
        options["faculty"].append("Centre for Teaching, Learning & Pedagogy (CTLP)")

    if 'youth work and guidance' in courseName:
        options["faculty"].append("SkillsFuture Work-Study Degree Programmes (WSDPs)")

    if len(options["faculty"]) == 0:
        print(courseName)

        break
    output.append(options)

jsonString = json.dumps(output)
jsonFile = open("ProgrammeData.json", "w")
jsonFile.write(jsonString)
jsonFile.close()
