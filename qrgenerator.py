#!/usr/bin/env python3
"""
QR CODE GENERATOR - VERSI TANPA SCANNER
FIX: No pyzbar, no opencv - PASTI JADI EXE!
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import qrcode
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime
import os

class QRGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("QR GENERATOR - NO SCANNER")
        self.root.geometry("1200x700")
        self.root.configure(bg='#1e1e1e')
        
        self.current_qr = None
        self.setup_database()
        self.setup_ui()
        self.root.mainloop()
    
    def setup_database(self):
        self.conn = sqlite3.connect('qr_codes.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_qr (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                qr_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def setup_ui(self):
        # MAIN CONTAINER
        main = tk.Frame(self.root, bg='#1e1e1e')
        main.pack(fill='both', expand=True, padx=15, pady=15)
        
        # LEFT PANEL
        left = tk.Frame(main, bg='#2d2d2d', width=500, relief='ridge', bd=2)
        left.pack(side='left', fill='both', expand=True, padx=(0,10))
        left.pack_propagate(False)
        
        tk.Label(left, text="🎯 QR GENERATOR", font=("Arial", 16, "bold"),
                bg='#2d2d2d', fg='#0078d7').pack(pady=15)
        
        # QR TYPE
        type_frame = tk.LabelFrame(left, text="📋 Pilih Tipe QR", bg='#2d2d2d', fg='white',
                                  font=('Arial', 11, 'bold'), padx=15, pady=15)
        type_frame.pack(fill='x', padx=15, pady=5)
        
        self.qr_type = tk.StringVar(value="Text/URL")
        types = [("📝 Text/URL", "Text/URL"), ("📶 WiFi", "WiFi"), ("👤 Contact", "Contact"),
                ("📧 Email", "Email"), ("💬 SMS", "SMS"), ("📍 Location", "Location")]
        
        for i, (text, val) in enumerate(types):
            tk.Radiobutton(type_frame, text=text, variable=self.qr_type, value=val,
                          bg='#2d2d2d', fg='white', selectcolor='#2d2d2d',
                          command=self.on_type_change).grid(row=i//3, column=i%3, padx=10, pady=5, sticky='w')
        
        # INPUT CONTAINER
        self.input_container = tk.LabelFrame(left, text="📝 Input Data", bg='#2d2d2d', fg='white',
                                           font=('Arial', 11, 'bold'), padx=15, pady=15)
        self.input_container.pack(fill='both', expand=True, padx=15, pady=10)
        
        self.create_text_frame()
        self.create_wifi_frame()
        self.create_contact_frame()
        self.create_email_frame()
        self.create_sms_frame()
        self.create_location_frame()
        self.show_frame(self.text_frame)
        
        # SETTINGS
        settings = tk.LabelFrame(left, text="⚙️ QR Settings", bg='#2d2d2d', fg='white',
                                font=('Arial', 11, 'bold'), padx=15, pady=15)
        settings.pack(fill='x', padx=15, pady=5)
        
        # Size
        size_frame = tk.Frame(settings, bg='#2d2d2d')
        size_frame.pack(fill='x', pady=5)
        tk.Label(size_frame, text="Size:", bg='#2d2d2d', fg='white').pack(side='left')
        self.size_var = tk.IntVar(value=12)
        tk.Scale(size_frame, from_=8, to=30, orient='horizontal', variable=self.size_var,
                length=200, bg='#2d2d2d', fg='white', troughcolor='#3c3c3c').pack(side='left', padx=20)
        
        # Border
        border_frame = tk.Frame(settings, bg='#2d2d2d')
        border_frame.pack(fill='x', pady=5)
        tk.Label(border_frame, text="Border:", bg='#2d2d2d', fg='white').pack(side='left')
        self.border_var = tk.IntVar(value=2)
        tk.Scale(border_frame, from_=0, to=5, orient='horizontal', variable=self.border_var,
                length=200, bg='#2d2d2d', fg='white', troughcolor='#3c3c3c').pack(side='left', padx=20)
        
        # Colors
        color_frame = tk.Frame(settings, bg='#2d2d2d')
        color_frame.pack(fill='x', pady=10)
        
        self.fill_color = tk.StringVar(value="#000000")
        tk.Label(color_frame, text="Fill:", bg='#2d2d2d', fg='white').pack(side='left')
        tk.Button(color_frame, text="🎨 Pick", command=self.pick_fill_color,
                 bg='#2d2d2d', fg='white', relief='raised', bd=2).pack(side='left', padx=10)
        
        self.back_color = tk.StringVar(value="#FFFFFF")
        tk.Label(color_frame, text="Background:", bg='#2d2d2d', fg='white').pack(side='left', padx=(20,0))
        tk.Button(color_frame, text="🎨 Pick", command=self.pick_back_color,
                 bg='#2d2d2d', fg='white').pack(side='left', padx=10)
        
        # GENERATE BUTTON
        tk.Button(left, text="🔮 GENERATE QR CODE", command=self.generate_qr,
                 bg='#0078d7', fg='white', font=('Arial', 14, 'bold'),
                 padx=30, pady=15, relief='raised', bd=3, cursor='hand2').pack(pady=15, padx=15, fill='x')
        
        # RIGHT PANEL
        right = tk.Frame(main, bg='#2d2d2d', relief='ridge', bd=2)
        right.pack(side='right', fill='both', expand=True)
        
        # QR DISPLAY
        display = tk.LabelFrame(right, text="📱 QR RESULT", bg='#2d2d2d', fg='white',
                                font=('Arial', 12, 'bold'), padx=20, pady=20)
        display.pack(fill='both', expand=True, padx=15, pady=15)
        
        self.qr_label = tk.Label(display, bg='white', relief='sunken', bd=3, width=400, height=400)
        self.qr_label.pack(pady=20)
        
        self.qr_info = tk.Label(display, text="Generate QR code untuk mulai",
                               bg='#2d2d2d', fg='#888888', font=('Arial', 10))
        self.qr_info.pack(pady=5)
        
        # BUTTONS
        btn_frame = tk.Frame(display, bg='#2d2d2d')
        btn_frame.pack(pady=10)
        
        self.save_btn = tk.Button(btn_frame, text="💾 Save QR", command=self.save_qr,
                                 bg='#28a745', fg='white', font=('Arial', 11),
                                 padx=20, pady=8, state='disabled')
        self.save_btn.pack(side='left', padx=5)
        
        self.download_btn = tk.Button(btn_frame, text="⬇️ Quick Download", command=self.download_qr,
                                     bg='#ffc107', fg='black', font=('Arial', 11),
                                     padx=20, pady=8, state='disabled')
        self.download_btn.pack(side='left', padx=5)
    
    def create_text_frame(self):
        self.text_frame = tk.Frame(self.input_container, bg='#2d2d2d')
        tk.Label(self.text_frame, text="Text / URL:", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0,5))
        self.text_entry = tk.Text(self.text_frame, height=4, font=('Arial', 11),
                                 bg='#3c3c3c', fg='white', insertbackground='white',
                                 relief='flat', bd=3)
        self.text_entry.pack(fill='x')
        self.text_entry.insert('1.0', "https://github.com/username")
    
    def create_wifi_frame(self):
        self.wifi_frame = tk.Frame(self.input_container, bg='#2d2d2d')
        tk.Label(self.wifi_frame, text="SSID:", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0,5))
        self.wifi_ssid = tk.Entry(self.wifi_frame, font=('Arial', 11),
                                 bg='#3c3c3c', fg='white', insertbackground='white', relief='flat', bd=3)
        self.wifi_ssid.pack(fill='x', pady=5)
        self.wifi_ssid.insert(0, "WiFi Name")
        
        tk.Label(self.wifi_frame, text="Password:", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10,5))
        self.wifi_pass = tk.Entry(self.wifi_frame, font=('Arial', 11),
                                 bg='#3c3c3c', fg='white', insertbackground='white', show='*', relief='flat', bd=3)
        self.wifi_pass.pack(fill='x', pady=5)
        
        tk.Label(self.wifi_frame, text="Encryption:", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10,5))
        self.wifi_encrypt = ttk.Combobox(self.wifi_frame, values=['WPA2', 'WPA', 'WEP', 'None'],
                                         state='readonly', font=('Arial', 11))
        self.wifi_encrypt.pack(fill='x', pady=5)
        self.wifi_encrypt.set('WPA2')
    
    def create_contact_frame(self):
        self.contact_frame = tk.Frame(self.input_container, bg='#2d2d2d')
        self.contact_entries = {}
        fields = [('Nama *', 'name'), ('Telepon', 'phone'), ('Email', 'email'),
                 ('Perusahaan', 'company'), ('Alamat', 'address')]
        
        for label, key in fields:
            tk.Label(self.contact_frame, text=label, bg='#2d2d2d', fg='white',
                    font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10,5))
            entry = tk.Entry(self.contact_frame, font=('Arial', 11),
                           bg='#3c3c3c', fg='white', insertbackground='white', relief='flat', bd=3)
            entry.pack(fill='x', pady=5)
            self.contact_entries[key] = entry
    
    def create_email_frame(self):
        self.email_frame = tk.Frame(self.input_container, bg='#2d2d2d')
        tk.Label(self.email_frame, text="Email Tujuan *", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0,5))
        self.email_to = tk.Entry(self.email_frame, font=('Arial', 11),
                                bg='#3c3c3c', fg='white', insertbackground='white', relief='flat', bd=3)
        self.email_to.pack(fill='x', pady=5)
        self.email_to.insert(0, "nama@email.com")
        
        tk.Label(self.email_frame, text="Subject:", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10,5))
        self.email_subject = tk.Entry(self.email_frame, font=('Arial', 11),
                                     bg='#3c3c3c', fg='white', insertbackground='white', relief='flat', bd=3)
        self.email_subject.pack(fill='x', pady=5)
        
        tk.Label(self.email_frame, text="Body:", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10,5))
        self.email_body = tk.Text(self.email_frame, height=4, font=('Arial', 11),
                                 bg='#3c3c3c', fg='white', insertbackground='white', relief='flat', bd=3)
        self.email_body.pack(fill='x', pady=5)
    
    def create_sms_frame(self):
        self.sms_frame = tk.Frame(self.input_container, bg='#2d2d2d')
        tk.Label(self.sms_frame, text="Nomor Telepon *", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0,5))
        self.sms_number = tk.Entry(self.sms_frame, font=('Arial', 11),
                                  bg='#3c3c3c', fg='white', insertbackground='white', relief='flat', bd=3)
        self.sms_number.pack(fill='x', pady=5)
        self.sms_number.insert(0, "081234567890")
        
        tk.Label(self.sms_frame, text="Pesan:", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10,5))
        self.sms_message = tk.Text(self.sms_frame, height=4, font=('Arial', 11),
                                  bg='#3c3c3c', fg='white', insertbackground='white', relief='flat', bd=3)
        self.sms_message.pack(fill='x', pady=5)
    
    def create_location_frame(self):
        self.location_frame = tk.Frame(self.input_container, bg='#2d2d2d')
        tk.Label(self.location_frame, text="Latitude *", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0,5))
        self.loc_lat = tk.Entry(self.location_frame, font=('Arial', 11),
                               bg='#3c3c3c', fg='white', insertbackground='white', relief='flat', bd=3)
        self.loc_lat.pack(fill='x', pady=5)
        self.loc_lat.insert(0, "-6.2088")
        
        tk.Label(self.location_frame, text="Longitude *", bg='#2d2d2d', fg='white',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10,5))
        self.loc_lon = tk.Entry(self.location_frame, font=('Arial', 11),
                               bg='#3c3c3c', fg='white', insertbackground='white', relief='flat', bd=3)
        self.loc_lon.pack(fill='x', pady=5)
        self.loc_lon.insert(0, "106.8456")
    
    def on_type_change(self):
        for f in [self.text_frame, self.wifi_frame, self.contact_frame,
                 self.email_frame, self.sms_frame, self.location_frame]:
            f.pack_forget()
        
        t = self.qr_type.get()
        if t == "Text/URL": self.show_frame(self.text_frame)
        elif t == "WiFi": self.show_frame(self.wifi_frame)
        elif t == "Contact": self.show_frame(self.contact_frame)
        elif t == "Email": self.show_frame(self.email_frame)
        elif t == "SMS": self.show_frame(self.sms_frame)
        elif t == "Location": self.show_frame(self.location_frame)
    
    def show_frame(self, frame):
        frame.pack(fill='both', expand=True, pady=5)
    
    def generate_qr(self):
        try:
            t = self.qr_type.get()
            
            if t == "Text/URL":
                content = self.text_entry.get('1.0', tk.END).strip()
                if not content: return messagebox.showwarning("Warning", "Isi text/URL!")
            elif t == "WiFi":
                ssid = self.wifi_ssid.get().strip()
                if not ssid: return messagebox.showwarning("Warning", "SSID harus diisi!")
                pw = self.wifi_pass.get().strip()
                enc = self.wifi_encrypt.get()
                content = f"WIFI:S:{ssid};T:{enc};P:{pw};;" if enc != 'None' else f"WIFI:S:{ssid};T:nopass;;"
            elif t == "Contact":
                name = self.contact_entries['name'].get().strip()
                if not name: return messagebox.showwarning("Warning", "Nama harus diisi!")
                content = f"BEGIN:VCARD\nVERSION:3.0\nN:{name}\nFN:{name}\nEND:VCARD"
            elif t == "Email":
                to = self.email_to.get().strip()
                if not to: return messagebox.showwarning("Warning", "Email tujuan harus diisi!")
                sub = self.email_subject.get().strip()
                body = self.email_body.get('1.0', tk.END).strip()
                content = f"mailto:{to}?subject={sub}&body={body}"
            elif t == "SMS":
                num = self.sms_number.get().strip()
                if not num: return messagebox.showwarning("Warning", "Nomor telepon harus diisi!")
                msg = self.sms_message.get('1.0', tk.END).strip()
                content = f"smsto:{num}:{msg}"
            elif t == "Location":
                lat = self.loc_lat.get().strip()
                lon = self.loc_lon.get().strip()
                if not lat or not lon: return messagebox.showwarning("Warning", "Latitude & Longitude harus diisi!")
                content = f"geo:{lat},{lon}"
            
            qr = qrcode.QRCode(box_size=self.size_var.get(), border=self.border_var.get())
            qr.add_data(content)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color=self.fill_color.get(), back_color=self.back_color.get())
            img_display = img.copy()
            img_display.thumbnail((400,400))
            
            self.tk_image = ImageTk.PhotoImage(img_display)
            self.qr_label.config(image=self.tk_image, width=400, height=400)
            self.current_qr = img
            self.save_btn.config(state='normal')
            self.download_btn.config(state='normal')
            self.qr_info.config(text=f"✅ QR Generated | Type: {t}")
            
            self.cursor.execute('INSERT INTO generated_qr (content, qr_type) VALUES (?,?)',
                              (content[:50], t))
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal: {str(e)}")
    
    def save_qr(self):
        if self.current_qr:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if f: self.current_qr.save(f); messagebox.showinfo("Success", f"Tersimpan: {f}")
    
    def download_qr(self):
        if self.current_qr:
            f = f"QR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.current_qr.save(f)
            messagebox.showinfo("Success", f"Tersimpan: {f}")
    
    def pick_fill_color(self):
        c = colorchooser.askcolor(color=self.fill_color.get())
        if c[1]: self.fill_color.set(c[1])
    
    def pick_back_color(self):
        c = colorchooser.askcolor(color=self.back_color.get())
        if c[1]: self.back_color.set(c[1])

if __name__ == "__main__":
    QRGenerator()