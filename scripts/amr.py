# modules
"""
Module amr : définit la classe AMR, qui analyse une phrase en AMR avec amrlib,
lit le graphe avec Penman et extrait un triplet (agent, action, patient).
Ce module est importé par main.py ; il ne se lance pas tout seul.
"""

import penman

class AMR:
    """
    Un objet qui représente une phrase analysée en AMR

    Propriétés publiques :
        phrase : phrase (str) en lecture seule

    Méthodes publiques :
        concept_digit : concept_digit : reçoit un concept AMR (str) ; renvoie le concept sans son
                        numéro de sens final (ex. play-11 -- > play, look-up-01 --> look-up), 
                        ou le concept inchangé s'il n'a pas de numéro (ex. girl)
        find_concept  : reçoit une variable du graphe (str, ex. g) ; renvoie le
                        concept de cette variable, sans numéro de sens et en
                        minuscules, ou None si la phrase ne la contient pas
        find_argument : reçoit une variable (str) et un role AMR (str) ;
                        renvoie la variable de l'enfant relié à cette variable par
                        ce role, peut renvoyer None si la phrase ne contient pas 
                        de variable ou si aucun arc ne porte ce role
        triplet_amr   : ne reçoit rien ; renvoie un tuple (agent, action, patient) de
                        concepts au même format que le triplet en dépendances : 
                        action = concept de la racine, agent = concept de l'enfant (:ARG0),
                        patient = concept de l'enfant (:ARG1). L'agent et le patient valent 
                        None s'ils ne sont pas trouvés. Renvoie None si le graphe n'a pas 
                        de racine.

    Attributs privés:
        parsed_phrase : le graphe AMR en texte au format Penamt (str), produit par amrlib
        graph         : le graphe Penman obtenu à partir de la phrase parsée
    """

    def __init__(self, phrase, model):
        self.phrase = phrase
        self.parsed_phrase = model.parse_sents([self.phrase])[0] # le premier element parce que la liste contient qu'un seul element
        self.graph = penman.decode(self.parsed_phrase)

    def concept_digit(self, concept):
        word = concept.rsplit("-", maxsplit=1)
        if word[-1].isdigit():
            return word[0]
        else:
            return concept

    def find_concept(self, var):
        if var is None:
            return None
        for i in self.graph.instances():
            if i.source == var:
                return self.concept_digit(i.target).lower()
        return None

    def find_argument(self, var, role):
        if var is None:
            return None
        for i in self.graph.edges():
            if i.source == var and i.role == role:
                return i.target
        return None

    def triplet_amr(self):
        action = self.find_concept(self.graph.top)
        if action is None:
            return None

        agent = self.find_concept(self.find_argument(self.graph.top, ":ARG0"))

        patient = self.find_concept(self.find_argument(self.graph.top, ":ARG1"))
        # :ARG1 n'est pas toujours un patient -->
        # !!! DECOMMENTER POUR TESTER !!!
        # if patient == None:
            # patient = self.find_concept(self.find_argument(self.graph.top, ":ARG2"))

        # !!! DECOMMENTER POUR TESTER PHRASES NEGATIVES !!!
        # negation = False
        # for i in self.graph.attributes():
        #     if i.source == self.graph.top and i.role == ":polarity" and i.target == "-":
        #         negation = True

        return agent, action, patient # negation