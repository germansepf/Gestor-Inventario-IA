import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import threading
from modules.excel_handler import read_excel, write_excel
from modules.data_cleaner import clean_and_transform_data, apply_filters
from modules.ai_description import generate_commercial_name, generate_commercial_names_in_parallel, generate_description, generate_descriptions_in_parallel, cache, save_cache

import os
import sys

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class ProductFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Inventario - Conexiones Celulares")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        
        # Cambiar el ícono de la ventana
        self.root.iconbitmap(resource_path("logoconex.ico"))  # Cambiar el ícono de la ventana
        
        # Configurar tema y estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Usar un tema más moderno
        
        # Configurar estilos personalizados
        self.configure_styles()
        
        # Variables
        self.file1 = None  
        self.df_original = None  
        self.df_filtered = None
        self.loading = False
        self.animation_id = None

        # Crear un frame principal con un fondo personalizado
        self.main_frame = tk.Frame(root, bg="#f5f5f7")
        self.main_frame.pack(fill="both", expand=True)
        
        # ---- Título con animación ----
        self.title_frame = tk.Frame(self.main_frame, bg="#f5f5f7")
        self.title_frame.pack(pady=10)
        
        self.title_label = tk.Label(
            self.title_frame, 
            text="🔍 Filtros y Generación de Inventario", 
            font=("Montserrat", 18, "bold"), 
            fg="#E30B2C",
            bg="#f5f5f7"
        )
        self.title_label.pack(pady=5)
        
        # Animación de subrayado para el título
        self.underline_canvas = tk.Canvas(self.title_frame, height=3, bg="#f5f5f7", highlightthickness=0)
        self.underline_canvas.pack(fill="x", padx=20)
        self.animate_title_underline()

        # ---- Botón para seleccionar archivo ----
        self.button_frame = tk.Frame(self.main_frame, bg="#f5f5f7")
        self.button_frame.pack(pady=10)
        
        self.select_file_btn = tk.Button(
            self.button_frame, 
            text="📂 Cargar Inventario", 
            command=self.select_file1,
            font=("Montserrat", 12, "bold"), 
            bg="#E30B2C", 
            fg="white", 
            padx=15, 
            pady=8, 
            bd=0, 
            cursor="hand2",
            activebackground="#c00921",
            activeforeground="white",
            relief=tk.RAISED
        )
        self.select_file_btn.pack(pady=5)
        self.add_hover_effect(self.select_file_btn)

        # ---- Sección de filtros ----
        self.filters_frame = tk.LabelFrame(
            self.main_frame, 
            text="Filtros", 
            font=("Montserrat", 12, "bold"), 
            padx=15, 
            pady=15,
            bg="#f5f5f7",
            fg="#333333"
        )
        self.filters_frame.pack(fill="x", padx=20, pady=10)

        # 🔹 Filtro de sucursales
        self.sucursal_label = tk.Label(
            self.filters_frame, 
            text="Sucursales:", 
            font=("Montserrat", 11),
            bg="#f5f5f7",
            fg="#333333"
        )
        self.sucursal_label.grid(row=0, column=0, padx=5, sticky="w")

        # Frame para el listbox con borde personalizado
        self.listbox_frame = tk.Frame(self.filters_frame, bg="#E30B2C", padx=1, pady=1)
        self.listbox_frame.grid(row=0, column=1, padx=5, pady=5)
        
        self.sucursal_listbox = tk.Listbox(
            self.listbox_frame, 
            selectmode=tk.MULTIPLE, 
            height=6, 
            width=35,
            font=("Montserrat", 10),
            bg="white",
            selectbackground="#E30B2C",
            relief=tk.FLAT
        )
        self.sucursal_listbox.pack()

        self.select_all_var = tk.BooleanVar()
        self.select_all_checkbox = ttk.Checkbutton(
            self.filters_frame, 
            text="Seleccionar todas", 
            variable=self.select_all_var,
            command=self.toggle_select_all,
            style="TCheckbutton"
        )
        self.select_all_checkbox.grid(row=0, column=2, padx=5, sticky="w")

        # 🔹 Filtro por precio
        self.price_frame = tk.Frame(self.filters_frame, bg="#f5f5f7")
        self.price_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="w")
        
        self.min_price_label = tk.Label(
            self.price_frame, 
            text="Precio mínimo:", 
            font=("Montserrat", 11),
            bg="#f5f5f7",
            fg="#333333"
        )
        self.min_price_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.min_price_entry = tk.Entry(
            self.price_frame, 
            width=10,
            font=("Montserrat", 10),
            relief=tk.FLAT,
            bd=2,
            highlightthickness=1,
            highlightbackground="#cccccc",
            highlightcolor="#E30B2C"
        )
        self.min_price_entry.grid(row=0, column=1, padx=5, pady=5)

        self.max_price_label = tk.Label(
            self.price_frame, 
            text="Precio máximo:", 
            font=("Montserrat", 11),
            bg="#f5f5f7",
            fg="#333333"
        )
        self.max_price_label.grid(row=0, column=2, padx=15, pady=5, sticky="w")

        self.max_price_entry = tk.Entry(
            self.price_frame, 
            width=10,
            font=("Montserrat", 10),
            relief=tk.FLAT,
            bd=2,
            highlightthickness=1,
            highlightbackground="#cccccc",
            highlightcolor="#E30B2C"
        )
        self.max_price_entry.grid(row=0, column=3, padx=5, pady=5)

        # ---- Botones de acción ----
        self.action_frame = tk.Frame(self.main_frame, bg="#f5f5f7")
        self.action_frame.pack(pady=15)
        
        # Botón para resetear filtros (NUEVO)
        self.reset_btn = tk.Button(
            self.action_frame, 
            text="🔄 Resetear Filtros", 
            command=self.reset_filters,
            font=("Montserrat", 11, "bold"), 
            bg="#6c757d", 
            fg="white", 
            padx=10, 
            pady=5, 
            bd=0, 
            cursor="hand2",
            activebackground="#5a6268",
            activeforeground="white",
            relief=tk.RAISED
        )
        self.reset_btn.grid(row=0, column=0, padx=10, pady=5)
        self.add_hover_effect(self.reset_btn)
        
        # Botón para aplicar filtros
        self.filter_btn = tk.Button(
            self.action_frame, 
            text="✅ Aplicar Filtros", 
            command=self.apply_filters,
            font=("Montserrat", 11, "bold"), 
            bg="#28A745", 
            fg="white", 
            padx=10, 
            pady=5, 
            bd=0, 
            cursor="hand2",
            activebackground="#218838",
            activeforeground="white",
            relief=tk.RAISED
        )
        self.filter_btn.grid(row=0, column=1, padx=10, pady=5)
        self.add_hover_effect(self.filter_btn)

        # ---- Botón para ejecutar OpenAI (Generar con IA) ----
        self.generate_btn = tk.Button(
            self.main_frame, 
            text="⚡ Generar con IA", 
            command=self.generate_with_ai_thread,
            font=("Montserrat", 12, "bold"), 
            bg="#E30B2C", 
            fg="white", 
            padx=15, 
            pady=8, 
            bd=0, 
            cursor="hand2", 
            state=tk.DISABLED,
            activebackground="#c00921",
            activeforeground="white",
            relief=tk.RAISED
        )
        self.generate_btn.pack(pady=10)
        self.add_hover_effect(self.generate_btn)

        # ---- Botón para guardar archivo final ----
        self.save_btn = tk.Button(
            self.main_frame, 
            text="💾 Guardar Archivo", 
            command=self.save_filtered_file,
            font=("Montserrat", 12, "bold"), 
            bg="#FFC107", 
            fg="black", 
            padx=15, 
            pady=8, 
            bd=0, 
            cursor="hand2", 
            state=tk.DISABLED,
            activebackground="#e0a800",
            activeforeground="black",
            relief=tk.RAISED
        )
        self.save_btn.pack(pady=10)
        self.add_hover_effect(self.save_btn)

        # ---- Barra de estado con animación ----
        self.status_frame = tk.Frame(self.main_frame, bg="#f5f5f7")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.status_label = tk.Label(
            self.status_frame, 
            text="Esperando...", 
            font=("Montserrat", 10, "italic"),
            bg="#f5f5f7",
            fg="#666666"
        )
        self.status_label.pack(pady=5)
        
        # Barra de progreso (oculta por defecto)
        self.progress = ttk.Progressbar(
            self.status_frame, 
            orient="horizontal", 
            length=300, 
            mode="indeterminate",
            style="TProgressbar"
        )
        
        # Iniciar animación de título
        self.animate_title()

    def configure_styles(self):
        """Configura los estilos personalizados para los widgets ttk"""
        # Estilo para Checkbutton
        self.style.configure(
            "TCheckbutton", 
            background="#f5f5f7", 
            font=("Montserrat", 10),
            foreground="#333333"
        )
        
        # Estilo para Progressbar
        self.style.configure(
            "TProgressbar", 
            troughcolor="#f5f5f7", 
            background="#E30B2C",
            thickness=6
        )

    def animate_title(self):
        """Animación sutil del título"""
        colors = ["#E30B2C", "#d1071f", "#bf0519", "#d1071f", "#E30B2C"]
        current_color = getattr(self, "color_index", 0)
        
        self.title_label.config(fg=colors[current_color])
        
        self.color_index = (current_color + 1) % len(colors)
        self.root.after(1000, self.animate_title)

    def animate_title_underline(self):
        """Animación de subrayado para el título"""
        self.underline_canvas.delete("underline")
        width = self.title_label.winfo_width()
        
        if width > 0:  # Asegurarse de que el título ya se ha renderizado
            self.underline_canvas.create_line(
                10, 2, width-10, 2, 
                fill="#E30B2C", 
                width=3, 
                tags="underline"
            )
        
        self.root.after(100, self.animate_title_underline)

    def add_hover_effect(self, button):
        """Añade efecto hover a los botones"""
        original_bg = button["bg"]
        darker_bg = self.darken_color(original_bg)
        
        def on_enter(e):
            if button["state"] != tk.DISABLED:
                button["bg"] = darker_bg
                
        def on_leave(e):
            if button["state"] != tk.DISABLED:
                button["bg"] = original_bg
                
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def darken_color(self, hex_color):
        """Oscurece un color hexadecimal"""
        # Convertir a RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Oscurecer
        factor = 0.85
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        # Convertir de vuelta a hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def show_loading(self, message="Procesando..."):
        """Muestra animación de carga"""
        self.loading = True
        self.status_label.config(text=message)
        self.progress.pack(pady=5)
        self.progress.start(10)
        
    def hide_loading(self, message="Completado"):
        """Oculta animación de carga"""
        self.loading = False
        self.status_label.config(text=message)
        self.progress.stop()
        self.progress.pack_forget()

    def reset_filters(self):
        """Resetea todos los filtros y botones a su estado inicial"""
        # Limpiar selección de sucursales
        self.sucursal_listbox.select_clear(0, tk.END)
        self.select_all_var.set(False)
        
        # Limpiar campos de precio
        self.min_price_entry.delete(0, tk.END)
        self.max_price_entry.delete(0, tk.END)
        
        # Resetear estado de botones si es necesario
        if self.df_original is not None:
            self.generate_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.DISABLED)
            
        # Actualizar mensaje de estado
        self.status_label.config(text="Filtros reseteados")
        
        # Efecto visual de confirmación
        self.flash_status_message("✅ Filtros reseteados correctamente")

    def flash_status_message(self, message, duration=1500):
        """Muestra un mensaje temporal con efecto de desvanecimiento"""
        original_text = self.status_label.cget("text")
        original_fg = self.status_label.cget("fg")
        
        # Mostrar el nuevo mensaje en verde
        self.status_label.config(text=message, fg="#28A745")
        
        # Programar la restauración del mensaje original
        self.root.after(duration, lambda: self.status_label.config(text=original_text, fg=original_fg))

    def select_file1(self):
        """Selecciona el archivo de inventario y carga las sucursales."""
        file_path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx *.xls")])
        if not file_path:
            return

        # Mostrar animación de carga
        self.show_loading("⏳ Cargando archivo...")
        
        # Usar un hilo para no bloquear la interfaz
        def load_file():
            try:
                self.file1 = file_path
                self.df_original = read_excel(self.file1)

                # Transformar y agrupar los datos automáticamente
                self.df_original = clean_and_transform_data(self.df_original)

                # Cargar sucursales únicas
                sucursales = sorted(self.df_original["brand"].astype(str).unique())
                
                # Actualizar UI en el hilo principal
                self.root.after(0, lambda: self.update_ui_after_load(sucursales))
                
            except Exception as e:
                error_message = str(e)
                self.root.after(0, lambda: self.show_error(f"Error al cargar archivo: {error_message}"))
        
        threading.Thread(target=load_file).start()

    def update_ui_after_load(self, sucursales):
        """Actualiza la UI después de cargar el archivo"""
        # Actualizar listbox de sucursales
        self.sucursal_listbox.delete(0, tk.END)
        for sucursal in sucursales:
            self.sucursal_listbox.insert(tk.END, sucursal)
        
        # Ocultar animación de carga
        self.hide_loading("✅ Archivo cargado correctamente")
        
        # Habilitar botones
        self.generate_btn.config(state=tk.NORMAL)
        
        # Mostrar mensaje
        messagebox.showinfo("Archivo Cargado", f"Archivo cargado con éxito. Se encontraron {len(self.df_original)} productos.")

    def show_error(self, message):
        """Muestra un mensaje de error y oculta la animación de carga"""
        self.hide_loading("❌ Error")
        messagebox.showerror("Error", message)

    def toggle_select_all(self):
        """Seleccionar/Deseleccionar todas las sucursales."""
        if self.select_all_var.get():
            self.sucursal_listbox.select_set(0, tk.END)
        else:
            self.sucursal_listbox.select_clear(0, tk.END)

    def apply_filters(self):
        """Aplica los filtros de sucursal y precio."""
        if self.df_original is None:
            messagebox.showwarning("Atención", "Primero debes cargar un archivo.")
            return

        # Mostrar animación de carga
        self.show_loading("⏳ Aplicando filtros...")
        
        # Usar un hilo para no bloquear la interfaz
        def filter_data():
            try:
                # Paso 2: Filtrar por sucursales
                selected_indices = self.sucursal_listbox.curselection()
                selected_sucursales = [self.sucursal_listbox.get(i) for i in selected_indices]

                # Paso 3: Filtrar por precios
                min_price = float(self.min_price_entry.get()) if self.min_price_entry.get() else None
                max_price = float(self.max_price_entry.get()) if self.max_price_entry.get() else None

                self.df_filtered = apply_filters(self.df_original, selected_sucursales, min_price, max_price)

                # Actualizar UI en el hilo principal
                self.root.after(0, lambda: self.update_ui_after_filter())
                
            except ValueError:
                self.root.after(0, lambda: self.show_error("Los valores de precio deben ser números."))
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error al aplicar filtros: {e}"))
        
        threading.Thread(target=filter_data).start()

    def update_ui_after_filter(self):
        """Actualiza la UI después de aplicar filtros"""
        # Ocultar animación de carga
        self.hide_loading("✅ Filtros aplicados correctamente")
        
        # Habilitar botones
        self.generate_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        
        # Mostrar mensaje con animación
        messagebox.showinfo("Filtros Aplicados", f"Se encontraron {len(self.df_filtered)} productos.")

    def generate_with_ai_thread(self):
        """Ejecuta la generación con IA en un hilo secundario."""
        self.show_loading("⚡ Generando con IA... por favor espera.")
        self.generate_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.generate_with_ai)
        thread.start()

    def generate_with_ai(self):
        """Actualiza el caché: genera nombres comerciales y descripciones faltantes usando paralelización."""
        try:
            if not cache:
                raise ValueError("El caché está vacío o no se pudo cargar.")

            # Paso 1: Identificar genéricos sin nombre comercial
            productos_sin_nombre = [name for name, data in cache.items()
                                    if not data.get("commercial_name")]

            if productos_sin_nombre:
                print(f"⚡ Generando nombres comerciales para {len(productos_sin_nombre)} productos...")
                generate_commercial_names_in_parallel(productos_sin_nombre, max_workers=5)

            # Paso 2: Identificar comerciales sin descripción
            productos_sin_descripcion = []
            for generic_name, data in cache.items():
                nombre_comercial = data.get("commercial_name")
                descripcion = data.get("description")
    
                # Verificar si hay un nombre comercial pero no hay descripción
                if nombre_comercial and (not descripcion or str(descripcion).strip() == "nan"):
                    print(f"⚠ El producto '{generic_name}' tiene nombre comercial pero no descripción.")
                    productos_sin_descripcion.append({"generic_name": generic_name, "name": nombre_comercial})

            if productos_sin_descripcion:
                print(f"📝 Generando descripciones para {len(productos_sin_descripcion)} productos...")
                generate_descriptions_in_parallel(productos_sin_descripcion, max_workers=5)

            # Paso 3: Guardar cache actualizado
            save_cache(cache)
            
            # Actualizar UI en el hilo principal
            self.root.after(0, lambda: self.update_ui_after_ai())
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"No se pudo generar con IA: {e}"))

    def update_ui_after_ai(self):
        """Actualiza la UI después de generar con IA"""
        # Ocultar animación de carga
        self.hide_loading("✅ IA completada. El caché ha sido actualizado.")
        
        # Habilitar botones
        self.save_btn.config(state=tk.NORMAL)
        
        # Mostrar mensaje con animación
        messagebox.showinfo("IA Completada", "Caché actualizado exitosamente con nombres y descripciones.")

    def save_filtered_file(self):
        """Guarda el archivo final filtrado."""
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if save_path:
            # Mostrar animación de carga
            self.show_loading("💾 Guardando archivo...")
            
            # Usar un hilo para no bloquear la interfaz
            def save_file():
                try:
                    write_excel(self.df_filtered, save_path)
                    
                    # Actualizar UI en el hilo principal
                    self.root.after(0, lambda: self.update_ui_after_save())
                    
                except Exception as e:
                    self.root.after(0, lambda: self.show_error(f"Error al guardar archivo: {e}"))
            
            threading.Thread(target=save_file).start()

    def update_ui_after_save(self):
        """Actualiza la UI después de guardar el archivo"""
        # Ocultar animación de carga
        self.hide_loading("✅ Archivo guardado correctamente")
        
        # Mostrar mensaje con animación
        messagebox.showinfo("Guardado", "Archivo guardado correctamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductFilterApp(root)
    root.mainloop()

