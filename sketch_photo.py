#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Gdk
import os
import cv2

class SketchPhoto(object):
    def __init__(self):
        sinais = {
            "on_btnAbrir_clicked":self.open_image,
            "on_btnFechar_clicked":self.sair,
            "on_mainwindow_destroy":self.sair,
            "on_btnConvert_clicked":self.on_btnConvert_clicked,
            "on_btnSalvar_clicked":self.save_image,
        }
        
        self.path = os.getcwd()
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file("mainwindow.glade")

        self.main_window = self.builder.get_object("mainwindow")

        self.image1 = self.builder.get_object("image1")
        self.btnConvert = self.builder.get_object("btnConvert")
        self.btnSalvar = self.builder.get_object("btnSalvar")

        self.spin1 = self.builder.get_object("spin1")
        self.spin2 = self.builder.get_object("spin2")
        self.spin3 = self.builder.get_object("spin3")
        
        self.adjust1 = self.builder.get_object("adjust1")
        self.adjust2 = self.builder.get_object("adjust2")
        self.adjust3 = self.builder.get_object("adjust3")
        
        self.value1 = int(self.spin1.get_value())
        self.value2 = int(self.spin2.get_value())
        self.value3 = int(self.spin3.get_value())
        
        self.spin1.connect("value-changed", self.spin1_value_changed)
        self.spin2.connect("value-changed", self.spin2_value_changed)
        self.spin3.connect("value-changed", self.spin3_value_changed)
        
        self.builder.connect_signals(sinais)

        screen = Gdk.Screen.get_default()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('style.css')

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.main_window.show()

    def sair(self, widget):
        Gtk.main_quit()

    def open_image(self, widget):
        self.adjust1.set_value(500)
        self.adjust2.set_value(500)
        self.adjust3.set_value(255)

        dialog = Gtk.FileChooserDialog(title="Abrir Arquivo", parent=self.main_window, action=Gtk.FileChooserAction.OPEN)

        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        
        self.add_filters(dialog)

        dialog.set_local_only(False)
        dialog.set_current_folder(self.path)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.filename = dialog.get_filename()
            self.path = dialog.get_current_folder()

            title = self.filename.split('/')
            title.reverse()
            self.main_window.set_title('Pencil Sketch - ' + title[0])
            
            self.img = cv2.imread(self.filename)
            self.img = cv2.cvtColor(self.img,cv2.COLOR_BGR2RGB)

            h, w, d = self.img.shape
            scale = w/h
            
            if w < h:
                w = 576
                h = 1024
            
            if w > 1024:
                w= 1024
                h = 576
            
            dim = (w, h)
            
            self.resized = cv2.resize(self.img, dim, interpolation = cv2.INTER_AREA)

            dialog.destroy()

            self.show_image(self.resized)

            self.btnConvert.set_sensitive(True)
            
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    def add_filters(self, dialog):
        filter_image = Gtk.FileFilter()
        
        filter_image.set_name("Todos Arquivos de Imagem")
        filter_image.add_pattern("*.jpg")
        filter_image.add_pattern("*.jpeg")
        filter_image.add_pattern("*.JPG")
        filter_image.add_pattern("*.JPEG")
        filter_image.add_pattern("*.png")
        filter_image.add_pattern("*.PNG")
        filter_image.add_pattern("*.tiff")
        filter_image.add_pattern("*.bmp")
        dialog.add_filter(filter_image)
        
        filter_image = Gtk.FileFilter()
        filter_image.set_name("Arquivos jpg")
        filter_image.add_pattern("*.jpg")
        dialog.add_filter(filter_image)

        filter_image = Gtk.FileFilter()
        filter_image.set_name("Arquivos jpeg")
        filter_image.add_pattern("*.jpeg")
        dialog.add_filter(filter_image)
        
        filter_image = Gtk.FileFilter()
        filter_image.set_name("Arquivos JPG")
        filter_image.add_pattern("*.JPG")
        dialog.add_filter(filter_image)

        filter_image = Gtk.FileFilter()
        filter_image.set_name("Arquivos JPEG")
        filter_image.add_pattern("*.JPEG")
        dialog.add_filter(filter_image)      

        filter_image = Gtk.FileFilter()
        filter_image.set_name("Arquivos PNG")
        filter_image.add_pattern("*.png")
        dialog.add_filter(filter_image)

    def convert(self, resized):
        #Converte Imagem para Escala de Cinza
        img_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        #Inverte a Imagem
        img_invert = cv2.bitwise_not(img_gray)

        #Além disso, também estaremos suavizando a imagem para garantir que o esboço obtido seja menos recortado e suave
        img_smoothing = cv2.blur(img_invert,(self.value1,self.value2))
        
        #Convertendo as imagens em esboços a lápis
        final = cv2.divide(img_gray, 255 - img_smoothing, scale=self.value3)
        final = cv2.cvtColor(final, cv2.COLOR_GRAY2BGR)

        self.btnSalvar.set_sensitive(True)

        return final

    def show_image(self, final):
        h, w, d = final.shape
        
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(final.tobytes(), GdkPixbuf.Colorspace.RGB, False, 8, w, h, w*3, None, None)
        self.image1.set_from_pixbuf(pixbuf)
    
    def spin1_value_changed(self, widget):
        self.value1 = int(widget.get_value())
        img = self.convert(self.resized)
        self.show_image(img)

    def spin2_value_changed(self, widget):
        self.value2 = int(widget.get_value())
        img = self.convert(self.resized)
        self.show_image(img)

    def spin3_value_changed(self, widget):
        self.value3 = int(widget.get_value())
        img = self.convert(self.resized)
        self.show_image(img)

    def on_btnConvert_clicked(self, widget):
        img = self.convert(self.resized)
        self.show_image(img)

    def save_image(self, widget):
        final = self.convert(self.img)
        
        dialog = Gtk.FileChooserDialog(title="Salvar Arquivo", parent=self.main_window, action=Gtk.FileChooserAction.SAVE)

        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        
        self.add_filters(dialog)

        dialog.set_filename(self.filename)
        
        dialog.set_local_only(False)

        dialog.set_current_folder(self.path)

        dialog.set_do_overwrite_confirmation(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file = dialog.get_filename()

            self.path = dialog.get_current_folder()
            
            cv2.imwrite(file, final)

            dialog.destroy()

            self.info_message("Arquivo salvo no disco.")
        
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()


    def info_message(self, message):
        messagedialog = Gtk.MessageDialog( parent=None, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, message_format=message)

        messagedialog.set_title("Salvar Arquivo")

        messagedialog.connect("response", self.info_dialog_response)

        messagedialog.show()

    def info_dialog_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            widget.destroy()

    def main(self):
        Gtk.main()

sketch_photo = SketchPhoto()
sketch_photo.main()
