from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QHeaderView, QDialog, QMessageBox, QAbstractItemView
from database import Database
import sys
import os
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader


class VentanaProductos(QDialog):
    product_added = Signal() 
    
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        interface_path = os.path.join(os.path.dirname(__file__), "interfaz.ui")
        self.ui = loader.load(interface_path, None)
        self.db = Database()

        self.ui.tableWidget.setColumnHidden(0, True)
        self.ui.btnEliminar.setVisible(False)
        self.load_products()

        self.ui.btnAfegir.clicked.connect(self.add_product)
        self.ui.btnModificar.clicked.connect(self.update_product)

        self.ui.show()

    def load_products(self):
        self.ui.tableWidget.setRowCount(0)
        products = self.db.get_products()
        for row_index, product in enumerate(products):
            self.ui.tableWidget.insertRow(row_index)
            for col_index, data in enumerate(product):
                self.ui.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(data)))

    def add_product(self):
        nom = self.ui.txtNom.text()
        preu = self.ui.txtPreu.text()
        categoria = self.ui.txtCategoria.text()

        if nom and preu and categoria:
            self.db.add_product(nom, float(preu), categoria)
            self.load_products()
            self.product_added.emit() 
            self.clear_inputs()
        else:
            QMessageBox.warning(self, "Error", "Tots els camps són obligatoris")

    def update_product(self):
        selected_row = self.ui.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Selecciona un producte per modificar")
            return

        product_id = int(self.ui.tableWidget.item(selected_row, 0).text())
        nom = self.ui.txtNom.text()
        preu = self.ui.txtPreu.text()
        categoria = self.ui.txtCategoria.text()

        if nom and preu and categoria:
            boton_pulsado = QMessageBox.question(
            self,
            "Estas segur?",
            "Quieres confirmar los cambios?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No
        )
            if boton_pulsado==QMessageBox.Yes:
                self.db.update_product(product_id, nom, float(preu), categoria)
                self.load_products()
                self.product_added.emit()  
                self.clear_inputs()
            elif boton_pulsado==QMessageBox.No:
                self.clear_inputs()
        else:
            QMessageBox.warning(self, "Error", "Tots els camps són obligatoris")

    def clear_inputs(self):
        self.ui.txtNom.clear()
        self.ui.txtPreu.clear()
        self.ui.txtCategoria.clear()


class ProductApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        interface_path = os.path.join(os.path.dirname(__file__), "interfaz.ui")
        self.ui = loader.load(interface_path, None)
        self.db = Database()
        self.ventanaproductos=None

        barra_menus = self.menuBar()
        menu = barra_menus.addMenu("&Menu")
        self.accion = QAction("&Gestionar Productes", self)
        self.accion.setShortcut(QKeySequence("Ctrl+G"))
        menu.addAction(self.accion)
        self.ui.verticalLayout.insertWidget(0,barra_menus)
        self.ui.tableWidget.setColumnHidden(0, True)
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.load_products()

        self.ui.btnAfegir.setVisible(False)
        self.ui.btnModificar.setVisible(False)
        self.ui.txtNom.setVisible(False)
        self.ui.labelNom.setVisible(False)
        self.ui.txtPreu.setVisible(False)
        self.ui.labelPreu.setVisible(False)
        self.ui.txtCategoria.setVisible(False)
        self.ui.labelCategoria.setVisible(False)

        self.ui.btnEliminar.clicked.connect(self.delete_product)
        self.ui.tableWidget.itemSelectionChanged.connect(self.load_selected_product)
        self.accion.triggered.connect(self.afegir_menu)

        self.ui.show()
    def load_products(self):
        self.ui.tableWidget.setRowCount(0)
        products = self.db.get_products()

        for row_index, product in enumerate(products):
            self.ui.tableWidget.insertRow(row_index)
            for col_index, data in enumerate(product):
                self.ui.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(data)))

    
    def delete_product(self):
        selected_row = self.ui.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Selecciona un producte per eliminar")
            return

        product_id = int(self.ui.tableWidget.item(selected_row, 0).text())
        
        boton_pulsado = QMessageBox.question(
        self,
        "Estas segur?",
        "Seguro que quieres eliminar?",
        buttons=QMessageBox.Yes | QMessageBox.No,
        defaultButton=QMessageBox.No
        )
        if boton_pulsado==QMessageBox.Yes:
            self.db.delete_product(product_id)
            self.load_products()


    def afegir_menu(self):
        if self.ventanaproductos is None:
            self.ventanaproductos=VentanaProductos()
            self.ventanaproductos.product_added.connect(self.load_products) 
            self.ventanaproductos.move(self.pos())

    def load_selected_product(self):
        selected_row = self.ui.tableWidget.currentRow()
        if selected_row != -1:
            self.ui.txtNom.setText(self.ui.tableWidget.item(selected_row, 1).text())
            self.ui.txtPreu.setText(self.ui.tableWidget.item(selected_row, 2).text())
            self.ui.txtCantidad.setText(self.ui.tableWidget.item(selected_row, 3).text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductApp()
    sys.exit(app.exec())

