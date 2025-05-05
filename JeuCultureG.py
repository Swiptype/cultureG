import tkinter as tk
from tkinter import messagebox
import Levenshtein
import random
import os
from num2words import num2words

def reponse_proche(utilisateur, correcte):
    utilisateur = utilisateur.strip().lower()
    correcte = correcte.strip().lower()

    variations_utilisateur = set()
    variations_correcte = set()

    variations_utilisateur.add(utilisateur)
    variations_correcte.add(correcte)

    if utilisateur.isdigit():
        try:
            lettre = num2words(int(utilisateur), lang='fr')
            variations_utilisateur.add(lettre)
        except:
            pass
    if correcte.isdigit():
        try:
            lettre = num2words(int(correcte), lang='fr')
            variations_correcte.add(lettre)
        except:
            pass

    try:
        nombre_utilisateur = int(''.join(filter(str.isdigit, utilisateur)))
        variations_utilisateur.add(num2words(nombre_utilisateur, lang='fr'))
        variations_utilisateur.add(str(nombre_utilisateur))
    except:
        pass

    try:
        nombre_correcte = int(''.join(filter(str.isdigit, correcte)))
        variations_correcte.add(num2words(nombre_correcte, lang='fr'))
        variations_correcte.add(str(nombre_correcte))
    except:
        pass

    for u in variations_utilisateur:
        for c in variations_correcte:
            distance = Levenshtein.distance(u, c)
            if distance <= 2:
                return True
    return False

def charger_questions_simple(fichier):
    with open(fichier, 'r', encoding='utf-8') as f:
        lignes = f.readlines()

    questions = []
    for i in range(0, len(lignes), 2):
        try:
            question = lignes[i].strip().split(":", 1)[1].strip()
            reponse = lignes[i + 1].strip().split(":", 1)[1].strip()
            questions.append((question, reponse))
        except IndexError:
            print(f"Erreur à la ligne {i} ou {i+1} : format inattendu")
        except Exception as e:
            print(f"Autre erreur à la ligne {i}: {e}")
    return questions

def charger_questions_qcm(fichier):
    with open(fichier, 'r', encoding='utf-8') as f:
        lignes = f.readlines()

    questions = []
    i = 0
    while i < len(lignes):
        question = lignes[i].strip().split(":", 1)[1].strip()
        choix = lignes[i + 1].strip().split(":", 1)[1].strip().split("|")
        reponse = lignes[i + 2].strip().split(":", 1)[1].strip()
        questions.append((question, choix, reponse))
        i += 3
    return questions

def charger_questions_vf(fichier):
    with open(fichier, 'r', encoding='utf-8') as f:
        lignes = f.readlines()

    questions = []
    for i in range(0, len(lignes), 2):
        question = lignes[i].strip().split(":", 1)[1].strip()
        reponse = lignes[i + 1].strip().split(":", 1)[1].strip()
        questions.append((question, reponse))
    return questions

class JeuMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Jeu de Culture Générale")
        self.menu()

    def menu(self):
        self.clear()
        tk.Label(self.root, text="Choisis une catégorie", font=("Helvetica", 16)).pack(pady=20)

        tk.Button(self.root, text="Réponses simples", width=25, command=self.lancer_simple).pack(pady=5)
        tk.Button(self.root, text="QCM", width=25, command=self.lancer_qcm).pack(pady=5)
        tk.Button(self.root, text="Vrai ou Faux", width=25, command=self.lancer_vf).pack(pady=5)

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def lancer_simple(self):
        questions = charger_questions_simple("questions_simple.txt")
        self.clear()
        JeuSimple(self.root, questions, retour=self.menu)

    def lancer_qcm(self):
        questions = charger_questions_qcm("questions_qcm.txt")
        self.clear()
        JeuQCM(self.root, questions, retour=self.menu)

    def lancer_vf(self):
        questions = charger_questions_vf("questions_vf.txt")
        self.clear()
        JeuVF(self.root, questions, retour=self.menu)

