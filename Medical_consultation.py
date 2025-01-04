# -*- coding: utf-8 -*-
"""
Created on Wed Dec 01 14:25:59 2023

@author: Dr Charles NKUNA
"""
import sys
import sqlite3

from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from os import path
from PyQt5.uic import loadUiType
from PyQt5.QtCore import Qt
# from consultation import Main as ConsultationMain
from mes_consultations import Main as MesConsultationsMain

FORM_CLASS, _ = loadUiType(path.join(path.dirname('__file__'), "login_csmcg.ui"))


class Main(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        # self.consultation_window = None
        # self.user_level = None
        # self.login_lineEdit = None
        self.setupUi(self)
        self.Handle_Buttons()

        # Fixer la taille de la fenêtre (par exemple, 800x600)
        self.setFixedSize(800, 600)

        # Centrer la fenêtre
        self.center_window()

    def center_window(self):
        # Récupérer la géométrie de l'écran
        screen_geometry = QApplication.desktop().availableGeometry(self)
        window_geometry = self.frameGeometry()

        # Calculer le centre de l'écran
        screen_center = screen_geometry.center()

        # Déplacer le rectangle de la fenêtre pour le centrer sur l'écran
        window_geometry.moveCenter(screen_center)

        # Positionner la fenêtre
        self.move(window_geometry.topLeft())

    def showEvent(self, event):
        super(Main, self).showEvent(event)
        self.login_lineEdit.setFocus()

    def Handle_Buttons(self):
        # self.cx_btn.clicked.connect(self.connexion_bdd)
        self.cx_btn.clicked.connect(lambda: self.connexion_bdd(self.login_lineEdit.text(),
                                                               self.mdp_lineEdit.text(),
                                                               self.comboBox_niveau.currentText(),
                                                               self))
        # Associez la touche Entrée (Return) comme raccourci pour le bouton cx_btn
        self.cx_btn.setShortcut(Qt.Key_Return)

        # Connectez la méthode returnButtonPressed au clic du bouton return_btn
        self.cx_btn.clicked.connect(self.returnButtonPressed)

    def connexion_bdd(self, login_lineEdit, mdp_lineEdit, comboBox_niveau, LoginWindow):

        db = sqlite3.connect("croixg.db")
        cursor = db.cursor()

        # app = QApplication([])
        fenetre = QWidget()
        fenetre.setWindowTitle("Cabinet de Soins Médicaux LA CROIX GLORIEUSE")

        cursor.execute("SELECT * FROM cg_connexion WHERE login = ? AND motdepasse = ? AND niveauutilisateur = ?",
                       (login_lineEdit, mdp_lineEdit, comboBox_niveau))
        result = cursor.fetchone()

        if result:
            # QMessageBox.information(fenetre, "Connexion réussie", f"Cliquez sur le bouton <span
            # style='font-weight:bold;color:#00018f;font-size:20px;'>OK</span> ci-dessous pour continuer !")

            # Ne pas Fermer la fenêtre actuelle
            self.hide()

            # Utilisez QTimer.singleShot pour retarder l'affichage de la deuxième fenêtre
            QTimer.singleShot(100, lambda: self.show_mes_consultations_window())

        else:
            QMessageBox.warning(fenetre, "Échec de la connexion", "Identifiants incorrects, Réessayez encore !")

    def show_mes_consultations_window(self):
        # print("Ouverture de la fenêtre ConsultationMain")
        self.login_lineEdit = self.login_lineEdit.text()
        self.user_level = self.comboBox_niveau.currentText()[:-4]

        # Créez la fenêtre secondaire sans définir de parent explicite
        # self.consultation_window = ConsultationMain(self)
        self.mes_consultations_window = MesConsultationsMain(self)

        # Passez l'information de l'utilisateur connecté
        self.mes_consultations_window.set_connected_user(self.login_lineEdit, self.user_level)
        # Affichez la fenêtre secondaire
        self.mes_consultations_window.show()

    def dash(self):
        pass

    def returnButtonPressed(self):
        pass

    # Our code geos here


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Appliquer le style "Fusion" à l'application
    window = Main()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
