from datetime import datetime
from app import db, bcrypt
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), default='pending', nullable=False) # superadmin, admin, staf, pending
    otp_secret = db.Column(db.String(32), nullable=True) # Increased length to 32 for pyotp secrets
    otp_enabled = db.Column(db.Boolean, default=False) # Flag to enable/disable 2FA
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    lockout_until = db.Column(db.DateTime, nullable=True)

    transaksi_masuk = db.relationship('TransaksiMasuk', backref='user', lazy='dynamic')
    transaksi_keluar = db.relationship('TransaksiKeluar', backref='user', lazy='dynamic')
    riwayat_aktivitas = db.relationship('RiwayatAktivitas', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class Produk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(128), index=True, nullable=False)
    harga = db.Column(db.Integer, nullable=False)
    stok = db.Column(db.Integer, default=0, nullable=False)
    kategori = db.Column(db.String(64), nullable=True) # Contoh: HP, Aksesoris
    gambar = db.Column(db.String(128), nullable=True) # Path atau URL gambar

    transaksi_masuk = db.relationship('TransaksiMasuk', backref='produk', lazy='dynamic')
    transaksi_keluar = db.relationship('TransaksiKeluar', backref='produk', lazy='dynamic')

    def __repr__(self):
        return f'<Produk {self.nama} (Stok: {self.stok})>'

class TransaksiMasuk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produk_id = db.Column(db.Integer, db.ForeignKey('produk.id'), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    tanggal_masuk = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<TransaksiMasuk Produk: {self.produk_id}, Jumlah: {self.jumlah}, Tanggal: {self.tanggal_masuk}>'

class TransaksiKeluar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produk_id = db.Column(db.Integer, db.ForeignKey('produk.id'), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    tanggal_keluar = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<TransaksiKeluar Produk: {self.produk_id}, Jumlah: {self.jumlah}, Tanggal: {self.tanggal_keluar}>'

class RiwayatAktivitas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    aktivitas = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<RiwayatAktivitas User: {self.user_id}, Aktivitas: {self.aktivitas}, Waktu: {self.timestamp}>'