class JeuSimple:
    def __init__(self, master, questions, retour):
        self.master = master
        self.questions = questions
        random.shuffle(self.questions)
        self.index = 0
        self.score = 0
        self.retour = retour
        self.historique = []

        self.label_question = tk.Label(master, text="", wraplength=400, font=("Helvetica", 14))
        self.label_question.pack(pady=20)

        self.entree_reponse = tk.Entry(master, font=("Helvetica", 12))
        self.entree_reponse.pack()

        self.bouton_valider = tk.Button(master, text="Valider", command=self.verifier_reponse)
        self.bouton_valider.pack(pady=10)

        self.label_resultat = tk.Label(master, text="", font=("Helvetica", 12))
        self.label_resultat.pack()

        self.label_infos = tk.Label(master, text="", font=("Helvetica", 10))
        self.label_infos.pack(pady=5)

        self.bouton_retour = tk.Button(master, text="Retour au menu", command=self.retour)
        self.bouton_retour.pack(pady=10)

        self.afficher_question()

    def afficher_question(self):
        question, _ = self.questions[self.index]
        self.label_question.config(text=question)
        self.entree_reponse.delete(0, tk.END)
        self.label_resultat.config(text="")
        self.label_infos.config(text=f"Score : {self.score} | Questions restantes : {len(self.questions) - self.index}")

    def verifier_reponse(self):
        reponse_utilisateur = self.entree_reponse.get()
        _, bonne_reponse = self.questions[self.index]

        if reponse_proche(reponse_utilisateur, bonne_reponse):
            self.label_resultat.config(text="✅ Bonne réponse !", fg="green")
            self.score += 1
            self.historique.append(f"Q : {self.questions[self.index][0]} | Réponse : {reponse_utilisateur} ✅")
        else:
            self.label_resultat.config(text=f"❌ Mauvaise réponse. Rép. : {bonne_reponse}", fg="red")
            self.historique.append(f"Q : {self.questions[self.index][0]} | Réponse : {reponse_utilisateur} ❌ (Bonne réponse : {bonne_reponse})")

        self.index += 1
        if self.index < len(self.questions):
            self.master.after(2000, self.afficher_question)
        else:
            self.master.after(3000, self.fin_jeu)

    def fin_jeu(self):
        self.label_question.config(text=f"✅ Fin du jeu ! Score final : {self.score} / {len(self.questions)}")
        self.entree_reponse.destroy()
        self.bouton_valider.destroy()
        self.label_resultat.destroy()
        self.label_infos.destroy()
        self.bouton_retour.destroy()

        with open("historique_reponses.txt", "w", encoding="utf-8") as f:
            for ligne in self.historique:
                f.write(ligne + "\n")

        self.bouton_voir_historique = tk.Button(self.master, text="Voir l'historique", command=self.ouvrir_historique)
        self.bouton_voir_historique.pack(pady=5)

        self.bouton_rejouer = tk.Button(self.master, text="Rejouer", command=self.rejouer)
        self.bouton_rejouer.pack(pady=5)

        self.bouton_retour = tk.Button(self.master, text="Retour au menu", command=self.retour)
        self.bouton_retour.pack(pady=5)

    def rejouer(self):
        # Relance le même mode avec les mêmes questions mélangées
        self.bouton_rejouer.destroy()
        self.bouton_retour.destroy()
        self.bouton_voir_historique.destroy()
        self.__init__(self.master, self.questions, self.retour)

    def ouvrir_historique(self):
        os.startfile("historique_reponses.txt")



