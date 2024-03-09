"""
Software zur Ermittlung von Sensoren zur Einbettung in ein Carbonfaserverstärktes Strukturbauteil.
Dieses Hauptmodul enthält den Arbeitsablauf und das Userinterface.

Author: Philipp Haug
Date: 24.05.2023
Version: 4.1
"""
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Button, Label, Entry, filedialog, Frame, Canvas, Toplevel, colorchooser
import cv2
import numpy as np
import ezdxf
import time
import win32com.client
import Datenaufbereitung as DA
import os
import Method as M9

class LoadingScreen:
    """
    Definiert den Ladefensters und die zugehörigen Eingabe- und Ladefunktionen.
    """
    def __init__(self, master):
        """
        GUI Aufbau des Ladefensters.
        
        Args:
            master : Tkinter Master

        Returns:
        """
        self.master = master
        self.master.title("Loading Screen")

        self.lbl_anleitung = Label(self.master, text='Willkommen zur Automatischen Sensorermittlung. \n \n Bitte stellen sie sicher, dass die folgenden Dateien in dem ausgewählten Ordner abliegen: \n \n - …Contour.dxf   (Drawing-exchange der Bauteilkontur) \n - …Splines.dxf   (Drawing-exchange der gewünschten Faserverläufe) \n - …MaxPrincipal.csv   (Export der Zugspannung aus Siemens NX mit Element Koordinaten) \n - …MinPrincipal.csv   (Export der Druckspannungen aus Siemens NX) \n \n Tragen Sie nun die Länge, Höhe und Breite des Bauteils ein. Länge entspricht dabei der X-Achse und Höhe der Y-Achse der Bauteilgrundfläche. Breite ist die zu Extrudierende Höhe. \n \n Drücken sie anschließend auf „Load“.',
                                   wraplength=700,justify= tk.LEFT)
        self.lbl_anleitung.grid(row=0, column=0, columnspan=6, padx=10, pady=10)

        # Folder selection
        self.selected_folder = tk.StringVar()
        self.lbl_folder = Label(self.master, text="Select Folder:")
        self.lbl_folder.grid(row=1, column=0, padx=10, pady=5)
        self.entry_folder = Entry(self.master, textvariable=self.selected_folder, width=56)
        self.entry_folder.grid(row=1, column=1, columnspan=3, padx=10, pady=5)
        self.btn_browse = Button(self.master, text="Browse", command=self.browse_folder)
        self.btn_browse.grid(row=1, column=4, padx=10, pady=5)

        # Inputs for length, height, and width
        self.lbl_length = Label(self.master, text="Length:")
        self.lbl_length.grid(row=2, column=0, padx=10, pady=5)
        self.entry_length = Entry(self.master)
        self.entry_length.grid(row=2, column=1, padx=10, pady=5)

        self.lbl_height = Label(self.master, text="Height:")
        self.lbl_height.grid(row=2, column=2, padx=10, pady=5)
        self.entry_height = Entry(self.master)
        self.entry_height.grid(row=2, column=3, padx=10, pady=5)

        self.lbl_width = Label(self.master, text="Width:")
        self.lbl_width.grid(row=2, column=4, padx=10, pady=5)
        self.entry_width = Entry(self.master)
        self.entry_width.grid(row=2, column=5, padx=10, pady=5)

        # Load button
        self.btn_load = Button(self.master, text="Load", command=self.load_data)
        self.btn_load.grid(row=3, column=0, columnspan=6, padx=10, pady=10)

        self.master.protocol("WM_DELETE_WINDOW", self.close_window)

    def browse_folder(self):
        """
        Browser zur Auswahl des Arbeitsordners
        """
        path = filedialog.askdirectory()
        self.selected_folder.set(path)

    def load_data(self):
        """
        Funktionen des 'Load' Button.
        Einlesen der Dateipfade und zugehörige Dateien.
        Überprüfend der Dateien.
        Öffnen des nächsten Fensters.
        """

        global path
        path = self.selected_folder.get()
        length = int(self.entry_length.get())
        height = int(self.entry_height.get())
        global width
        width = int(self.entry_width.get())

        if not path or not length or not height or not width:
            # Highlight empty fields in red
            if not path:
                self.entry_folder.config(bg="red")
            if not length:
                self.entry_length.config(bg="red")
            if not height:
                self.entry_height.config(bg="red")
            if not width:
                self.entry_width.config(bg="red")
            tk.messagebox.showerror("Error", "Please fill in all fields.")
        else:
            self.entry_folder.config(bg="white")
            self.entry_length.config(bg="white")
            self.entry_height.config(bg="white")
            self.entry_width.config(bg="white")
            print("Folder path:", path)
            print("Length:", length)
            print("Height:", height)
            print("Width:", width)
            
            global nameContourdxf
            nameContourdxf = ''
            global nameSplinesdxf
            nameSplinesdxf = ''
            MinPrincipal = ''
            MaxPrincipal = ''

            for file_name in os.listdir(path):
                if file_name.endswith('Splines.dxf'):
                    nameSplinesdxf = os.path.join(path, file_name)
                if file_name.endswith('Contour.dxf'):
                    nameContourdxf = os.path.join(path, file_name)
                if file_name.endswith('MinPrincipal.csv'):
                    MinPrincipal = os.path.join(path, file_name)
                if file_name.endswith('MaxPrincipal.csv'):
                    MaxPrincipal = os.path.join(path, file_name)
        
            dateicheck = any([nameContourdxf == '', nameSplinesdxf == '',
                        MinPrincipal == '', MaxPrincipal == ''])
            
            if dateicheck:
                tk.messagebox.showerror('Error', 'Make sure all data is in the selected folder') 
            else:    
     
                WerteBildvorhanden, ModellBildvorhanden = False, False
                for file_name in os.listdir(path):
                    if file_name.endswith('Werte.png'):
                        WerteBildvorhanden = True
                    if file_name.endswith('Modell.png'):
                        ModellBildvorhanden = True
                
                if WerteBildvorhanden == False or ModellBildvorhanden == False:

                    DA.Aufbereitung(MinPrincipal, MaxPrincipal, path)


                ModellBild = cv2.imread(path +'/Modell.png')
                image = cv2.imread(path +'/Werte.png')
                cv2.imwrite(path + '/Werte_unedited.png', image)
                cv2.imwrite(path + '/Modell_unedited.png', ModellBild)

                lowerGrey = np.array([159,159,159], dtype="uint8") #Grey RGB (160,160,160)
                upperGrey = np.array([161,161,161], dtype="uint8")
                maskGrey = cv2.inRange(ModellBild, lowerGrey, upperGrey)
                contoursGrey, hierarchy = cv2.findContours(maskGrey, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                if len(contoursGrey) > 0:
                    grey_area = max(contoursGrey, key=cv2.contourArea)
                    global x 
                    global y
                    x, y, breite, hoehe = cv2.boundingRect(grey_area)
                    cv2.rectangle(image,(x, y),(x+breite, y+hoehe),(255, 0, 0), 2)

                global scaley
                scaley = hoehe / height
                global scalex
                scalex = breite / length
                global xC
                xC = x
                global yC
                yC = y + hoehe

                print('ScaleX', scalex)
                print('ScaleY', scaley)

                self.master.withdraw()
                global Sensoren
                Sensoren = M9.SensorErkennung(path, scalex, scaley)
                print(Sensoren)
                
                global Anzahl
                Anzahl = 1
                MaxAnzahl = len(Sensoren)

                image = M9.SensorMalen(image, Sensoren[-Anzahl,2], Sensoren[-Anzahl,3], Sensoren[-Anzahl,4], Sensoren[-Anzahl,5], Sensoren[-Anzahl,6], \
                                        Sensoren[-Anzahl,7], Sensoren[-Anzahl,8], Sensoren[-Anzahl,9])

                cv2.imwrite(path + '/Sensor1.png', image)

                global ToplevelMaster
                ToplevelMaster = Toplevel(self.master)
                SensorenAuswählen(ToplevelMaster, MaxAnzahl)

    def close_window(self):
        """
        Schließen des Fensters.
        """
        self.master.destroy()

    
def SensorMalenDXF(msp, x1 : int, y1 : int, x2 : int, y2 : int, Anschluss1x : int, Anschluss1y : int, Anschluss2x : int, Anschluss2y : int):
    """Zeichnet den Sensor in die auszugebende .dxf

    Args:
        msp : DXF-Modelspace in dem der Sensor platziert werden soll
        x1 (int) : X-Parameter von Sensorpunkt 1
        y1 (int) : Y-Parameter von Sensorpunkt 1
        x2 (int) : X-Parameter von Sensorpunkt 2
        y2 (int) : Y-Parameter von Sensorpunkt 2
        Anschluss1x (int) : X-Parameter von Anschluss 1
        Anschluss1y (int) : Y-Parameter von Anschluss 1
        Anschluss2x (int) : X-Parameter von Anschluss 2
        Anschluss2y (int) : Y-Parameter von Anschluss 2

    Returns:
    """
    #Sensor an sich
    y1dxf = (yC - y1) / scaley
    y2dxf = (yC - y2) / scaley
    x1dxf = (x1 - x) / scalex
    x2dxf = (x2 - x) / scalex

    msp.add_line((x1dxf, y1dxf), (x2dxf, y2dxf), dxfattribs={'layer': 'Sensor', "color": 1})

    #AnschlussStelle 1
    y1dxf = (yC - y1) / scaley
    y2dxf = (yC - Anschluss1y) / scaley
    x1dxf = (x1 - x) / scalex
    x2dxf = (Anschluss1x - x) / scalex

    msp.add_line((x1dxf, y1dxf), (x2dxf, y2dxf), dxfattribs={'layer': 'Sensor', "color": 1})

    #AnschlussStelle 2
    y1dxf = (yC - Anschluss2y) / scaley
    y2dxf = (yC - y2) / scaley
    x1dxf = (Anschluss2x - x) / scalex
    x2dxf = (x2 - x) / scalex

    msp.add_line((x1dxf, y1dxf), (x2dxf, y2dxf), dxfattribs={'layer': 'Sensor', "color": 1})


class SensorenAuswählen:
    """
    Definiert das Fenster zur Auswahl der Sensoren.
    """
    def __init__(self, master, MaxAnzahl :int):
        """
        GUI Aufbau des Sensorfensters.
        
        Args:
            master : Tkinter Master
            MaxAnzahl (int) : Maximale Anzahl an möglichen Sensoren

        Returns:
        """

        self.master = master
        self.master.title('Sensoren')

        # Load and display the image
        image_path = path + '/Sensor1.png'
        self.image = Image.open(image_path)
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_label = Label(self.master, image=self.image_tk)
        self.image_label.pack()

        #Frame für Button Anordnung
        self.btn_frame = Frame(self.master)
        self.btn_frame.pack(fill=tk.X)
        self.btn_frame.columnconfigure(0, weight=1)
        self.btn_frame.columnconfigure(1, weight=1)
        self.btn_frame.columnconfigure(2, weight=1)

        # Buttons for adding and removing sensors
        self.add_button = Button(self.btn_frame, text='+', command=lambda: self.handle_add_button(MaxAnzahl))
        self.add_button.grid(row= 0, column=0, sticky=tk.W+tk.E)
        self.sensor_label = Label(self.btn_frame, text='add Sensor')
        self.sensor_label.grid(row= 1, column=0, sticky=tk.W+tk.E)
        self.remove_button = Button(self.btn_frame, text='-', command= self.handle_remove_button)
        self.remove_button.grid(row= 2, column=0, sticky=tk.W+tk.E)

        # Buttons for editing and exporting
        self.edit_button = Button(self.btn_frame, text='Edit', command=self.Edit)
        self.edit_button.grid(row= 0, column=1, sticky=tk.W+tk.E)
        self.export_button = Button(self.btn_frame, text='Export', command=self.Export)
        self.export_button.grid(row= 1, column=1, sticky=tk.W+tk.E)

        self.AnleitungSensoren = Label(self.btn_frame, text='Anleitung zur Auswahl der Sensoren: \n \n Zugspannungen dargestellt in Orange.             Druckspannungen dargestellt in Lila. \n Die geplanten Sensoren sind in Schwarz dargestellt. \n Sollten die Spannungen oder das Modell nicht korrekt dargestellt sein, überprüfen Sie bitte die Daten und laden Sie diese erneut ein. \n \n Über die „+“ und „-“ Schaltflächen können Sensoren hinzugefügt oder entfernt werden. \n \n Mit Klick auf „Export“ werden die dargestellten Sensoren als .dxf exportiert und in NanoCAD geöffnet. \n \n Um die Modellkontur zur bearbeiten oder gesonderte Sensoren hinzuzufügen öffnen Sie bitte den Bearbeitungsmodus mit Klick auf „Edit“',
                           wraplength=1000, justify= tk.LEFT)
        self.AnleitungSensoren.grid(row= 0, column=2, rowspan=3, sticky=tk.W+tk.E)
        #self.text1.insert(END, 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.')

        self.master.protocol("WM_DELETE_WINDOW", self.close_window)

    def handle_add_button(self, MaxAnzahl : int):
        """
        Funktion des Buttons zum hinzufügen eines Sensors.
        Aufrufen der Funktion, die den Sensor ins Bild zeichnet. Aktualisierung des Bildes.
        
        Args:
            MaxAnzahl (int) : Maximale Anzahl an möglichen Sensoren

        Returns:
        """
        global Anzahl
        Anzahl += 1
        if Anzahl > MaxAnzahl:
            Anzahl -= 1
            print('Maximale Sensoranzahl=', MaxAnzahl)

        image = cv2.imread(path +'/Werte.png')
        AnzahlN = 1
        while AnzahlN <= Anzahl:
            image = M9.SensorMalen(image, Sensoren[-AnzahlN, 2], Sensoren[-AnzahlN, 3], Sensoren[-AnzahlN, 4], Sensoren[-AnzahlN, 5], Sensoren[-AnzahlN, 6], \
                            Sensoren[-AnzahlN, 7], Sensoren[-AnzahlN, 8], Sensoren[-AnzahlN, 9])
            AnzahlN += 1

        cv2.imwrite(path + '/crop_img.png', image)
        self.image = Image.open(path + '/crop_img.png')
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_label.configure(image=self.image_tk)

    def handle_remove_button(self):
        """
        Funktion des Buttons zum entfernen eines Sensors.
        Aufrufen der Funktion, die den Sensor ins Bild zeichnet. Aktualisierung des Bildes.
        """
        global Anzahl
        Anzahl -= 1
        if Anzahl < 1:
            Anzahl += 1
            print('Nicht weniger als 1 Sensor einbauen!')

        image = cv2.imread(path + '/Werte.png')
        AnzahlN = 1
        while AnzahlN <= Anzahl:
            image = M9.SensorMalen(image, Sensoren[-AnzahlN, 2], Sensoren[-AnzahlN, 3], Sensoren[-AnzahlN, 4], Sensoren[-AnzahlN, 5], Sensoren[-AnzahlN, 6], \
                            Sensoren[-AnzahlN, 7], Sensoren[-AnzahlN, 8], Sensoren[-AnzahlN, 9])
            AnzahlN += 1


        cv2.imwrite(path + '/crop_img.png', image)
        self.image = Image.open(path + '/crop_img.png')
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_label.configure(image=self.image_tk)

    def Edit(self):
        """
        Funktion des Buttons zum bearbeiten der Sensoren.
        Aufrufen des Bearbeitungsfensters.
        """
        self.master.withdraw()
        paintGui = Toplevel(self.master)
        PaintModellGUI(paintGui)


    def Export(self):
        """
        Funktion des Buttons zur exportierung der Sensoren.
        Erstellen mehrerer Schichten (Modellschicht, Modellschicht mit Faser, Sensorschicht)
        Speichern als DXF-File. Öffnen dieses DXF-Files in NanoCAD
        """
        global Sensoren

        NewNamedxf = nameContourdxf[:-11] + '_Sensors.dxf'

        doc = ezdxf.new('R2010')
        Contourdxf = ezdxf.readfile(nameContourdxf)
        Splinesdxf = ezdxf.readfile(nameSplinesdxf)

        # Create Start and finish Layer
        for entity in Contourdxf.modelspace():
            entity_copy = entity.copy()
            entity_copy.dxf.layer = 'OnlyContour'
            entity_copy.dxf.color = 7
            doc.modelspace().add_entity(entity_copy)

        # Contour + Fiber
        for entity in Splinesdxf.modelspace():
            entity_copy = entity.copy()
            entity_copy.dxf.layer = 'ContourAndFiber'
            entity_copy.dxf.color = 3
            doc.modelspace().add_entity(entity_copy)       
        for entity in Contourdxf.modelspace():
            entity_copy = entity.copy()
            entity_copy.dxf.layer = 'ContourAndFiber'
            entity_copy.dxf.color = 7
            doc.modelspace().add_entity(entity_copy)

        #Sensor Schicht
        for entity in Contourdxf.modelspace():
            entity_copy = entity.copy()
            entity_copy.dxf.layer = 'Sensor'
            entity_copy.dxf.color = 7
            doc.modelspace().add_entity(entity_copy)
        AnzahlN = 1
        while AnzahlN <= Anzahl:
            SensorMalenDXF(doc.modelspace(), Sensoren[-AnzahlN,2], Sensoren[-AnzahlN,3], Sensoren[-AnzahlN,4], Sensoren[-AnzahlN,5], Sensoren[-AnzahlN,6], \
                            Sensoren[-AnzahlN,7], Sensoren[-AnzahlN,8], Sensoren[-AnzahlN,9])
            AnzahlN += 1

        doc.saveas(NewNamedxf)

        time.sleep(2)
        self.master.withdraw()
        print('Erfolg')

        # Erstelle eine neue Instanz von NanoCAD
        try: 
            nano_app = win32com.client.Dispatch("nanocad.application")
        except:
            print('NanoCAD not found.')
            exit()
        else:
            doc = nano_app.Documents.Open(os.path.join(path, NewNamedxf))

            exit()

    def close_window(self):
        """
        Schließen des Fensters.
        """
        self.master.destroy()
        exit(0)


class PaintModellGUI():
    """
    Paint-Clone zur Bearbeitung der Modellgeometrie.
    """

    def __init__(self, master) -> None:
        """
        GUI Aufbau des Bearbeitungsfensters.
        
        Args:
            master : Tkinter Master

        Returns:
        """
        self.master = master

        self.image = Image.open(path + '/Modell.png')
        self.img = ImageTk.PhotoImage(file=path + '/Modell.png')
        self.img_clear = Image.open(path + '/Modell_unedited.png')

        self.master.title('Edit Modell')

        self.brush_width = 5
        self.current_color = '#000000'

        
        WIDTH, HEIGHT = self.image.size
        self.cnv = Canvas(self.master, width=WIDTH, height=HEIGHT, bg='white')
        self.cnv.pack()
        self.cnv.bind('<B1-Motion>', self.paint)


        self.cnv.create_image(0,0, anchor=tk.NW, image = self.img)

        self.draw = ImageDraw.Draw(self.image)

        self.btn_frame = Frame(self.master)
        self.btn_frame.pack(fill=tk.X)

        self.btn_frame.columnconfigure(0, weight=1)
        self.btn_frame.columnconfigure(1, weight=1)
        self.btn_frame.columnconfigure(2, weight=1)

        self.clear_btn = Button(self.btn_frame, text='Clear', command=self.clear)
        self.clear_btn.grid(row= 0, column=1, sticky=tk.W+tk.E)

        self.save_btn = Button(self.btn_frame, text='Save', command=self.save)
        self.save_btn.grid(row= 2, column=1, sticky=tk.W+tk.E)

        self.switch_btn = Button(self.btn_frame, text='Spannungen', command=self.spannungen)
        self.switch_btn.grid(row= 1, column=1, sticky=tk.W+tk.E)

        self.bplus_btn = Button(self.btn_frame, text='Brush +', command=self.brush_plus)
        self.bplus_btn.grid(row= 0, column=0, sticky=tk.W+tk.E)

        self.bminus_btn = Button(self.btn_frame, text='Brush -', command=self.brush_minus)
        self.bminus_btn.grid(row= 1, column=0, sticky=tk.W+tk.E)

        self.color_btn = Button(self.btn_frame, text='Change Color', command=self.change_color)
        self.color_btn.grid(row= 2, column=0, sticky=tk.W+tk.E)

        self.AnleitungEditModell = Label(self.btn_frame, text='Anleitung zur Bearbeitung des Modells: \n \n Über „B+“ und „B-“ kann die Pinselstärke verändert werden. \n Mit Klick auf „Change Color“ kann die Farbe des Pinsels angepasst werden. \n „Clear“ setzt das Bild auf Ursprungszustand zurück. \n Klick auf „Spannungen“ bringt Sie zum Bearbeitungsmodus für die Spannungen \n Über „Save“ werden die Änderungen gespeichert und Sie gelangen zurück zur Auswahl der Sensoren \n \n Zur Bearbeitung des Modells bitte die Farbe Grau RGB (160, 160, 160) oder Weiß RGB (255, 255, 255) über „Change Color“ auswählen. \n Mit der Farbe Rot RGB (255, 0, 0) können Bereiche markiert werden, an denen keine Sensoranschlussstelle gesetzt werden soll. \n \n Tipp: Der Bearbeitungsmodus für das Modell ist optimal um kleine Lücken im Modell zu schließen.',
                           wraplength=1000, justify= tk.LEFT)
        self.AnleitungEditModell.grid(row= 0, column=2, rowspan=3, sticky=tk.W+tk.E)

        self.master.protocol('WM_DELETE_WINDOW', self.on_closing)

    def spannungen(self):
        """
        Funktion des Buttons zum wechseln des Bearbeitungsmodus zum bearbeiten der Spannungen.
        Aufrufen des Paint-Clones zur Bearbeitung der Spannungen.
        """
        self.image.save(path + '/Modell.png')
        testmaster = Toplevel(self.master)
        self.master.withdraw()
        PaintWerteGUI(testmaster)

    def paint(self, event):
        """
        Funktion zum malen bei Mausklick

        Args:
            event : Mausposition im Bild

        Returns:
        """
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        self.cnv.create_rectangle(x1, y1, x2, y2, outline=self.current_color, fill= self.current_color, width=self.brush_width)
        self.draw.rectangle([x1, y1, x2 + self.brush_width, y2 + self.brush_width], outline=self.current_color, fill= self.current_color, width=self.brush_width)

    def clear(self):
        """
        Funktion des 'Clear'-Button: Zurücksetzen des Bildes auf Ausgangszustand.
        """
        self.cnv.delete('all')
        self.draw.rectangle([0,0,10000,10000], fill='white')
        self.cnv.create_image(0,0, anchor=tk.NW, image=self.img_clear)
        
    def save(self):
        """
        Funktion des 'Save'-Button: Speichern des Modellbildes.
        """
        self.image.save(path + '/Modell.png')
        self.on_closing()

    def brush_plus(self):
        """
        Funktion zur änderung der Pinselstärke. Vergößerung der Pinselstärke
        """
        if self.brush_width < 20:
            self.brush_width += 1

    def brush_minus(self):
        """
        Funktion zur änderung der Pinselstärke. Verkleinerung der Pinselstärke
        """
        if self.brush_width > 1:
            self.brush_width -= 1

    def change_color(self):
        """
        Funktion des 'Change Color'-Button: Aufrufen des ColorChooser von Tkinter zur Auswahl der Farbe.
        """
        _, self.current_color = colorchooser.askcolor(title = 'Choose A Color')

    def on_closing(self):
        """
        Funktion zum schließen des Fensters. Speichern des aktuellen Standes und öffnen des Auswahlmodus für die Sensoren.
        """
        self.master.withdraw()
        image = cv2.imread(path +'/Werte.png')
        global Sensoren
        Sensoren = M9.SensorErkennung(path, scalex, scaley)
        print(Sensoren)
                
        Anzahl = 1
        MaxAnzahl = len(Sensoren)

        image = M9.SensorMalen(image, Sensoren[-Anzahl,2], Sensoren[-Anzahl,3], Sensoren[-Anzahl,4], Sensoren[-Anzahl,5], Sensoren[-Anzahl,6], \
                                Sensoren[-Anzahl,7], Sensoren[-Anzahl,8], Sensoren[-Anzahl,9])
        
        cv2.imwrite(path + '/Sensor1.png', image)
        testmaster = Toplevel(self.master)
        SensorenAuswählen(testmaster, MaxAnzahl)


class PaintWerteGUI():
    """
    Paint-Clone zur Bearbeitung der Spannungen.
    """

    def __init__(self, master) -> None:
        """
        GUI Aufbau des Bearbeitungsfensters.
        
        Args:
            master : Tkinter Master

        Returns:
        """
        self.master = master
        self.image = Image.open(path + '/Werte.png')
        self.img = ImageTk.PhotoImage(file=path + '/Werte.png')
        self.img_clear = Image.open(path + '/Werte_unedited.png')

        self.master.title('Edit Spannungen')

        self.brush_width = 5
        self.current_color = '#000000'
  
        WIDTH, HEIGHT = self.image.size
        self.cnv = Canvas(self.master, width=WIDTH, height=HEIGHT, bg='white')
        self.cnv.pack()
        self.cnv.bind('<B1-Motion>', self.paint)

        self.cnv.create_image(0,0, anchor=tk.NW, image = self.img)

        self.draw = ImageDraw.Draw(self.image)

        self.btn_frame = Frame(self.master)
        self.btn_frame.pack(fill=tk.X)

        self.btn_frame.columnconfigure(0, weight=1)
        self.btn_frame.columnconfigure(1, weight=1)
        self.btn_frame.columnconfigure(2, weight=1)

        self.clear_btn = Button(self.btn_frame, text='Clear', command=self.clear)
        self.clear_btn.grid(row= 0, column=1, sticky=tk.W+tk.E)

        self.save_btn = Button(self.btn_frame, text='Save', command=self.save)
        self.save_btn.grid(row= 2, column=1, sticky=tk.W+tk.E)

        self.switch_btn = Button(self.btn_frame, text='Modell', command=self.modell)
        self.switch_btn.grid(row= 1, column=1, sticky=tk.W+tk.E)

        self.bplus_btn = Button(self.btn_frame, text='Brush +', command=self.brush_plus)
        self.bplus_btn.grid(row= 0, column=0, sticky=tk.W+tk.E)

        self.bminus_btn = Button(self.btn_frame, text='Brush -', command=self.brush_minus)
        self.bminus_btn.grid(row= 1, column=0, sticky=tk.W+tk.E)

        self.color_btn = Button(self.btn_frame, text='Change Color', command=self.change_color)
        self.color_btn.grid(row= 2, column=0, sticky=tk.W+tk.E)

        self.AnleitungEditWerte = Label(self.btn_frame, text='Anleitung zur Bearbeitung der Spannungen: \n \n Über „B+“ und „B-“ kann die Pinselstärke verändert werden. \n Mit Klick auf „Change Color“ kann die Farbe des Pinsels angepasst werden. \n „Clear“ setzt das Bild auf Ursprungszustand zurück. \n Klick auf „Modell“ bringt Sie zum Bearbeitungsmodus für das Modell \n Über „Save“ werden die Änderungen gespeichert und Sie gelangen zurück zur Auswahl der Sensoren \n \n Zur Bearbeitung der Zugspannungen bitte die Farbe Orange RGB (255, 165, 0), für die Druckspannungen Lila RGB (160, 32, 240) über „Change Color“ auswählen. \n Zum Entfernen von Spannungen bitte die Modellfarbe Grau RGB (160, 160, 160) auswählen \n \n Zum Hinzufügen von Sensoren ein Bereich mit entweder Orange oder Lila markieren. \n \n Achtung: Das Modell kann die im Bearbeitungsmodus Modell getätigten Änderungen noch nicht anzeigen. Diese Änderungen müssen nicht noch einmal getätigt werden.',
                           wraplength=1000, justify= tk.LEFT)
        self.AnleitungEditWerte.grid(row= 0, column=2, rowspan=3, sticky=tk.W+tk.E)

        self.master.protocol('WM_DELETE_WINDOW', self.on_closing)

    def modell(self):
        """
        Funktion des Buttons zum wechseln des Bearbeitungsmodus zum bearbeiten des Modells.
        Aufrufen des Paint-Clones zur Bearbeitung der Modellgeometrie.
        """
        self.image.save(path + '/Werte.png')
        testmaster = Toplevel(self.master)
        self.master.withdraw()
        PaintWerteGUI(testmaster)

    def paint(self, event):
        """
        Funktion zum malen bei Mausklick

        Args:
            event : Mausposition im Bild

        Returns:
        """
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        self.cnv.create_rectangle(x1, y1, x2, y2, outline=self.current_color, fill= self.current_color, width=self.brush_width)
        self.draw.rectangle([x1, y1, x2 + self.brush_width, y2 + self.brush_width], outline=self.current_color, fill= self.current_color, width=self.brush_width)

    def clear(self):
        """
        Funktion des 'Clear'-Button: Zurücksetzen des Bildes auf Ausgangszustand.
        """
        self.cnv.delete('all')
        self.draw.rectangle([0,0,10000,10000], fill='white')
        self.cnv.create_image(0,0, anchor=tk.NW, image=self.img_clear)
        
    def save(self): 
        """
        Funktion des 'Save'-Button: Speichern des Modellbildes.
        """
        self.image.save(path + '/Werte.png')
        self.on_closing()

    def brush_plus(self):
        """
        Funktion zur änderung der Pinselstärke. Vergößerung der Pinselstärke
        """
        if self.brush_width < 20:
            self.brush_width += 1

    def brush_minus(self):
        """
        Funktion zur änderung der Pinselstärke. Verkleinerung der Pinselstärke
        """
        if self.brush_width > 1:
            self.brush_width -= 1

    def change_color(self):
        """
        Funktion des 'Change Color'-Button: Aufrufen des ColorChooser von Tkinter zur Auswahl der Farbe.
        """
        _, self.current_color = colorchooser.askcolor(title = 'Choose A Color')

    def on_closing(self):
        """
        Funktion zum schließen des Fensters. Speichern des aktuellen Standes und öffnen des Auswahlmodus für die Sensoren.
        """
        self.master.withdraw()
        image = cv2.imread(path +'/Werte.png')
        global Sensoren
        Sensoren = M9.SensorErkennung(path, scalex, scaley)
        print(Sensoren)
                
        Anzahl = 1
        MaxAnzahl = len(Sensoren)

        image = M9.SensorMalen(image, Sensoren[-Anzahl,2], Sensoren[-Anzahl,3], Sensoren[-Anzahl,4], Sensoren[-Anzahl,5], Sensoren[-Anzahl,6], \
                                Sensoren[-Anzahl,7], Sensoren[-Anzahl,8], Sensoren[-Anzahl,9])
        
        cv2.imwrite(path + '/Sensor1.png', image)
        testmaster = Toplevel(self.master)
        SensorenAuswählen(testmaster, MaxAnzahl)


if __name__ == '__main__':
    root = Tk()
    app = LoadingScreen(root)
    root.mainloop()
