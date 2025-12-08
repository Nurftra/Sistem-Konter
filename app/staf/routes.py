import functools
from flask import Blueprint, render_template, abort, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import Produk, TransaksiMasuk, TransaksiKeluar, RiwayatAktivitas
from app.admin.forms import IncomingProductForm, OutgoingProductForm # Reusing forms from admin

staf_bp = Blueprint('staf', __name__, url_prefix='/staf')

# Decorator to restrict access to staf and pending roles (and admin/superadmin for general staf pages)
def staf_required(f):
    @functools.wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Allow superadmin and admin to access staf pages too, if needed, but primarily for staf/pending
        if current_user.role not in ['staf', 'pending', 'admin', 'superadmin']: 
            flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'error')
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@staf_bp.route('/dashboard')
@staf_required
def dashboard():
    return render_template('staf/dashboard.html', title='Staf Dashboard')

@staf_bp.route('/products')
@staf_required
def list_products():
    products = Produk.query.order_by(Produk.nama).all()
    return render_template('staf/list_products.html', title='Daftar Produk', products=products)

@staf_bp.route('/incoming', methods=['GET', 'POST'])
@staf_required
def incoming_products():
    form = IncomingProductForm()
    form.product_id.choices = [(p.id, p.nama) for p in Produk.query.order_by(Produk.nama).all()]

    if form.validate_on_submit():
        product = Produk.query.get(form.product_id.data)
        if product:
            quantity = form.quantity.data
            product.stok += quantity
            
            transaction = TransaksiMasuk(
                produk_id=product.id,
                jumlah=quantity,
                user_id=current_user.id
            )
            db.session.add(transaction)

            activity = RiwayatAktivitas(
                user_id=current_user.id,
                aktivitas=f'[Staf] Input barang masuk: {quantity} unit {product.nama}'
            )
            db.session.add(activity)

            db.session.commit()
            flash(f'{quantity} unit {product.nama} berhasil ditambahkan ke stok.', 'message')
            return redirect(url_for('staf.incoming_products'))
        else:
            flash('Produk tidak ditemukan.', 'error')
    
    return render_template('staf/incoming_products.html', title='Input Barang Masuk', form=form)


@staf_bp.route('/outgoing', methods=['GET', 'POST'])
@staf_required
def outgoing_products():
    form = OutgoingProductForm()
    form.product_id.choices = [(p.id, p.nama) for p in Produk.query.order_by(Produk.nama).all()]

    if form.validate_on_submit():
        product = Produk.query.get(form.product_id.data)
        if product:
            quantity = form.quantity.data
            if product.stok >= quantity:
                product.stok -= quantity

                transaction = TransaksiKeluar(
                    produk_id=product.id,
                    jumlah=quantity,
                    user_id=current_user.id
                )
                db.session.add(transaction)

                activity = RiwayatAktivitas(
                    user_id=current_user.id,
                    aktivitas=f'[Staf] Input barang keluar: {quantity} unit {product.nama}'
                )
                db.session.add(activity)

                db.session.commit()
                flash(f'{quantity} unit {product.nama} berhasil dikeluarkan dari stok.', 'message')
                return redirect(url_for('staf.outgoing_products'))
            else:
                flash(f'Stok {product.nama} tidak mencukupi. Stok tersedia: {product.stok}.', 'error')
        else:
            flash('Produk tidak ditemukan.', 'error')
    
    return render_template('staf/outgoing_products.html', title='Input Barang Keluar', form=form)

@staf_bp.route('/my_activity')
@staf_required
def my_activity():
    activities = RiwayatAktivitas.query.filter_by(user_id=current_user.id).order_by(RiwayatAktivitas.timestamp.desc()).all()
    return render_template('staf/my_activity.html', title='Riwayat Aktivitas Pribadi', activities=activities)