class JeuQCM:
    def __init__(self, master, questions, retour):
        self.master = master
        self.questions = questions
        random.shuffle(self.questions)
        self.index = 0
        self.score = 0
        self.retour = retour
        self.var_choix = tk.StringVar()
        self.widgets_choix = []

        self.label_question = tk.Label(master, text="", wraplength=400, font=("Helvetica", 14))
        self.label_question.pack(pady=20)

        self.frame_choix = tk.Frame(master)
        self.frame_choix.pack()

        self.bouton_valider = tk.Button(master, text="Valider", command=self.verifier_reponse)
        self.bouton_valider.pack(pady=10)

        self.label_resultat = tk.Label(master, text="", font=("Helvetica", 12))
        self.label_resultat.pack()

        self.label_infos = tk.Label(master, text="", font=("Helvetica", 10))
        self.label_infos.pack(pady=5)

        self.bouton_retour = tk.Button(master, text="Retour au menu", command=self.retour)
        self.bouton_retour.pack(pady=10)

        self.afficher_question()

    def afficher_question(self):
        question, choix, _ = self.questions[self.index]
        self.label_question.config(text=question)
        self.var_choix.set("")
        for widget in self.widgets_choix:
            widget.destroy()
        self.widgets_choix = []

        for option in choix:
            bouton = tk.Radiobutton(self.frame_choix, text=option.strip(), variable=self.var_choix, value=option.strip(), font=("Helvetica", 12))
            bouton.pack(anchor="w")
            self.widgets_choix.append(bouton)

        self.label_resultat.config(text="")
        self.label_infos.config(text=f"Score : {self.score} | Questions restantes : {len(self.questions) - self.index}")

    def verifier_reponse(self):
        selection = self.var_choix.get()
        _, _, bonne_reponse = self.questions[self.index]

        if selection == bonne_reponse:
            self.label_resultat.config(text="✅ Bonne réponse !", fg="green")
            self.score += 1
        else:
            self.label_resultat.config(text=f"❌ Mauvaise réponse. Rép. : {bonne_reponse}", fg="red")

        self.index += 1
        if self.index < len(self.questions):
            self.master.after(2000, self.afficher_question)
        else:
            self.master.after(3000, self.fin_jeu)

    def fin_jeu(self):
        self.label_question.config(text=f"✅ Fin du QCM ! Score final : {self.score} / {len(self.questions)}")
        for widget in self.widgets_choix:
            widget.destroy()
        self.frame_choix.destroy()
        self.bouton_valider.destroy()
        self.label_resultat.destroy()
        self.label_infos.destroy()
        self.bouton_retour.destroy()

        self.bouton_rejouer = tk.Button(self.master, text="Rejouer", command=self.rejouer)
        self.bouton_rejouer.pack(pady=5)

        self.bouton_retour = tk.Button(self.master, text="Retour au menu", command=self.retour)
        self.bouton_retour.pack(pady=5)

    def rejouer(self):
        self.bouton_rejouer.destroy()
        self.bouton_retour.destroy()
        self.__init__(self.master, self.questions, self.retour)


class JeuVF:
    def __init__(self, master, questions, retour):
        self.master = master
        self.questions = questions
        random.shuffle(self.questions)
        self.index = 0
        self.score = 0
        self.retour = retour

        self.label_question = tk.Label(master, text="", wraplength=400, font=("Helvetica", 14))
        self.label_question.pack(pady=20)

        self.bouton_vrai = tk.Button(master, text="Vrai", width=10, command=lambda: self.verifier_reponse("Vrai"))
        self.bouton_faux = tk.Button(master, text="Faux", width=10, command=lambda: self.verifier_reponse("Faux"))
        self.bouton_vrai.pack()
        self.bouton_faux.pack()

        self.label_resultat = tk.Label(master, text="", font=("Helvetica", 12))
        self.label_resultat.pack()

        self.label_infos = tk.Label(master, text="", font=("Helvetica", 10))
        self.label_infos.pack(pady=5)

        self.bouton_retour = tk.Button(master, text="Retour au menu", command=self.retour)
        self.bouton_retour.pack(pady=10)

        self.afficher_question()

    def afficher_question(self):
        question, _ = self.questions[self.index]
        self.label_question.config(text=question)
        self.label_resultat.config(text="")
        self.label_infos.config(text=f"Score : {self.score} | Questions restantes : {len(self.questions) - self.index}")

    def verifier_reponse(self, choix):
        _, bonne_reponse = self.questions[self.index]
        if choix.lower() == bonne_reponse.lower():
            self.label_resultat.config(text="✅ Bonne réponse !", fg="green")
            self.score += 1
        else:
            self.label_resultat.config(text=f"❌ Mauvaise réponse. Rép. : {bonne_reponse}", fg="red")

        self.index += 1
        if self.index < len(self.questions):
            self.master.after(2000, self.afficher_question)
        else:
            self.master.after(3000, self.fin_jeu)

    def fin_jeu(self):
        self.label_question.config(text=f"✅ Fin du Vrai/Faux ! Score final : {self.score} / {len(self.questions)}")
        self.bouton_vrai.destroy()
        self.bouton_faux.destroy()
        self.label_resultat.destroy()
        self.label_infos.destroy()
        self.bouton_retour.destroy()

        self.bouton_rejouer = tk.Button(self.master, text="Rejouer", command=self.rejouer)
        self.bouton_rejouer.pack(pady=5)

        self.bouton_retour = tk.Button(self.master, text="Retour au menu", command=self.retour)
        self.bouton_retour.pack(pady=5)

    def rejouer(self):
        self.bouton_rejouer.destroy()
        self.bouton_retour.destroy()
        self.__init__(self.master, self.questions, self.retour)



# Lancement du jeu
if __name__ == "__main__":
    root = tk.Tk()
    app = JeuMenu(root)
    root.mainloop()
