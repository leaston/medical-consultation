# -*- coding: utf-8 -*-
"""
Created on Wed Dec 01 14:25:59 2023

@author: Dr Charles NKUNA
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QDateTimeEdit, QLabel, QMessageBox, QPushButton
from PyQt5.QtCore import QDateTime, QTimer
from PyQt5.QtWidgets import QApplication

import sys

from os import path

from PyQt5.uic import loadUiType
from PyQt5.QtCore import Qt

FORM_CLASS, _ = loadUiType(path.join(path.dirname('__file__'), "csm-cg.ui"))

import sqlite3

from consultation import Main as ConsultationMain


class Main(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Handle_Buttons()

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

        app = QApplication([])
        fenetre = QWidget()
        fenetre.setWindowTitle("Cabinet de Soins Médicaux LA CROIX GLORIEUSE")

        cursor.execute("SELECT * FROM cg_connexion WHERE login = ? AND motdepasse = ? AND niveauutilisateur = ?",
                       (login_lineEdit, mdp_lineEdit, comboBox_niveau))
        result = cursor.fetchone()

        if result:
            # QMessageBox.information(fenetre, "Connexion réussie", f"Cliquez sur le bouton <span
            # style='font-weight:bold;color:#00018f;font-size:20px;'>OK</span> ci-dessous pour continuer !")

            # Fermez la fenêtre actuelle
            self.close()

            # Utilisez QTimer.singleShot pour retarder l'affichage de la deuxième fenêtre
            QTimer.singleShot(100, lambda: self.show_consultation_window())

        else:
            QMessageBox.warning(fenetre, "Échec de la connexion", "Identifiants incorrects, Réessayez encore !")

    def show_consultation_window(self):
        self.login_lineEdit = self.login_lineEdit.text()
        self.user_level = self.comboBox_niveau.currentText()[:-4]
        # Instanciez et affichez la deuxième fenêtre en utilisant la même instance d'QApplication
        self.consultation_window = ConsultationMain(self.parent())
        self.consultation_window.set_connected_user(self.login_lineEdit,
                                                    self.user_level)  # Passez l'information de l'utilisateur connecté
        self.consultation_window.show()

    def dash(self):
        pass

    def returnButtonPressed(self):
        pass

    # Our code geos here


def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()