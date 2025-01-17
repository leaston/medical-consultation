# -*- coding: utf-8 -*-
"""
Created on Wed Dec 01 14:25:59 2023

@author: Dr Charles NKUNA
"""
import sys
import sqlite3
import re
from os import path

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QDateTimeEdit, QTableWidget, \
    QLabel, QMessageBox, QWidget, QLineEdit, QPushButton, QHBoxLayout, QRadioButton, QButtonGroup, QCheckBox, QComboBox, \
    QTextEdit, QSpinBox, QHeaderView, QVBoxLayout, QDialog, QTabWidget, QGridLayout
from PyQt5.QtGui import QRegExpValidator, QIntValidator, QColor
from PyQt5.QtCore import QRegExp, QDateTime, Qt, QTimer
from PyQt5 import QtWidgets
from PyQt5.uic import loadUiType

FORM_CLASS, _ = loadUiType(path.join(path.dirname('__file__'), "dashboard.ui"))

precedent = 0
suivant = 2


class Main(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        self.search_results = None

        # Création du QTabWidget
        self.tw_identity = QTabWidget(self)
        self.setCentralWidget(self.tw_identity)

        # Onglets
        self.create_tabs()
        self.create_saisie_diagnostic_tab()

        # Fixer la taille de la fenêtre (par exemple, 800x600)
        self.setFixedSize(1270, 730)
        self.setWindowTitle("Mes Consultations")
        # Centrer la fenêtre
        self.center_window()

        # Add input validation for QLineEdit
        self.add_input_validators()

        #################################

        self.setupUi(self)
        self.handle_buttons()

        # Aligner les noms de colonnes à gauche
        header = self.restitute_tbl.horizontalHeader()
        for col in range(self.restitute_tbl.columnCount()):
            header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Fixation de la largeur de chaque colonne
        # Liste des largeurs de colonnes
        column_widths = [30, 200, 150, 50, 50, 100, 60, 75, 250, 50, 50, 50, 50, 250, 250, 250, 120]

        # Ajustez la largeur des colonnes en fonction des valeurs de la liste
        self.resize_columns(column_widths)

        # self.radio_group = QButtonGroup(self)
        self.gender_group = QButtonGroup(self)

    def keyPressEvent(self, event):
        """Redéfinir keyPressEvent pour intercepter la touche Tab."""
        focused_widget = QApplication.focusWidget()

        # Vérifier si le widget actif est un QTextEdit
        if isinstance(focused_widget, QTextEdit) and event.key() == Qt.Key_Tab:
            if hasattr(focused_widget, 'next_widget') and focused_widget.next_widget:
                focused_widget.next_widget.setFocus()
            return  # Empêche le comportement par défaut de la touche Tab

        # Appeler la méthode parente pour les autres touches
        super().keyPressEvent(event)

    def handle_buttons(self):
        # Définissez une minuterie pour mettre à jour l'heure toutes les secondes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_current_time)
        self.timer.start(1000)  # Mettez à jour toutes les 1000 millisecondes (1 seconde)

        # Ajoutez un QTimer pour déclencher la recherche après un délai court
        self.search_timer = QTimer()
        self.search_timer.timeout.connect(self.search_data_in_table)
        self.search_timer.timeout.connect(self.search_data_in_row)

        # Connectez le signal textChanged à la fonction de recherche
        self.search_lineEdit.textChanged.connect(self.on_search_text_changed)
        self.search_lineEdit_2.textChanged.connect(self.search_data_in_widgets)
        self.add_btn.clicked.connect(self.add_data)
        self.add_btn_2.clicked.connect(self.add_data)

        self.del_btn.clicked.connect(self.delete_data)
        self.del_btn_2.clicked.connect(self.delete_data)

        # > self.erase_all_widgets_btn.clicked.connect(self.erase_all_widgets)
        self.erase_all_widgets_btn.clicked.connect(self.reset_all_fields)

        self.refresh_btn.clicked.connect(self.get_data)
        self.quit_btn.clicked.connect(self.close)

        self.edit_btn.clicked.connect(self.perform_update)
        self.edit_btn_2.clicked.connect(self.perform_update)

        # Connectez l'événement de clic de la table à votre fonction de gestion
        self.restitute_tbl.cellClicked.connect(self.show_popup_on_click)

        self.search_btn.clicked.connect(self.search_data_in_table)
        self.search_btn.setShortcut(Qt.Key_Return)
        self.search_btn_2.clicked.connect(self.search_data_in_table)
        self.search_btn_2.setShortcut(Qt.Key_Return)

        # Connect signals
        self.name_ledit.textChanged.connect(lambda: self.capitalize_lineedit(self.name_ledit))
        self.profession_ledit.textChanged.connect(lambda: self.capitalize_lineedit(self.profession_ledit))
        self.commune_ledit.textChanged.connect(lambda: self.capitalize_lineedit(self.commune_ledit))

        # Connect textChanged signal to capitalize function for QTextEdits
        self.diagnostic_textEdit.textChanged.connect(lambda: self.capitalize_sentences(self.diagnostic_textEdit))
        self.treatments_textEdit.textChanged.connect(lambda: self.capitalize_sentences(self.treatments_textEdit))
        self.observations_textEdit.textChanged.connect(lambda: self.capitalize_sentences(self.observations_textEdit))

        # self.diagnostic_textEdit.textChanged.connect(self.capitalize_sentences)
        # self.treatments_textEdit.textChanged.connect(self.capitalize_sentences)
        # self.observations_textEdit.textChanged.connect(self.capitalize_sentences)

        self.search_btn_2.clicked.connect(self.search_data)
        # self.search_btn_2.clicked.connect(self.toggle_labels_visibility)
        # self.search_lineEdit_2.textChanged.connect(self.toggle_labels_visibility)

        # Connecter le slot à l'événement de changement d'onglet
        self.tw_identity.currentChanged.connect(self.handle_tab_change)

        # =================================================
        #       LES 4 BOUTONS DE NAVIGATION
        # =================================================

        self.next_btn.clicked.connect(self.meth_next_row)
        self.previous_btn.clicked.connect(self.meth_previous_row)
        self.last_btn.clicked.connect(self.meth_last_row)
        self.first_btn.clicked.connect(self.meth_first_row)

        self.next_btn_2.clicked.connect(self.meth_next_row)
        self.previous_btn_2.clicked.connect(self.meth_previous_row)
        self.last_btn_2.clicked.connect(self.meth_last_row)
        self.first_btn_2.clicked.connect(self.meth_first_row)

        # =================================================
        #       FIN 4 BOUTONS DE NAVIGATION
        # =================================================

    def create_tabs(self):
        # Onglet Patient (Placeholder)
        self.patient_tab = QWidget()

        # Onglet Saisie Identité (Placeholder)
        self.tasaisie_identite_tab = QWidget()

        # Onglet Saisie Diagnostic
        self.saisie_diagnostic_tab = QWidget()
        self.create_saisie_diagnostic_tab()

        # Ajouter les onglets au QTabWidget
        self.tw_identity.addTab(self.patient_tab, "Patient")
        self.tw_identity.addTab(self.tasaisie_identite_tab, "Saisie Identité")
        self.tw_identity.addTab(self.saisie_diagnostic_tab, "Saisie Diagnostic")

    def create_saisie_diagnostic_tab(self):
        # Création d'un layout pour l'onglet "Saisie Diagnostic"
        grid_layout = QGridLayout()

        # Widgets pour la première colonne
        self.diagnostic_lbl = QLabel("Diagnostic")
        self.diagnostic_textEdit = QTextEdit()

        self.observations_lbl = QLabel("Observations")
        self.observations_textEdit = QTextEdit()

        # Widgets pour la deuxième colonne
        self.treatments_lbl = QLabel("Treatments")
        self.treatments_textEdit = QTextEdit()

        # Placement dans la grille
        grid_layout.addWidget(self.diagnostic_lbl, 0, 0)  # Première colonne, première ligne
        grid_layout.addWidget(self.diagnostic_textEdit, 1, 0)  # Première colonne, deuxième ligne
        grid_layout.addWidget(self.observations_lbl, 2, 0)  # Première colonne, troisième ligne
        grid_layout.addWidget(self.observations_textEdit, 3, 0)  # Première colonne, quatrième ligne

        grid_layout.addWidget(self.treatments_lbl, 0, 1)  # Deuxième colonne, première ligne
        grid_layout.addWidget(self.treatments_textEdit, 1, 1, 3, 1)  # Deuxième colonne, occupe trois lignes

        # Appliquer le layout à l'onglet
        self.saisie_diagnostic_tab.setLayout(grid_layout)

        # Configurer le focus pour gérer Tab entre les QTextEdit
        self.diagnostic_textEdit.next_widget = self.treatments_textEdit
        self.treatments_textEdit.next_widget = self.observations_textEdit
        self.observations_textEdit.next_widget = self.diagnostic_textEdit  # Boucle au premier QTextEdit

    def center_window(self):
        screen_geometry = QApplication.desktop().availableGeometry(self)
        window_geometry = self.frameGeometry()
        screen_center = screen_geometry.center()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

    def add_input_validators(self):
        """Add input validation for QLineEdit widgets."""
        # Example: Name QLineEdit
        self.name_ledit = QLineEdit(self)
        validator_text = QRegExpValidator(QRegExp(r"[a-zA-Z'-]+"), self)  # Letters, apostrophe, hyphen
        self.name_ledit.setValidator(validator_text)

    def capitalize_lineedit(self, line_edit):
        """Capitalize each word in a QLineEdit."""
        text = line_edit.text()
        if text and not text.endswith(' '):  # Ne pas capitaliser si l'espace est à la fin du texte
            capitalized_text = ' '.join([word.capitalize() for word in text.split()])
            line_edit.setText(capitalized_text)

    def capitalize_sentences(self, text_edit):
        """Capitalize the first letter of each sentence in a QTextEdit."""
        cursor = text_edit.textCursor()
        pos = cursor.position()

        # Get the current text
        text = text_edit.toPlainText()

        # Capitalize the first letter of each sentence
        capitalized_text = re.sub(r'([.!?]\s*|^)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)

        # Update the QTextEdit content only if there is a change
        if text != capitalized_text:
            text_edit.blockSignals(True)  # Block signals to avoid recursion
            text_edit.setPlainText(capitalized_text)
            text_edit.blockSignals(False)  # Unblock signals

            # Restore the cursor position
            cursor.setPosition(pos)
            text_edit.setTextCursor(cursor)

    def on_search_text_changed(self):
        # Réinitialisez le timer à chaque changement de texte
        self.search_timer.stop()
        self.search_timer.start(300)  # Démarrez le timer après 300 millisecondes

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

    def get_widget_value(self, widget):
        # Obtenir la valeur du widget en fonction de son type
        if isinstance(widget, (QLineEdit, QTextEdit)):
            return widget.text()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QDateTimeEdit):
            return widget.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        elif isinstance(widget, (QRadioButton, QCheckBox)):
            return widget.isChecked()
        else:
            return None  # Ajoutez d'autres cas au besoin

    def db_connection(self):
        self.db = sqlite3.connect("croixg.db")
        self.cursor = self.db.cursor()

    def set_connected_user(self, user_name, niveau_utilisateur):
        self.user_info = f"<strong>{user_name.upper()}</strong>  :  <em style='font-size: 14px;'>{niveau_utilisateur}</em>"
        # Affichez le nom de l'utilisateur connecté sur le label name_user_auth_lbl
        self.name_user_auth_lbl.setText(self.user_info)
        self.name_user_auth_lbl.setStyleSheet('''
                color: #00018f;
                font-size: 16px;
                font-family: Century Gothic;
                /*font-weight: bold;*/
                padding-left: 10px;  ''')

    def update_current_time(self):
        # Obtenez l'heure actuelle
        self.current_time = QDateTime.currentDateTime()

        # Définissez l'heure actuelle dans le QDateTimeEdit
        self.date_heure.setDateTime(self.current_time)

    def show_popup_on_click(self, row, column):
        # Récupérez les données de la ligne sélectionnée
        selected_row_data = [self.restitute_tbl.item(row, col).text() for col in
                             range(self.restitute_tbl.columnCount())]

        # Affichez un pop-up avec les détails de la ligne
        self.show_popup(selected_row_data)

    def get_data(self):

        # db = sqlite3.connect("croixg.db")
        # cursor = db.cursor()
        self.db_connection()

        command = ''' SELECT * FROM treatment_table'''

        result = self.cursor.execute(command)

        self.restitute_tbl.setRowCount(0)

        for row_number, row_data in enumerate(result):
            self.restitute_tbl.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.restitute_tbl.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def showEvent(self, event):
        super(Main, self).showEvent(event)
        self.search_lineEdit.setFocus()
        self.search_lineEdit_2.setFocus()

    def handle_tab_change(self, index):
        if index == 0:
            self.search_lineEdit.setFocus()

        if index == 1:
            self.search_lineEdit_2.setFocus()

    def search_data_in_table(self):
        self.db_connection()

        # search_name = self.search_lineEdit.text()
        search_text = self.search_lineEdit.text()

        # Exécutez la requête pour récupérer les données basées sur le nom query = "SELECT * FROM treatment_table
        # WHERE NomPrenoms LIKE ?" result = self.cursor.execute(query, ('%' + search_name + '%',)) Exécutez la
        # requête pour récupérer les données basées sur le nom ou la profession ou la commune ou le secteur ou le
        # numéro de téléphone
        query = """SELECT * FROM treatment_table 
               WHERE NomPrenoms LIKE ? OR 
                     Profession LIKE ? OR 
                     Commune LIKE ? OR 
                     Secteur LIKE ? OR 
                     Telephone LIKE ?"""

        result = self.cursor.execute(query, (
            '%' + search_text + '%',
            '%' + search_text + '%',
            '%' + search_text + '%',
            '%' + search_text + '%',
            '%' + search_text + '%'
        ))
        self.restitute_tbl.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.restitute_tbl.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.restitute_tbl.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        data = result.fetchone()

    def search_data_in_row(self):
        self.db_connection()

        # search_name = self.search_lineEdit.text()
        search_text = self.search_lineEdit_2.text()

        # Exécutez la requête pour récupérer les données basées sur le nom query = "SELECT * FROM treatment_table
        # WHERE NomPrenoms LIKE ?" result = self.cursor.execute(query, ('%' + search_name + '%',)) Exécutez la
        # requête pour récupérer les données basées sur le nom ou la profession ou la commune ou le secteur ou le
        # numéro de téléphone
        query = """SELECT * FROM treatment_table 
               WHERE NomPrenoms LIKE ? OR 
                     Profession LIKE ? OR 
                     Commune LIKE ? OR 
                     Secteur LIKE ? OR 
                     Telephone LIKE ?"""

        result = self.cursor.execute(query, (
            '%' + search_text + '%',
            '%' + search_text + '%',
            '%' + search_text + '%',
            '%' + search_text + '%',
            '%' + search_text + '%'
        ))

        self.search_results = result.fetchall()

        for row_number, row_data in enumerate(result):

            self.name_ledit.setText(str(row_data[1]))
            self.profession_ledit.setText(str(row_data[2]))

            # self.sexe = str(row_data[3])
            # if self.sexe == "Masculin":
            #     self.man_rbtn.setChecked(True)
            # elif self.sexe == "Féminin":
            #     self.woman_rbtn.setChecked(True)

            if str(row_data[3]) == "Masculin":
                self.man_rbtn.setChecked(True)
            if str(row_data[3]) == "Féminin":
                self.woman_rbtn.setChecked(True)

            self.age_spinBox.setValue(int(row_data[4]))
            self.commune_ledit.setText(str(row_data[5]))
            self.sector_spinBox.setValue(int(row_data[6]))
            self.phone_ledit.setText(str(row_data[7]))
            self.zone_comboBox.setCurrentText(str(row_data[8]))
            self.temp_ledit.setText(str(row_data[9]))
            self.tabd_ledit.setText(str(row_data[10]))
            self.tabg_ledit.setText(str(row_data[11]))
            self.bg_ledit.setText(str(row_data[12]))
            self.weight_ledit.setText(str(row_data[13]))
            self.diagnostic_textEdit.setPlainText(str(row_data[14]))
            self.treatments_textEdit.setPlainText(str(row_data[15]))
            self.observations_textEdit.setPlainText(str(row_data[16]))
            self.record_id = row_data[0]
            self.label_ID_Recup = row_data[0]
            self.label_ID_Recup_2 = row_data[0]
            # dateHeure = row_data[18]
            # self.lbl_date_heure = self.date_heure.setText(dateHeure)
            # data_hour = f"Date et heure dernière consultation {result[17]}"
            # self.lbl_date_heure.setText(f"Date et heure dernière consultation {data_hour}")

            self.erase_all_widgets()

    def erase_all_widgets(self):

        if self.search_results:
            row_data = self.search_results[0]
            # Boucle pour réinitialiser les widgets
            for widget in [self.name_ledit, self.profession_ledit, self.search_lineEdit, self.age_spinBox,
                           self.commune_ledit, self.sector_spinBox, self.phone_ledit, self.zone_comboBox,
                           self.temp_ledit, self.tabd_ledit, self.tabg_ledit, self.bg_ledit, self.weight_ledit,
                           self.diagnostic_textEdit, self.treatments_textEdit, self.observations_textEdit,
                           self.result_label, self.label_ID_Recup, self.label_ID_Recup_2, self.record_id,
                           self.record_id_2,
                           self.lbl_date_heure, self.search_lineEdit_2]:
                if isinstance(widget, QtWidgets.QLineEdit):
                    widget.clear()
                elif isinstance(widget, QtWidgets.QSpinBox):
                    widget.setValue(0)
                elif isinstance(widget, QtWidgets.QComboBox):
                    widget.setCurrentText("Choisir la distance du domicile en Km")
                elif isinstance(widget, QtWidgets.QTextEdit):
                    widget.clear()

            # print("Après réinitialisation :", self.name_ledit.text())

            # Modification de la visibilité des étiquettes après la réinitialisation des widgets
            for label in [self.label_ID_Enr, self.label_ID_Recup, self.label_ID_Recup_2, self.label_date_heure_recup,
                          self.lbl_date_heure,
                          self.result_label]:
                label.setVisible(not label.isVisible())

            # # Forcez la mise à jour de l'interface utilisateur
            # QApplication.processEvents()

    def search_data(self):
        self.db_connection()

        search_name = self.search_lineEdit_2.text()
        self.record_id = QLabel(self)
        self.record_id_2 = QLabel(self)
        # Initialisez self.cursor si ce n'est pas déjà fait
        if not hasattr(self, 'cursor') or self.cursor is None:
            self.cursor = self.db.cursor()

        # Exécutez la requête pour récupérer les données basées sur le nom
        query = "SELECT * FROM treatment_table WHERE NomPrenoms LIKE ?"
        result = self.cursor.execute(query, ('%' + search_name + '%',))
        data = result.fetchone()

        # Version sans LIKE, mais avecNomPrenoms=?. Son inconvénient est qu'il faut écrire le nom complet tel qu'il
        # se trouve dans la table dans la BDD query = "SELECT * FROM treatment_table WHERE NomPrenoms=?" result =
        # self.cursor.execute(query, (search_name,)) data = result.fetchone()

        if data:
            self.dateTimeEdit_recup = ""
            # Si le nom est trouvé, remplissez les autres widgets avec les informations correspondantes
            self.label_ID_Recup.setStyleSheet(
                'background-color: rgb(0, 1, 146); border: 1px solid rgb(0, 1, 146); color: rgb(186, 209, 248); font: '
                '12pt "Century Gothic";padding-left: 5px;')
            # 'border: 1px solid #00ff00; font: 10pt "Century Gothic"; color: rgb(0, 85, 0); background-color: rgb('
            # '255, 250, 187);')
            self.label_ID_Recup_2.setStyleSheet(
                'background-color: rgb(0, 1, 146); border: 1px solid rgb(0, 1, 146); color: rgb(186, 209, 248); font: '
                '12pt "Century Gothic";padding-left: 5px;')
            self.lbl_date_heure.setStyleSheet(
                'font-size: 9pt "Century Gothic"; color: rgb(255, 0, 0); background-color: #ffded7; padding: 10px 5px; '
                'border-radius: 5px; font-style: italic;')
            self.result_label.setStyleSheet(
                'color: transparent; background-color: transparent;')

            self.result_label.setText(f"{data[1]}")
            # Remplacez les lignes suivantes par le code pour remplir vos autres widgets
            # self.widget1.setText(str(data[1]))
            # self.widget2.setText(str(data[2]))
            # ...

            if self.record_id is not None:
                self.record_id.setText(str(data[0]))
                # print(f"1-IF-Type de record_id: {type(self.record_id)}")
            # else:
            #     print("Erreur : self.record_id n'est pas initialisé.")
                # print(f"2-ELSE-Type de record_id: {type(self.record_id)}")

            if self.record_id_2 is not None:
                self.record_id_2.setText(str(data[0]))
            #     print(f"1-IF-Type de record_id_2: {type(self.record_id_2)}")
            # else:
            #     print("Erreur : self.record_id_2 n'est pas initialisé.")
            #     print(f"2-ELSE-Type de record_id_2: {type(self.record_id_2)}")

            self.label_ID_Recup.setText(str(data[0]))
            self.label_ID_Recup_2.setText(str(data[0]))
            self.name_ledit.setText(str(data[1]))
            # print(self.name_ledit.setText(str(data[1])))
            self.profession_ledit.setText(str(data[2]))

            if str(data[3]) == "Masculin":
                self.man_rbtn.setChecked(True)
            if str(data[3]) == "Féminin":
                self.woman_rbtn.setChecked(True)

            self.age_spinBox.setValue(int(data[4]))
            self.commune_ledit.setText(str(data[5]))
            self.sector_spinBox.setValue(int(data[6]))
            self.phone_ledit.setText(str(data[7]))
            self.zone_comboBox.setCurrentText(str(data[8]))
            self.temp_ledit.setText(str(data[9]))
            self.tabd_ledit.setText(str(data[10]))
            self.tabg_ledit.setText(str(data[11]))
            self.bg_ledit.setText(str(data[12]))
            self.weight_ledit.setText(str(data[13]))
            self.diagnostic_textEdit.setPlainText(str(data[14]))
            self.treatments_textEdit.setPlainText(str(data[15]))
            self.observations_textEdit.setPlainText(str(data[16]))

            data_hour = f"{data[17]}"
            # print(data_hour)
            # print(f"Valeur de data[17]: {data[17]}")
            self.lbl_date_heure.setText(str(data_hour))

            # self.edit_btn.clicked.connect(self.perform_update)
            # self.edit_btn_2.clicked.connect(self.perform_update)

        else:
            # Si le nom n'est pas trouvé, affichez un message d'avertissement
            self.label_ID_Recup.setStyleSheet(
                'background - color: rgb(0, 1, 146); color: rgb(186, 209, 248); font: 75 16pt "Century Gothic"; '
                'padding - left: 5px;')
            # 'border: 1px solid #ff0000; font: 10pt "Century Gothic"; color: rgb(176, 0, 0); background-color: '
            # 'rgb(255, 228, 201);')
            self.label_ID_Recup_2.setStyleSheet(
                'background - color: rgb(0, 1, 146); color: rgb(186, 209, 248); font: 75 16pt "Century Gothic"; '
                'padding - left: 5px;')
            self.lbl_date_heure.setStyleSheet(
                'border: 1px solid #ff0000; font: 10pt "Century Gothic"; color: rgb(176, 0, 0); background-color: '
                'rgb(255, 228, 201);')
            self.result_label.setStyleSheet(
                'color: transparent; background-color: transparent;')

            self.result_label.setText(f"Nom non trouvé : {search_name}")

            # app = QApplication([])
            fenetre = QWidget()
            fenetre.setWindowTitle("Cabinet de Soins Médicaux LA CROIX GLORIEUSE")
            # fenetre()
            QMessageBox.warning(fenetre, "Nom non trouvé", f"Le nom '{search_name}' n'a pas été trouvé.")

    # def toggle_labels_visibility(self):
    #
    #     # Inversez l'état de visibilité des labels
    #     self.label_ID_Enr.setVisible(not self.label_ID_Enr.isVisible())
    #     self.label_ID_Recup.setVisible(not self.label_ID_Recup.isVisible())
    #     self.label_date_heure_recup.setVisible(not self.label_date_heure_recup.isVisible())
    #     self.lbl_date_heure.setVisible(not self.lbl_date_heure.isVisible())
    #     self.result_label.setVisible(not self.result_label.isVisible())

    # AUTRE METHODE avec au départ les labels visibles Inverser la visibilité des labels for label in [
    # self.label_ID_Enr, self.label_ID_Recup, self.label_date_heure_recup, self.lbl_date_heure,
    # self.result_label]: label.setVisible(label.isVisible()) if label.isVisible(): label.setVisible(False) else:
    # label.setVisible(True)

    def reset_all_fields(self):
        # Réinitialisez tous les champs à leurs valeurs par défaut ou vides
        self.name_ledit.clear()
        self.profession_ledit.clear()
        self.woman_rbtn.setChecked(True)  # On réinitialise avec la valeur par défaut

        self.search_lineEdit_2.clear()

        self.age_spinBox.setValue(0)
        self.commune_ledit.clear()
        self.sector_spinBox.setValue(0)
        self.phone_ledit.clear()

        index = self.zone_comboBox.findText("Choisir la distance du domicile en Km")
        if index != -1:
            self.zone_comboBox.setCurrentIndex(index)

        # self.zone_comboBox.setCurrentIndex("Choisir la distance du domicile en Km")
        self.temp_ledit.setText("0")
        self.tabd_ledit.setText("0")
        self.tabg_ledit.setText("0")
        self.bg_ledit.setText("0")
        self.weight_ledit.setText("0")
        self.diagnostic_textEdit.clear()
        self.treatments_textEdit.clear()
        self.observations_textEdit.clear()
        # self.date_heure.clear()
        # print(f"Type de self.record_id : {type(self.record_id)}")
        # print(f"Valeur de self.record_id : {self.record_id}")
        # > self.record_id.clear()
        # > self.record_id_2.clear()

        # Remettez le focus à search_lineEdit
        self.search_lineEdit.setFocus()
        self.search_lineEdit_2.setFocus()

        # Efface les labels si nécessaire
        self.label_ID_Recup.setText("0")
        self.label_ID_Recup_2.setText("0")
        # self.label_ID_Recup.clear()
        # self.label_ID_Recup_2.clear()
        self.lbl_date_heure.clear()
        self.lbl_date_heure.setStyleSheet(
            '''background-color: transparent;'''
        )
        self.attention_lbl.clear()
        self.attention_lbl.setStyleSheet(
            '''background-color: transparent;'''
        )
        self.attention_lbl_2.clear()
        self.attention_lbl_2.setStyleSheet(
            '''background-color: transparent;'''
        )

        # self.reset_all_fields()

    def resize_columns(self, column_widths):
        for col, width in enumerate(column_widths):
            self.restitute_tbl.setColumnWidth(col, width)

        self.restitute_tbl.setStyleSheet('''
            QTableWidget::item {
                background-color: rgb(222, 235, 247);
                color: black;
                border: 0.2px solid #00018f;
                padding: 1px;
            }
            align: left;
            color: #00018f; /*rgb(0,112,192);*/
            background-color: rgb(222, 235, 247);
        ''')

    def perform_update(self):
        # Exécuter la requête de mise à jour
        self.db_connection()

        # Récupérer les données modifiées depuis les widgets
        self.updated_name = self.name_ledit.text()
        self.updated_profession = self.profession_ledit.text()

        self.updated_sexe = "Féminin" if self.woman_rbtn.isChecked() else "Masculin"

        # Récupérer l'ID de l'enregistrement à mettre à jour
        self.record_id = int(self.label_ID_Recup.text())

        self.updated_age = str(self.age_spinBox.value())
        self.updated_commune = self.commune_ledit.text()
        self.updated_secteur = str(self.sector_spinBox.value())
        self.updated_phone = self.phone_ledit.text()
        self.updated_zone = self.zone_comboBox.currentText()
        self.updated_temp = self.temp_ledit.text()
        self.updated_tabd = self.tabd_ledit.text()
        self.updated_tabg = self.tabg_ledit.text()
        self.updated_bg = self.bg_ledit.text()
        self.updated_weight = self.weight_ledit.text()
        self.updated_diagnostic = self.diagnostic_textEdit.toPlainText()
        self.updated_treatements = self.treatments_textEdit.toPlainText()
        self.updated_observations = self.observations_textEdit.toPlainText()
        self.updated_date_heure = self.date_heure.text()

        print("Champs vérifiés :")
        for widget in [self.updated_name, self.updated_profession, self.updated_sexe, self.updated_age,
                       self.updated_commune, self.updated_secteur, self.updated_phone, self.updated_zone,
                       self.updated_temp, self.updated_tabd, self.updated_tabg, self.updated_bg, self.updated_weight,
                       self.updated_diagnostic, self.updated_treatements, self.updated_observations,
                       self.updated_date_heure]:
            print(f"{widget=}")

        # Vérifier si tous les champs requis sont remplis
        if all(value.strip() for value in
               [self.updated_name, self.updated_profession, self.updated_sexe, self.updated_age, self.updated_commune,
                self.updated_secteur, self.updated_phone, self.updated_zone, self.updated_temp, self.updated_tabd,
                self.updated_tabg, self.updated_bg, self.updated_weight, self.updated_diagnostic,
                self.updated_treatements, self.updated_observations, self.updated_date_heure]):
            # Tous les champs requis sont remplis, procéder à l'insertion
            row = (
                self.updated_name,
                self.updated_profession,
                self.updated_sexe,
                self.updated_age,
                self.updated_commune,
                self.updated_secteur,
                self.updated_phone,
                self.updated_zone,
                self.updated_temp,
                self.updated_tabd,
                self.updated_tabg,
                self.updated_bg,
                self.updated_weight,
                self.updated_diagnostic,
                self.updated_treatements,
                self.updated_observations,
                self.updated_date_heure,
                self.record_id
            )

            # Créer un tuple avec les données mises à jour
            update_query = '''UPDATE treatment_table SET NomPrenoms=?, Profession=?, Sexe=?, Age=?, Commune=?, 
            Secteur=?, Telephone=?, ZoneDeResidence=?, Tem=?, TABD=?, TABG=?, BG=?, Poids=?, Diagnostic=?, 
            Traitements=?, Observations=?, HeureDate=? WHERE ID=?'''

            self.res = self.cursor.execute(update_query, row)
            self.db.commit()

            # Afficher un message de succès ou faire d'autres actions nécessaires
            QMessageBox.information(self, "Mise à jour réussie", "Les données ont été mises à jour avec succès.")

            # Réinitialisez tous les champs après l'insertion
            self.reset_all_fields()
        else:
            print("Valeurs des champs :")
            for widget in [self.updated_name, self.updated_profession, self.updated_sexe, self.updated_age,
                           self.updated_commune, self.updated_secteur, self.updated_phone, self.updated_zone,
                           self.updated_temp, self.updated_tabd, self.updated_tabg, self.updated_bg,
                           self.updated_weight, self.updated_diagnostic, self.updated_treatements,
                           self.updated_observations, self.updated_date_heure]:
                print(f"{widget}: {widget}")
            # Afficher un message d'erreur si des champs requis sont vides
            QMessageBox.warning(self, "Champs vides", "Veuillez remplir tous les champs requis.")

    def add_data(self):

        self.db_connection()
        self.create_widgets()

        name = self.name_ledit.text().strip()
        profession = self.profession_ledit.text().strip()

        sexe = "Masculin" if self.man_rbtn.isChecked() else "Féminin"

        # =======================================================================
        #        FIN DE LA PARTIE A REVOIR
        # =======================================================================

        age = str(self.age_spinBox.value())
        commune = self.commune_ledit.text().strip()
        secteur = str(self.sector_spinBox.value())
        phone = self.phone_ledit.text().strip()
        zone = self.zone_comboBox.currentText()
        temp = self.temp_ledit.text().strip()
        tabd = self.tabd_ledit.text().strip()
        tabg = self.tabg_ledit.text().strip()
        bg = self.bg_ledit.text().strip()
        weight = self.weight_ledit.text().strip()
        diagnostic = self.diagnostic_textEdit.toPlainText().strip()
        treatments = self.treatments_textEdit.toPlainText().strip()
        observations = self.observations_textEdit.toPlainText().strip()
        date_heure = self.date_heure.text().strip()

        for k in [name, profession, sexe, age, commune, secteur, phone, zone, temp, tabd, tabg, bg, weight,
                  diagnostic, treatments, observations, date_heure]: print(k)

        # Vérifier si tous les champs requis sont remplis et ne sont pas des valeurs par défaut
        if all(value and value not in ["0", "Choisir la distance du domicile en Km"] for value in
               [name, profession, sexe, age, commune, secteur, phone, zone, temp, tabd, tabg, bg, weight, diagnostic,
                treatments, observations, date_heure]):
            # Tous les champs requis sont remplis, procéder à l'insertion
            row = (name, profession, sexe, age, commune, secteur, phone, zone, temp, tabd, tabg, bg, weight, diagnostic,
                   treatments, observations, date_heure)
            command = '''INSERT INTO treatment_table (NomPrenoms, Profession, Sexe, Age, Commune, Secteur, Telephone, 
            ZoneDeResidence, Tem, TABD, TABG, BG, Poids, Diagnostic, Traitements, Observations, HeureDate) VALUES(?,?,
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''

            self.res = self.cursor.execute(command, row)
            self.db.commit()

            # Message de confirmation
            self.message_box()

            # Réinitialisez tous les champs après l'insertion
            self.reset_all_fields()

            # Bascule vers l'onglet d'index 0
            if self.tw_identity.currentIndex() != 0:
                self.tw_identity.setCurrentIndex(0)
                print(f"Index actif: {self.tw_identity.currentIndex()}")

        else:
            # Afficher un message d'erreur si validation échoue
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Champs invalides")
            msg_box.setText("Veuillez remplir tous les champs requis avec des valeurs différentes de ceux par défaut.")
            msg_box.setInformativeText("Informations supplémentaires ici...")
            msg_box.exec_()

    def create_widgets(self):

        # Application du validateur pour autoriser uniquement les lettres, - et '
        # validator_text = QRegExpValidator(QRegExp(r"[a-zA-Z'-]+"), self)
        # validator_text = QRegExpValidator(QRegExp(r"[a-zA-Z'-]+"), self)  # Lettres, - et '' sont autorisés
        validator_number = QIntValidator(0, 999999, self)  # Exemple : Limite entre 0 et 999999
        validator_phone = QRegExpValidator(QRegExp(r"\+?\d+"), self)  # + facultatif, suivi de chiffres

        # Champ Mot de pass
        self.mdp_lineEdit = QLineEdit()
        self.mdp_lineEdit.setEchoMode(QLineEdit.Password)

        # Créez vos boutons radio
        self.woman_rbtn = QRadioButton("Féminin")
        self.man_rbtn = QRadioButton("Masculin")

        # Créez un groupe de boutons radio
        # self.gender_group = QButtonGroup(self)
        # self.gender_group.addButton(self.woman_rbtn)
        # self.gender_group.addButton(self.man_rbtn)

        # Créer le layout des boutons radios
        # self.horiz_lay_btnRadio = QHBoxLayout()

        # Ajoutez les boutons radio au layout
        # self.horiz_lay_btnRadio.addWidget(self.woman_rbtn)
        # self.horiz_lay_btnRadio.addWidget(self.man_rbtn)
        #
        # self.setLayout(self.horiz_lay_btnRadio)

        # Créer les autres widgets
        self.name_ledit_ = self.name_ledit.text()
        self.profession_ledit_ = self.profession_ledit.text()

        self.sexe_ = ""
        self.woman_rbtn_ = self.woman_rbtn.text()
        self.man_rbtn_ = self.man_rbtn.text()

        if self.woman_rbtn.isChecked():
            self.sexe_ = "Féminin"
        elif self.man_rbtn.isChecked():
            self.sexe_ = "Masculin"

        self.age_spinBox_ = str(self.age_spinBox.value())
        self.commune_ledit_ = self.commune_ledit.text()
        self.sector_spinBox_ = str(self.sector_spinBox.value())
        self.phone_ledit_ = self.phone_ledit.text()
        self.zone_comboBox_ = self.zone_comboBox.currentText()
        self.temp_ledit_ = self.temp_ledit.text()
        self.tabd_ledit_ = self.tabd_ledit.text()
        self.tabg_ledit_ = self.tabg_ledit.text()
        self.bg_ledit_ = self.bg_ledit.text()
        self.weight_ledit_ = self.weight_ledit.text()
        self.diagnostic_textEdit_ = self.diagnostic_textEdit.toPlainText()
        self.treatments_textEdit_ = self.treatments_textEdit.toPlainText()
        self.observations_textEdit_ = self.observations_textEdit.toPlainText()
        self.date_heure_ = self.date_heure.text()

        self.search_lineEdit_2_ = self.search_lineEdit_2.text()
        # self.search_lineEdit_2 = QLineEdit()
        self.search_btn_2 = QPushButton("Recherche")
        self.result_label = QLabel()

        self.lay_infos_recup = QHBoxLayout()
        self.lay_infos_recup.addWidget(self.label_ID_Enr)
        self.lay_infos_recup.addWidget(self.label_ID_Recup)
        self.lay_infos_recup.addWidget(self.label_date_heure_recup)
        self.lay_infos_recup.addWidget(self.lbl_date_heure)
        self.lay_infos_recup.addWidget(self.result_label)

        self.attention_lbl = QLabel()
        self.attention_lbl_2 = QLabel()
        self.tw_identity = QTabWidget()

        # self.age_spinBox = QSpinBox(self)
        # self.age_spinBox.setRange(0, 100)

    def delete_data(self):
        # Récupérer l'identifiant de l'enregistrement à supprimer
        identifiant = self.label_ID_Enr.text()

        # Afficher une boîte de dialogue de confirmation
        # app = QApplication([])
        fen = QWidget()
        fen.setWindowTitle("Cabinet de Soins Médicaux LA CROIX GLORIEUSE")
        confirm_dialog = QMessageBox.question(fen, 'Confirmation de suppression',
                                              'Voulez-vous vraiment supprimer cet enregistrement?',
                                              QMessageBox.Yes | QMessageBox.No)

        if confirm_dialog == QMessageBox.Yes:
            # Supprimer l'enregistrement de la base de données
            self.db_connection()

            command = ''' DELETE FROM treatment_table WHERE ID=? '''

            self.cursor.execute(command, (identifiant,))

            self.db.commit()

            # self.message_box()
            # Afficher un message de succès ou faire d'autres actions nécessaires
            # app = QApplication([])
            fen = QWidget()
            fen.setWindowTitle("Cabinet de Soins Médicaux LA CROIX GLORIEUSE")
            QMessageBox.information(fen, "Suppression réussie", "L'enregistrement a bien été supprimé avec succès.")

            self.search_lineEdit_2.clear()

            # Réinitialiser les champs après la suppression
            self.erase_all_widgets()
            self.reset_all_fields()
        else:
            self.erase_all_widgets()
            self.reset_all_fields()

    def search_data_in_widgets(self):
        search_text = self.search_lineEdit_2.text().strip()

        # Vérifiez si le champ de recherche est vide
        if not search_text:
            self.clear_widgets()  # Méthode pour réinitialiser les widgets
            return

        # Requête SQL pour rechercher un enregistrement correspondant
        self.db_connection()
        query = """SELECT * FROM treatment_table 
                   WHERE NomPrenoms LIKE ? OR 
                         Profession LIKE ? OR 
                         Commune LIKE ? OR 
                         Secteur LIKE ? OR 
                         Telephone LIKE ?"""
        result = self.cursor.execute(query, (
            '%' + search_text + '%',
            '%' + search_text + '%',
            '%' + search_text + '%',
            '%' + search_text + '%',
            '%' + search_text + '%'
        )).fetchone()

        # Si un résultat est trouvé, remplissez les widgets
        if result:
            self.record_id = self.label_ID_Enr.setText(str(result[0]))
            self.record_id_2 = self.label_ID_Enr.setText(str(result[0]))
            self.label_ID_Recup.setText(str(result[0]))
            self.label_ID_Recup_2.setText(str(result[0]))

            self.name_ledit.setText(result[1])
            self.profession_ledit.setText(result[2])

            if result[3] == "Masculin":
                self.man_rbtn.setChecked(True)
            elif result[3] == "Féminin":
                self.woman_rbtn.setChecked(True)

            self.age_spinBox.setValue(int(result[4]))
            self.commune_ledit.setText(result[5])
            self.sector_spinBox.setValue(int(result[6]))
            self.phone_ledit.setText(str(result[7]))
            self.zone_comboBox.setCurrentText(result[8])

            self.temp_ledit.setText(str(result[9]))
            self.tabd_ledit.setText(str(result[10]))
            self.tabg_ledit.setText(str(result[11]))
            self.bg_ledit.setText(str(result[12]))
            self.weight_ledit.setText(str(result[13]))
            self.diagnostic_textEdit.setPlainText(str(result[14]))
            self.treatments_textEdit.setPlainText(str(result[15]))
            self.observations_textEdit.setPlainText(str(result[16]))

            data_hour = f"{result[17]}"
            # print(data_hour)
            # print(f"Valeur de data[17]: {data[17]}")
            self.lbl_date_heure.setText(f"{data_hour}")
        else:
            # Si aucun résultat, réinitialisez les widgets
            self.clear_widgets()

    def clear_widgets(self):
        """Réinitialise tous les widgets liés aux données"""
        self.label_ID_Recup.clear()
        self.label_ID_Recup_2.clear()
        self.name_ledit.clear()
        self.profession_ledit.clear()
        self.man_rbtn.setChecked(False)
        self.woman_rbtn.setChecked(False)
        self.age_spinBox.setValue(0)
        self.commune_ledit.clear()
        self.sector_spinBox.setValue(0)
        self.phone_ledit.clear()
        self.zone_comboBox.setCurrentIndex(0)  # Si "Choisir une option" est l'index 0

    def message_box(self):
        fenetre = QWidget()
        fenetre.setWindowTitle("Cabinet de Soins Médicaux LA CROIX GLORIEUSE")

        # Vérifiez si self.res existe et est valide avant d'appeler rowcount
        if self.res and self.cursor.rowcount > 0:
            QMessageBox.information(fenetre, f"Opération réussie", f"Opération effectuée avec succes.")
            # self.db.commit()
        else:
            QMessageBox.warning(fenetre, "Échec de l'opération", "Réessayez après quelques minutes !")

    # ========================================================

    #         DEBUT BOUTON DE NAVIGATION
    # ========================================================

    def config_navigation(self):
        self.db_connection()

        command = ''' SELECT ID FROM treatment_table '''
        self.result = self.cursor.execute(command)
        self.val = self.result.fetchall()

    def meth_next_row(self):
        self.config_navigation()
        self.tot = len(self.val)
        global precedent
        global suivant

        precedent = precedent + 1
        if precedent < self.tot:
            suivant = self.val[precedent][0]
            self.navigate()
            self.update_attention_label()
        else:
            precedent = self.tot - 1
            # print("End of file")

    def meth_previous_row(self):
        self.config_navigation()
        global precedent
        global suivant
        precedent = precedent - 1
        if precedent > -1:
            suivant = self.val[precedent][0]
            self.navigate()
            self.update_attention_label()
        else:
            precedent = 0
            # print("Begin of file")

    def meth_last_row(self):
        self.config_navigation()
        self.tot = len(self.val)
        global precedent
        global suivant

        precedent = self.tot - 1
        if precedent < self.tot:
            suivant = self.val[precedent][0]
            self.navigate()
            self.update_attention_label()
        else:
            precedent = self.tot - 1
            # print("End of file")

    def meth_first_row(self):
        self.config_navigation()
        # self.db = sqlite3.connect("croixg.db")

        # self.cursor = self.db.cursor()

        # command = ''' SELECT ID FROM treatment_table '''

        # self.result = self.cursor.execute(command)
        # self.val = self.result.fetchall()

        global precedent
        global suivant
        precedent = 0

        if precedent > -1:
            suivant = self.val[precedent][0]
            self.navigate()
            self.update_attention_label()
        else:
            precedent = 0
            # suivant = self.val[precedent][0] if self.val else 0  # Ajout d'une condition pour éviter une erreur si
            # self.val est vide print("Begin of file")

    def update_attention_label(self):
        # Mettez à jour le label en fonction de la position actuelle
        if precedent == 0:
            self.attention_lbl.setText("Premier élément de la table atteint")
            self.attention_lbl_2.setText("Premier élément de la table atteint")
            self.attention_lbl.setStyleSheet(
                'font-size: 9pt "Century Gothic"; color: rgb(255, 0, 0); background-color: #ffded7; padding: 10px 5px; '
                'border-radius: 5px; font-style: italic;')
            self.attention_lbl_2.setStyleSheet(
                'font-size: 9pt "Century Gothic"; color: rgb(255, 0, 0); background-color: #ffded7; padding: 10px 5px; '
                'border-radius: 5px; font-style: italic;')
            # print("Premier élément de la table atteint")

        elif precedent == self.tot - 1:
            self.attention_lbl.setText("Dernier élément de la table atteint")
            self.attention_lbl_2.setText("Dernier élément de la table atteint")
            self.attention_lbl.setStyleSheet(
                'font-size: 9pt "Century Gothic"; color: rgb(255, 0, 0); background-color: #ffded7; padding: 10px 5px; '
                'border-radius: 5px; font-style: italic;')
            self.attention_lbl_2.setStyleSheet(
                'font-size: 9pt "Century Gothic"; color: rgb(255, 0, 0); background-color: #ffded7; padding: 10px 5px; '
                'border-radius: 5px; font-style: italic;')
            # print("Dernier élément de la table atteint")
        else:
            self.attention_lbl.clear()
            self.attention_lbl.setStyleSheet('background-color: transparent;')
            self.attention_lbl_2.clear()
            self.attention_lbl_2.setStyleSheet('background-color: transparent;')

    # ========================================================
    #         FIN BOUTON DE NAVIGATION
    # ========================================================

    def navigate(self):
        global suivant
        self.db_connection()

        command = ''' SELECT * FROM treatment_table WHERE ID=? '''

        self.result = self.cursor.execute(command, [suivant])
        val = self.result.fetchone()
        # print(val) # Juste pour le débogage
        self.label_ID_Recup.setText(str(val[0]))
        self.label_ID_Recup_2.setText(str(val[0]))
        self.name_ledit.setText(str(val[1]))
        self.profession_ledit.setText(str(val[2]))

        if str(val[3]) == "Masculin":
            self.man_rbtn.setChecked(True)
        elif str(val[3]) == "Féminin":
            self.woman_rbtn.setChecked(True)

        self.age_spinBox.setValue(int(val[4]))
        self.commune_ledit.setText(str(val[5]))
        self.sector_spinBox.setValue(int(val[6]))
        self.phone_ledit.setText(str(val[7]))
        self.zone_comboBox.setCurrentText(str(val[8]))
        self.temp_ledit.setText(str(val[9]))
        self.tabd_ledit.setText(str(val[10]))
        self.tabg_ledit.setText(str(val[11]))
        self.bg_ledit.setText(str(val[12]))
        self.weight_ledit.setText(str(val[13]))
        self.diagnostic_textEdit.setPlainText(str(val[14]))
        self.treatments_textEdit.setPlainText(str(val[15]))
        self.observations_textEdit.setPlainText(str(val[16]))

        val_hour = f"{val[17]}"
        # print(val_hour) # Juste pour le débogage

        self.lbl_date_heure.setText(f"Date et heure de la dernière consultation : {val_hour}")
        self.lbl_date_heure.setStyleSheet(
            'font-size: 9pt "Century Gothic"; color: rgb(255, 0, 0); background-color: #ffded7; padding: 10px 5px; '
            'border-radius: 5px; font-style: italic;')
        # print(v_h)

        # self.date_heure.setText(str(val[17]))

        # self.date_heure.setDateTime(QDateTime.fromString(str(val[17]), "dd-MM-yyyy HH:mm:ss"))

        # self.meth_first_row()
        # self.navigate()

    def populate_table(self, result):
        self.restitute_tbl.setRowCount(len(result))
        self.num_columns = len(result[0]) if result else 0

        for row, data in enumerate(result):
            for col in range(self.num_columns):
                self.restitute_tbl.setItem(row, col, QTableWidgetItem(str(data[col])))

    def show_popup(self, data):
        popup_dialog = QDialog()
        popup_dialog.setWindowTitle("Détails de la ligne")

        popup_dialog.resize(250, 125)

        # Ajoutez une table à la disposition du popup
        table_popup = QTableWidget()
        table_popup.setColumnCount(2)
        table_popup.setRowCount(len(data))

        # Aligner les noms de colonnes à gauche
        header = table_popup.horizontalHeader()
        header.setStyleSheet('font-weight: bold;')

        for col in range(table_popup.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        # Aligner les noms des en-têtes à gauche
        header = table_popup.horizontalHeader()
        header.setStyleSheet('font-weight: bold; alignment')

        for col in range(table_popup.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

        # Définir les noms et la largeur des colonnes
        table_popup.setHorizontalHeaderLabels(["REFERENCES", "VALEURS"])

        # Définir la taille fixe du popup
        popup_dialog.setFixedSize(500, 475)

        table_popup.setColumnCount(2)
        table_popup.setRowCount(len(data))

        # Aligner les noms des en-têtes à gauche
        header = table_popup.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        table_popup.setColumnWidth(0, 125)  # 1ère colonne avec une largeur de 100px
        table_popup.setColumnWidth(1, 325)  # 2è colonne avec une largeur de 350px

        # Couleurs d'arrière-plan alternées
        color1 = QColor("#E6E6E6")  # Couleur 1
        color2 = QColor("#FFFFFF")  # Couleur 2

        def apply_alternate_colors():
            for row in range(table_popup.rowCount()):
                for col in range(table_popup.columnCount()):
                    item = table_popup.item(row, col)
                    if item:
                        item.setBackground(color1 if row % 2 == 0 else color2)

        # Parcourez les données et remplissez la table
        for row, (label, value) in enumerate(
                zip(['ID:', 'Nom Prenoms:', 'Profession:', 'Sexe:', 'Age', 'Commune', 'Secteur', 'Telephone',
                     'Zone De Residence', 'Température', 'TABD', 'TABG', 'BG', 'Poids', 'Diagnostic', 'Traitements',
                     'Observations', 'DateHeure'], data)):
            item_label = QTableWidgetItem(f"{label}")
            item_value = QTableWidgetItem(f"{value}")

            # Alternez les couleurs d'arrière-plan
            if row % 2 == 0:
                item_label.setBackground(color1)
                item_value.setBackground(color1)
            else:
                item_label.setBackground(color2)
                item_value.setBackground(color2)

            table_popup.setItem(row, 0, item_label)
            table_popup.setItem(row, 1, item_value)

            # Ajustez automatiquement la hauteur de la ligne en fonction du contenu
            table_popup.resizeRowToContents(row)

        # Ajoutez une bordure de couleur à la table
        table_popup.setStyleSheet("QTableWidget{border: 1px solid #CCCCCC;}")

        # Ajustez la largeur des colonnes en fonction des valeurs de la liste
        column_widths = [50, 200]
        self.resize_columns(column_widths)

        layout = QVBoxLayout()
        layout.addWidget(table_popup)

        apply_alternate_colors()

        # Ajouter les boutons de navigation et de fermeture
        prev_button = QPushButton("←")
        next_button = QPushButton("→")
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(popup_dialog.close)

        # Ajouter la logique de navigation
        def navigate(direction):
            current_row = self.restitute_tbl.currentRow()
            if direction == "prev" and current_row > 0:
                self.restitute_tbl.selectRow(current_row - 1)
            elif direction == "next" and current_row < self.restitute_tbl.rowCount() - 1:
                self.restitute_tbl.selectRow(current_row + 1)

            # Mettez à jour les données affichées dans le popup
            new_data = [
                self.restitute_tbl.item(self.restitute_tbl.currentRow(), col).text()
                if self.restitute_tbl.item(self.restitute_tbl.currentRow(), col) else ""
                for col in range(self.restitute_tbl.columnCount())
            ]
            for row, value in enumerate(new_data):
                table_popup.setItem(row, 1, QTableWidgetItem(value))

            apply_alternate_colors()

        prev_button.clicked.connect(lambda: navigate("prev"))
        next_button.clicked.connect(lambda: navigate("next"))
        close_button.clicked.connect(popup_dialog.close)

        # Créer une disposition horizontale pour les flèches et le bouton de fermeture
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(close_button)
        nav_layout.addStretch()
        nav_layout.addWidget(next_button)

        # Créer la disposition
        layout = QVBoxLayout()
        layout.addWidget(table_popup)
        layout.addLayout(nav_layout)
        # layout.addWidget(close_button)  # Ajouter le bouton de fermeture à la disposition

        popup_dialog.setLayout(layout)

        popup_dialog.exec_()
