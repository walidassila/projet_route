import re
class Labels:
    def __init__(self, class_colors=None, class_abrv=None):
        default_colors = {
            "faiencage": (255, 0, 0),
            "fissure longitudinal": (0, 255, 0),
            "fissure-transversal": (0, 0, 255),
            "nid de poul": (255, 255, 0),
            "ornierage": (255, 0, 255),
            "pelade": (0, 255, 255),
            "plumage": (128, 0, 128),
            "ressuage": (56, 87, 35)
        }

        default_class_abrv = {
            "faiencage": "Fai",
            "fissure longitudinal": "FL",
            "fissure-transversal": "FT",
            "nid de poul": "NP",
            "ornierage": "Orn",
            "pelade": "Pel",
            "plumage": "Plu",
            "ressuage": "Ress"
        }

        # Mise à jour des valeurs par défaut avec celles fournies (si existantes)
        self.class_colors = {**default_colors, **(class_colors or {})}
        self.class_abrv = {**default_class_abrv, **(class_abrv or {})}



def generate_abbreviation(text, length=4):
    # Séparateurs possibles
    separators = re.compile(r'[ _\.\-]+')
    
    # Trouve tous les séparateurs (pour garder la forme)
    splits = separators.split(text)
    seps = separators.findall(text)
    
    # Abréviation de chaque mot : premières lettres (ou mot entier si plus court)
    abbrs = [word[:length].lower() for word in splits]
    
    # Reconstruire le texte en remettant les séparateurs d'origine
    result = ""
    for i, abbr in enumerate(abbrs):
        result += abbr
        if i < len(seps):
            result += seps[i]
    return result
def remplace_name(model,class_names):
    new_names={}
    for i, full_name in model.names.items():
            if full_name in class_names:
                new_names[i] = class_names[full_name]
            else:
                  new_names[i]=full_name
    return new_names

