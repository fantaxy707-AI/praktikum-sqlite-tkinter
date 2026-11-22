\# Aplikasi Data Mahasiswa (Python Tkinter \& SQLite)



Aplikasi desktop sederhana pakai Python (Tkinter) dan SQLite buat nyimpan, nampilin, ngubah, dan ngehapus data mahasiswa secara lokal. Dibuat untuk memenuhi tugas praktikum Sesi #12 Pemrograman Berorientasi Objek.



\## Fitur Utama



\* \*\*CRUD Data Mahasiswa:\*\* Tambah, tampil, ubah, dan hapus data mahasiswa.

\* \*\*Pencarian Data:\*\* Cari data mahasiswa berdasarkan Nama atau NIM.

\* \*\*Validasi \& Keamanan Dasar:\*\*

&#x20; \* Cek kolom wajib (`Nama`, `NIM`, `Program Studi`, `Angkatan`) biar nggak kosong dan pastiin `Angkatan` diisi angka.

&#x20; \* Cegah `NIM` kembar pakai penanganan error `sqlite3.IntegrityError`.

&#x20; \* Pakai placeholder `?` di semua query SQL biar aman dari SQL Injection.

\* \*\*Koneksi Database Rapi:\*\* Pakai `@contextmanager` supaya koneksi otomatis di-commit kalau sukses, di-rollback kalau error, dan selalu ditutup setelah selesai.



\## Cara Kerja Singkat



1\. \*\*Bikin Database Otomatis:\*\* Pas aplikasi dibuka, file `mahasiswa.db` dan tabel `mahasiswa` langsung dibikin otomatis kalau belum ada.

2\. \*\*Simpan \& Validasi:\*\* Data yang diinput di form dicek dulu kelengkapannya, baru disimpan ke SQLite dan langsung ditampilin di tabel.

3\. \*\*Edit \& Hapus:\*\* Klik salah satu baris di tabel, datanya otomatis masuk ke form buat diubah atau dihapus.

4\. \*\*Data Permanen:\*\* Karena disimpan di file `mahasiswa.db`, datanya nggak bakal hilang meskipun aplikasi ditutup.



\## Struktur Tabel (`mahasiswa`)



Database disimpan di file \*\*`mahasiswa.db`\*\* dengan susunan kolom:



| Kolom | Tipe Data | Keterangan |

| :--- | :--- | :--- |

| `id` | `INTEGER` | Primary Key, Auto Increment |

| `nama` | `TEXT` | Wajib diisi |

| `nim` | `TEXT` | Wajib diisi, tidak boleh kembar (`UNIQUE`) |

| `prodi` | `TEXT` | Wajib diisi |

| `angkatan` | `INTEGER` | Wajib diisi (angka tahun) |

| `alamat` | `TEXT` | Opsional |



\## Cara Menjalankan



1\. Pastikan \*\*Python 3\*\* sudah terinstal di komputer.

2\. Unduh file `aplikasi\_mahasiswa.py` (atau download repository ini dalam format ZIP lalu ekstrak).

3\. Buka terminal atau command prompt di dalam folder tempat file tersebut disimpan.

4\. Jalankan perintah berikut:

&#x20;  ```bash

&#x20;  python aplikasi\_mahasiswa.py

