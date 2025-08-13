import re

import re

def generate_model_abbreviations(names_dict):
    """
    Génère un dictionnaire d'abréviations à partir des noms du modèle.

    Args:
        names_dict (dict): dictionnaire {id: nom_classe}

    Returns:
        dict: {id_classe: abréviation}
    """
    abbreviations = {}
    separators = re.compile(r'[ _\.\-/#]+')  # espaces, _, ., -, /, #

    for cls_id, cls_name in names_dict.items():
        # Découper le nom en mots selon les séparateurs
        words = separators.split(cls_name)
        words = [w for w in words if w]  # supprimer les éventuels vides

        if len(words) > 1:
            # Plusieurs mots → première lettre de chaque mot
            abbr = ''.join([w[0].upper() for w in words])
        else:
            # Un seul mot → 3 premiers caractères
            abbr = words[0][:3].upper()

        abbreviations[cls_id] = abbr

    return abbreviations


a={0: 'faiencage',
 1: 'fissure longitudinal#poo',
 2: 'fissure-transversal',
 3: 'nid de poul',
 4: 'ornierage',
 5: 'pelade',
 6: 'plumage',
 7: 'ressuage'}

print(generate_model_abbreviations(a))