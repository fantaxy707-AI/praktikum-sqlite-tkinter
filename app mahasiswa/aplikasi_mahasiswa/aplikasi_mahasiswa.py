import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from contextlib import contextmanager
import os

DB_NAME = "mahasiswa.db"


@contextmanager
def koneksi():
    """
    Generator context manager untuk mengelola koneksi database SQLite.
    Melakukan commit otomatis jika berhasil, rollback jika terjadi exception,
    dan selalu menutup koneksi di blok finally.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def inisialisasi_db():
    """Membuat tabel mahasiswa jika belum ada."""
    with koneksi() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mahasiswa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                nim TEXT NOT NULL UNIQUE,
                prodi TEXT NOT NULL,
                alamat TEXT,
                angkatan INTEGER NOT NULL
            )
            """
        )


class AplikasiMahasiswa(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Data Mahasiswa")
        self.geometry("950x650")
        self.minsize(850, 550)

        # Variabel untuk menampung ID data terpilih
        self.selected_id = None

        # Style ttk
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        self.style.configure("Treeview", font=("Helvetica", 9), rowheight=25)

        self._buat_komponen()
        self.muat_data()

    def _buat_komponen(self):
        # Frame Utama
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ================= FORMULIR INPUT =================
        form_frame = ttk.LabelFrame(main_frame, text=" Formulir Data Mahasiswa ", padding="15")
        form_frame.pack(fill=tk.X, pady=(0, 10))

        # Grid form
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Baris 0: Nama & NIM
        ttk.Label(form_frame, text="Nama Lengkap:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=6)
        self.txt_nama = ttk.Entry(form_frame)
        self.txt_nama.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=6)

        ttk.Label(form_frame, text="NIM:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=6)
        self.txt_nim = ttk.Entry(form_frame)
        self.txt_nim.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=6)

        # Baris 1: Program Studi & Angkatan
        ttk.Label(form_frame, text="Program Studi:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=6)
        prodi_options = ("Informatika", "Sistem Informasi", "Manajemen", "Akuntansi")
        self.cmb_prodi = ttk.Combobox(form_frame, values=prodi_options, state="readonly")
        self.cmb_prodi.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=6)

        ttk.Label(form_frame, text="Angkatan (Tahun):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=6)
        self.txt_angkatan = ttk.Entry(form_frame)
        self.txt_angkatan.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=6)

        # Baris 2: Alamat
        ttk.Label(form_frame, text="Alamat:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=6)
        self.txt_alamat = ttk.Entry(form_frame)
        self.txt_alamat.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=6)

        # ================= TOMBOL AKSI =================
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 15))

        self.btn_simpan = ttk.Button(btn_frame, text="Simpan Data", command=self.simpan_data)
        self.btn_simpan.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_ubah = ttk.Button(btn_frame, text="Ubah Data", command=self.ubah_data)
        self.btn_ubah.pack(side=tk.LEFT, padx=5)

        self.btn_hapus = ttk.Button(btn_frame, text="Hapus Data", command=self.hapus_data)
        self.btn_hapus.pack(side=tk.LEFT, padx=5)

        self.btn_bersihkan = ttk.Button(btn_frame, text="Bersihkan Formulir", command=self.bersihkan_form)
        self.btn_bersihkan.pack(side=tk.LEFT, padx=5)

        self.btn_refresh = ttk.Button(btn_frame, text="Refresh", command=self.muat_data)
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

        # ================= SEARCH BAR =================
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(search_frame, text="Cari Mahasiswa (Nama / NIM):").pack(side=tk.LEFT, padx=(0, 8))
        self.txt_cari = ttk.Entry(search_frame)
        self.txt_cari.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        # Pencarian real-time saat mengetik
        self.txt_cari.bind("<KeyRelease>", lambda event: self.cari_data())

        btn_cari = ttk.Button(search_frame, text="Cari", command=self.cari_data)
        btn_cari.pack(side=tk.LEFT, padx=2)

        btn_reset_cari = ttk.Button(search_frame, text="Reset", command=self.reset_pencarian)
        btn_reset_cari.pack(side=tk.LEFT, padx=2)

        # ================= TABEL DATA (TREEVIEW) =================
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "nama", "nim", "prodi", "angkatan", "alamat")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Konfigurasi Header
        self.tree.heading("id", text="ID")
        self.tree.heading("nama", text="Nama Lengkap")
        self.tree.heading("nim", text="NIM")
        self.tree.heading("prodi", text="Program Studi")
        self.tree.heading("angkatan", text="Angkatan")
        self.tree.heading("alamat", text="Alamat")

        # Konfigurasi Kolom
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("nama", width=180, anchor=tk.W)
        self.tree.column("nim", width=110, anchor=tk.CENTER)
        self.tree.column("prodi", width=140, anchor=tk.W)
        self.tree.column("angkatan", width=80, anchor=tk.CENTER)
        self.tree.column("alamat", width=250, anchor=tk.W)

        # Scrollbar Vertikal
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Event pemilihan baris Treeview
        self.tree.bind("<<TreeviewSelect>>", self.pada_baris_dipilih)

    def validasi_input(self):
        """
        Validasi input:
        - Nama, NIM, Prodi, Angkatan tidak boleh kosong.
        - Angkatan harus berupa angka bulat positif.
        """
        nama = self.txt_nama.get().strip()
        nim = self.txt_nim.get().strip()
        prodi = self.cmb_prodi.get().strip()
        angkatan_str = self.txt_angkatan.get().strip()
        alamat = self.txt_alamat.get().strip()

        if not nama or not nim or not prodi or not angkatan_str:
            messagebox.showwarning(
                "Peringatan Validasi",
                "Kolom Nama, NIM, Program Studi, dan Angkatan wajib diisi!"
            )
            return None

        if not angkatan_str.isdigit():
            messagebox.showwarning(
                "Peringatan Validasi",
                "Kolom Angkatan harus berupa angka tahun (contoh: 2024)!"
            )
            return None

        return {
            "nama": nama,
            "nim": nim,
            "prodi": prodi,
            "angkatan": int(angkatan_str),
            "alamat": alamat
        }

    def simpan_data(self):
        """Menyimpan data mahasiswa baru ke database."""
        data = self.validasi_input()
        if not data:
            return

        query = """
            INSERT INTO mahasiswa (nama, nim, prodi, alamat, angkatan)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            with koneksi() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (
                    data["nama"],
                    data["nim"],
                    data["prodi"],
                    data["alamat"],
                    data["angkatan"]
                ))
            messagebox.showinfo("Sukses", "Data mahasiswa berhasil disimpan!")
            self.bersihkan_form()
            self.muat_data()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Kesalahan Duplikasi",
                f"NIM '{data['nim']}' sudah terdaftar dalam sistem!\nSilakan gunakan NIM yang berbeda."
            )
        except Exception as e:
            messagebox.showerror("Kesalahan Database", f"Terjadi kesalahan saat menyimpan data:\n{e}")

    def ubah_data(self):
        """Memperbarui data mahasiswa yang dipilih."""
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data mahasiswa dari tabel yang ingin diubah terlebih dahulu!")
            return

        data = self.validasi_input()
        if not data:
            return

        query = """
            UPDATE mahasiswa
            SET nama = ?, nim = ?, prodi = ?, alamat = ?, angkatan = ?
            WHERE id = ?
        """
        try:
            with koneksi() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (
                    data["nama"],
                    data["nim"],
                    data["prodi"],
                    data["alamat"],
                    data["angkatan"],
                    self.selected_id
                ))
            messagebox.showinfo("Sukses", "Data mahasiswa berhasil diperbarui!")
            self.bersihkan_form()
            self.muat_data()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Kesalahan Duplikasi",
                f"NIM '{data['nim']}' sudah digunakan oleh mahasiswa lain!\nSilakan periksa kembali."
            )
        except Exception as e:
            messagebox.showerror("Kesalahan Database", f"Terjadi kesalahan saat mengubah data:\n{e}")

    def hapus_data(self):
        """Menghapus data mahasiswa yang dipilih dengan konfirmasi."""
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data mahasiswa dari tabel yang ingin dihapus terlebih dahulu!")
            return

        nama = self.txt_nama.get()
        nim = self.txt_nim.get()
        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus data mahasiswa:\n\nNama: {nama}\nNIM: {nim}?"
        )
        if not konfirmasi:
            return

        query = "DELETE FROM mahasiswa WHERE id = ?"
        try:
            with koneksi() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (self.selected_id,))
            messagebox.showinfo("Sukses", "Data mahasiswa berhasil dihapus!")
            self.bersihkan_form()
            self.muat_data()
        except Exception as e:
            messagebox.showerror("Kesalahan Database", f"Terjadi kesalahan saat menghapus data:\n{e}")

    def bersihkan_form(self):
        """Mengosongkan form input dan me-reset ID terpilih."""
        self.selected_id = None
        self.txt_nama.delete(0, tk.END)
        self.txt_nim.delete(0, tk.END)
        self.cmb_prodi.set("")
        self.txt_angkatan.delete(0, tk.END)
        self.txt_alamat.delete(0, tk.END)

        # Batalkan pemilihan di Treeview jika ada
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def muat_data(self, data_list=None):
        """
        Menampilkan data pada Treeview.
        Jika data_list diberikan, tampilkan data tersebut.
        Jika tidak, ambil seluruh data dari database.
        """
        # Bersihkan baris yang ada di tabel
        for item in self.tree.get_children():
            self.tree.delete(item)

        if data_list is None:
            query = "SELECT id, nama, nim, prodi, angkatan, alamat FROM mahasiswa ORDER BY id DESC"
            try:
                with koneksi() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    data_list = cursor.fetchall()
            except Exception as e:
                messagebox.showerror("Kesalahan Database", f"Gagal memuat data:\n{e}")
                return

        for row in data_list:
            # Ganti None dengan string kosong agar rapi
            row_clean = [col if col is not None else "" for col in row]
            self.tree.insert("", tk.END, values=row_clean)

    def cari_data(self):
        """Memfilter data berdasarkan pencarian Nama atau NIM menggunakan LIKE parameterized query."""
        kata_kunci = self.txt_cari.get().strip()
        if not kata_kunci:
            self.muat_data()
            return

        query = """
            SELECT id, nama, nim, prodi, angkatan, alamat
            FROM mahasiswa
            WHERE nama LIKE ? OR nim LIKE ?
            ORDER BY id DESC
        """
        parameter = f"%{kata_kunci}%"
        try:
            with koneksi() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (parameter, parameter))
                hasil = cursor.fetchall()
            self.muat_data(data_list=hasil)
        except Exception as e:
            messagebox.showerror("Kesalahan Pencarian", f"Terjadi kesalahan saat mencari data:\n{e}")

    def reset_pencarian(self):
        """Mengosongkan field pencarian dan menampilkan seluruh data."""
        self.txt_cari.delete(0, tk.END)
        self.muat_data()

    def pada_baris_dipilih(self, event):
        """
        Event handler saat baris pada Treeview diklik/dipilih.
        Mengisi otomatis formulir input dengan data baris yang dipilih.
        """
        selected_items = self.tree.selection()
        if not selected_items:
            return

        selected_item = selected_items[0]
        values = self.tree.item(selected_item, "values")
        if not values:
            return

        # values: (id, nama, nim, prodi, angkatan, alamat)
        self.selected_id = values[0]

        # Isi data ke input formulir
        self.txt_nama.delete(0, tk.END)
        self.txt_nama.insert(0, values[1])

        self.txt_nim.delete(0, tk.END)
        self.txt_nim.insert(0, values[2])

        self.cmb_prodi.set(values[3])

        self.txt_angkatan.delete(0, tk.END)
        self.txt_angkatan.insert(0, values[4])

        self.txt_alamat.delete(0, tk.END)
        self.txt_alamat.insert(0, values[5])


if __name__ == "__main__":
    # Inisialisasi tabel database terlebih dahulu
    inisialisasi_db()

    # Jalankan aplikasi GUI
    app = AplikasiMahasiswa()
    app.mainloop()
