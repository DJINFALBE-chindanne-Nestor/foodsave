# ============================================================
# STRUCTURE GEOGRAPHIQUE OFFICIELLE - TCHAD ET CAMEROUN
# ------------------------------------------------------------
# Le Tchad compte 23 regions depuis 2012.
# Le Cameroun compte 10 regions depuis 2008.
#
# Structure Python :
#   REGIONS = {
#       "Tchad": {
#           "Mayo-Kebbi-Ouest": {
#               "climat": "soudan",
#               "departements": {
#                   "Mayo-Binder": ["Binder", "Lere", ...],
#                   "Mayo-Kebbi": ["Pala", "Lagon", ...],
#               }
#           },
#           ...
#       },
#       "Cameroun": { ... }
#   }
#
# "climat" sert a determiner les conseils de conservation adaptes :
#   - "sahel"  : tres chaud et sec
#   - "soudan" : chaud, humide en saison des pluies
#   - "humide" : chaud et tres humide toute l'annee
# ============================================================

REGIONS = {

    # ========================================================
    # TCHAD - 23 regions
    # ========================================================
    "Tchad": {

        # -------- Zone sahelienne (extreme nord, nord, ouest) --------
        "N'Djamena": {
            "climat": "sahel",
            "departements": {
                "N'Djamena": ["N'Djamena"]
            }
        },
        "Borkou": {
            "climat": "sahel",
            "departements": {
                "Borkou": ["Faya-Largeau"],
                "Borkou Yala": ["Kirdimi"],
                "Yamoussa": ["Yarda"]
            }
        },
        "Ennedi-Est": {
            "climat": "sahel",
            "departements": {
                "Am-Djarass": ["Am-Djarass"],
                "Wadi Hawar": ["Bahaï"]
            }
        },
        "Ennedi-Ouest": {
            "climat": "sahel",
            "departements": {
                "Fada": ["Fada"],
                "Mourtcha": ["Gouro"]
            }
        },
        "Tibesti": {
            "climat": "sahel",
            "departements": {
                "Tibesti Est": ["Bardaï"],
                "Tibesti Ouest": ["Aouzou"]
            }
        },
        "Wadi-Fira": {
            "climat": "sahel",
            "departements": {
                "Biltine": ["Biltine"],
                "Dar Tama": ["Guereda"],
                "Kobe": ["Iriba"]
            }
        },
        "Batha": {
            "climat": "sahel",
            "departements": {
                "Batha Est": ["Oum-Hadjer"],
                "Batha Ouest": ["Ati"],
                "Fitri": ["Yao"]
            }
        },
        "Kanem": {
            "climat": "sahel",
            "departements": {
                "Kanem": ["Mao"],
                "Nord Kanem": ["Nokou"],
                "Wadi Bissam": ["Mondo"]
            }
        },
        "Lac": {
            "climat": "sahel",
            "departements": {
                "Mamdi": ["Bol"],
                "Wayi": ["Ngouri"],
                "Fouli": ["Liwa"]
            }
        },
        "Barh-El-Gazel": {
            "climat": "sahel",
            "departements": {
                "Barh-El-Gazel": ["Moussoro"],
                "Centre": ["Moussoro"],
                "Sud": ["Atrone"]
            }
        },
        "Hadjer-Lamis": {
            "climat": "sahel",
            "departements": {
                "Dababa": ["Bokoro"],
                "Dagana": ["Massakory"],
                "Haraze-Al-Biar": ["N'Djamena Fara"]
            }
        },

        # -------- Zone soudanienne (centre et sud) --------
        "Chari-Baguirmi": {
            "climat": "soudan",
            "departements": {
                "Baguirmi": ["Massénya"],
                "Chari": ["Mandélia"],
                "Loug-Chari": ["Bousso"]
            }
        },
        "Guera": {
            "climat": "soudan",
            "departements": {
                "Guera": ["Mongo"],
                "Abtouyour": ["Bitkine"],
                "Barh Signaka": ["Melfi"],
                "Mangalmé": ["Mangalmé"]
            }
        },
        "Mayo-Kebbi-Est": {
            "climat": "soudan",
            "departements": {
                "Mayo-Boneye": ["Bongor"],
                "Mayo-Louti": ["Guelendeng"],
                "Mont Illi": ["Fianga"]
            }
        },
        "Mayo-Kebbi-Ouest": {
            "climat": "soudan",
            "departements": {
                "Mayo-Binder": ["Binder", "Léré"],
                "Mayo-Kebbi": ["Pala", "Lagon"],
                "Mayo-Dallah": ["Pala"]
            }
        },
        "Tandjile": {
            "climat": "soudan",
            "departements": {
                "Tandjile Est": ["Laï"],
                "Tandjile Ouest": ["Kelo"],
                "Tandjile": ["Bere"]
            }
        },
        "Logone-Occidental": {
            "climat": "soudan",
            "departements": {
                "Logone Occidental": ["Moundou"],
                "Dodje": ["Beinamar"],
                "Gueni": ["Krim Krim"],
                "Lac Wey": ["Moundou"]
            }
        },
        "Logone-Oriental": {
            "climat": "soudan",
            "departements": {
                "Logone Oriental": ["Doba"],
                "Nya": ["Bebedjia"],
                "Pende": ["Gore"],
                "Monts de Lam": ["Baibokoum"]
            }
        },
        "Moyen-Chari": {
            "climat": "soudan",
            "departements": {
                "Barh Kôh": ["Sarh"],
                "Lac Iro": ["Boum Kebir"],
                "Grande Sido": ["Maro"]
            }
        },
        "Mandoul": {
            "climat": "soudan",
            "departements": {
                "Mandoul Occidental": ["Koumra"],
                "Mandoul Oriental": ["Beboto"],
                "Barh Sara": ["Moïssala"]
            }
        },
        "Salamat": {
            "climat": "soudan",
            "departements": {
                "Salamat": ["Am Timan"],
                "Abtouyour": ["Am Timan"],
                "Barh Azoum": ["Am Timan"]
            }
        },
        "Sila": {
            "climat": "soudan",
            "departements": {
                "Sila": ["Goz Beida"],
                "Djourf Al Ahmar": ["Am Dam"],
                "Kimiti": ["Goz Beida"]
            }
        }
    },

    # ========================================================
    # CAMEROUN - 10 regions
    # ========================================================
    "Cameroun": {

        # -------- Zone sahelienne (Extreme-Nord) --------
        "Extreme-Nord": {
            "climat": "sahel",
            "departements": {
                "Diamare": ["Maroua", "Bogo"],
                "Logone-et-Chari": ["Kousseri", "Makary"],
                "Mayo-Kani": ["Kaele", "Guider"],
                "Mayo-Sava": ["Mora"],
                "Mayo-Tsanaga": ["Mokolo"],
                "Meme": ["Mora"]
            }
        },

        # -------- Zone soudanienne (Nord, Adamaoua) --------
        "Nord": {
            "climat": "soudan",
            "departements": {
                "Benoue": ["Garoua", "Lagdo"],
                "Faro": ["Poli"],
                "Mayo-Louti": ["Guider"],
                "Mayo-Rey": ["Tchollire"]
            }
        },
        "Adamaoua": {
            "climat": "soudan",
            "departements": {
                "Djerem": ["Tibati"],
                "Faro-et-Deo": ["Tignere"],
                "Mayo-Banyo": ["Banyo"],
                "Mbere": ["Meiganga"],
                "Vina": ["Ngaoundere"]
            }
        },

        # -------- Zone soudano-humide (Centre, Ouest, Nord-Ouest) --------
        "Centre": {
            "climat": "humide",
            "departements": {
                "Haute-Sanaga": ["Nanga-Eboko"],
                "Lekie": ["Monatele"],
                "Mbam-et-Inoubou": ["Bafia"],
                "Mbam-et-Kim": ["Ntui"],
                "Mefou-et-Afamba": ["Mfou"],
                "Mefou-et-Akono": ["Ngoumou"],
                "Mfoundi": ["Yaounde"],
                "Nyong-et-Kelle": ["Eseka"],
                "Nyong-et-Mfoumou": ["Akonolinga"],
                "Nyong-et-Soo": ["Mbalmayo"]
            }
        },
        "Ouest": {
            "climat": "humide",
            "departements": {
                "Bamboutos": ["Mbouda"],
                "Haut-Nkam": ["Bafang"],
                "Hauts-Plateaux": ["Baham"],
                "Koung-Khi": ["Bandjoun"],
                "Menoua": ["Dschang"],
                "Mifi": ["Bafoussam"],
                "Nde": ["Bangangte"],
                "Noun": ["Foumban"]
            }
        },
        "Nord-Ouest": {
            "climat": "humide",
            "departements": {
                "Boyo": ["Fundong"],
                "Bui": ["Kumbo"],
                "Donga-Mantung": ["Nkambé"],
                "Menchum": ["Wum"],
                "Mezam": ["Bamenda"],
                "Momo": ["Mbengwi"],
                "Ngo-Ketunjia": ["Ndop"]
            }
        },

        # -------- Zone forestiere humide (Sud, Littoral, Sud-Ouest, Est) --------
        "Littoral": {
            "climat": "humide",
            "departements": {
                "Moungo": ["Nkongsamba"],
                "Nkam": ["Yabassi"],
                "Sanaga-Maritime": ["Edea"],
                "Wouri": ["Douala"]
            }
        },
        "Sud": {
            "climat": "humide",
            "departements": {
                "Dja-et-Lobo": ["Sangmelima"],
                "Mvila": ["Ebolowa"],
                "Ocean": ["Kribi"],
                "Vallee-du-Ntem": ["Ambam"]
            }
        },
        "Sud-Ouest": {
            "climat": "humide",
            "departements": {
                "Fako": ["Limbe", "Buea"],
                "Koupe-Manengouba": ["Bangem"],
                "Lebialem": ["Menji"],
                "Manyu": ["Mamfe"],
                "Meme": ["Kumba"],
                "Ndian": ["Mundemba"]
            }
        },
        "Est": {
            "climat": "humide",
            "departements": {
                "Boumba-et-Ngoko": ["Yokadouma"],
                "Haut-Nyong": ["Abong-Mbang"],
                "Kadey": ["Batouri"],
                "Lom-et-Djerem": ["Bertoua"]
            }
        }
    }
}


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def liste_pays():
    """Retourne la liste des pays disponibles : ['Tchad', 'Cameroun']."""
    return list(REGIONS.keys())


def liste_regions(pays):
    """Retourne la liste des regions d'un pays donne."""
    return list(REGIONS.get(pays, {}).keys())


def liste_villes(pays, region):
    """
    Retourne la liste de toutes les villes d'une region donnee.
    On aplatit les departements : on ne garde que les villes.
    """
    villes = []
    departements = REGIONS.get(pays, {}).get(region, {}).get("departements", {})
    for dep, villes_dep in departements.items():
        for v in villes_dep:
            villes.append(v)
    # On trie par ordre alphabetique et on supprime les doublons.
    return sorted(set(villes))


def get_climat(pays, region):
    """Retourne le code climat ('sahel', 'soudan', 'humide') d'une region."""
    return REGIONS.get(pays, {}).get(region, {}).get("climat", "soudan")


def trouver_region(pays, ville):
    """
    Retrouve la region a laquelle appartient une ville.
    Retourne None si la ville n'est pas trouvee.
    """
    for region, data in REGIONS.get(pays, {}).items():
        for dep, villes in data.get("departements", {}).items():
            if ville in villes:
                return region
    return None