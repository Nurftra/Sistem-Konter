import functools
from flask import Blueprint, render_template, abort, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Produk, TransaksiMasuk, TransaksiKeluar, RiwayatAktivitas
from app.admin.forms import UserRoleForm, ProductForm, IncomingProductForm, OutgoingProductForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to restrict access to superadmin and admin roles
def admin_required(f):
    @functools.wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['superadmin', 'admin']:
            flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'error')
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_products = Produk.query.count()
    total_incoming_transactions = TransaksiMasuk.query.with_entities(db.func.sum(TransaksiMasuk.jumlah)).scalar() or 0
    total_outgoing_transactions = TransaksiKeluar.query.with_entities(db.func.sum(TransaksiKeluar.jumlah)).scalar() or 0

    return render_template('admin/dashboard.html',
                           title='Admin Dashboard',
                           total_users=total_users,
                           total_products=total_products,
                           total_incoming_transactions=total_incoming_transactions,
                           total_outgoing_transactions=total_outgoing_transactions)

@admin_bp.route('/users', methods=['GET', 'POST']) # Allow POST for form submission
@admin_required
def manage_users():
    users = User.query.all()
    form_instances = {} # Dictionary to hold a form instance for each user

    for user in users:
        form = UserRoleForm()
        form.role.data = user.role # Pre-populate with current role
        form_instances[user.id] = form

    if request.method == 'POST':
        user_id = request.form.get('user_id') # Get user_id from hidden field in form
        if user_id:
            user_to_update = User.query.get(int(user_id))
            if user_to_update:
                form = UserRoleForm(request.form) # Bind form data to specific form
                if form.validate_on_submit():
                    # Security checks for role changes
                    # If the target user is a Superadmin
                    if user_to_update.role == 'superadmin':
                        # Prevent changing another Superadmin's role (except self, handled below)
                        if user_to_update.id != current_user.id:
                            flash('Anda tidak memiliki izin untuk mengubah peran Superadmin lain.', 'error')
                            return redirect(url_for('admin.manage_users'))
                        # Prevent a Superadmin from demoting themselves
                        elif form.role.data != 'superadmin':
                            flash('Superadmin tidak dapat menurunkan perannya sendiri.', 'error')
                            return redirect(url_for('admin.manage_users'))
                        else: # Superadmin trying to set their own role to superadmin (no actual change)
                            flash(f'Peran pengguna {user_to_update.username} sudah Superadmin.', 'message')
                            return redirect(url_for('admin.manage_users'))
                    # If the target user is NOT a Superadmin
                    else:
                        # Prevent non-Superadmin from promoting to Superadmin
                        if form.role.data == 'superadmin' and current_user.role != 'superadmin':
                            flash('Hanya Superadmin yang dapat mengangkat pengguna ke peran Superadmin.', 'error')
                            return redirect(url_for('admin.manage_users'))

                        user_to_update.role = form.role.data
                        db.session.commit()
                        flash(f'Peran pengguna {user_to_update.username} berhasil diperbarui menjadi {user_to_update.role}.', 'message')
                        return redirect(url_for('admin.manage_users'))
                else:
                    # If form validation fails for a specific user, display errors
                    for field, errors in form.errors.items():
                        for error in errors:
                            flash(f'Error pada {field} untuk {user_to_update.username}: {error}', 'error')
            else:
                flash('Pengguna tidak ditemukan.', 'error')
        else:
            flash('ID pengguna tidak diberikan.', 'error')

    return render_template('admin/manage_users.html', title='Kelola Admin & Staf', users=users, form_instances=form_instances)

@admin_bp.route('/products', methods=['GET', 'POST'])
@admin_required
def manage_products():
    form = ProductForm()
    if form.validate_on_submit():
        product = Produk(
            nama=form.name.data,
            harga=int(form.price.data), # Convert to int
            stok=int(form.stock.data),   # Convert to int
            kategori=form.category.data,
            gambar=form.image.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Produk berhasil ditambahkan!', 'message')
        return redirect(url_for('admin.manage_products'))

    products = Produk.query.all()
    return render_template('admin/manage_products.html', title='Kelola Produk', products=products, form=form)

@admin_bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Produk.query.get_or_404(product_id)
    form = ProductForm()
    if form.validate_on_submit():
        product.nama = form.name.data
        product.harga = int(form.price.data)
        product.stok = int(form.stock.data)
        product.kategori = form.category.data
        product.gambar = form.image.data
        db.session.commit()
        flash('Produk berhasil diperbarui!', 'message')
        return redirect(url_for('admin.manage_products'))
    elif request.method == 'GET':
        form.name.data = product.nama
        form.price.data = product.harga
        form.stock.data = product.stok
        form.kategori.data = product.kategori
        form.gambar.data = product.gambar
    return render_template('admin/edit_product.html', title='Edit Produk', form=form, product_id=product.id)


@admin_bp.route('/product/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Produk.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Produk berhasil dihapus!', 'message')
    return redirect(url_for('admin.manage_products'))


@admin_bp.route('/incoming', methods=['GET', 'POST'])
@admin_required
def incoming_products():
    form = IncomingProductForm()
    # Populate product choices dynamically
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
                aktivitas=f'Input barang masuk: {quantity} unit {product.nama}'
            )
            db.session.add(activity)

            db.session.commit()
            flash(f'{quantity} unit {product.nama} berhasil ditambahkan ke stok.', 'message')
            return redirect(url_for('admin.incoming_products'))
        else:
            flash('Produk tidak ditemukan.', 'error')
    
    return render_template('admin/incoming_products.html', title='Input Barang Masuk', form=form)

@admin_bp.route('/outgoing', methods=['GET', 'POST'])
@admin_required
def outgoing_products():
    form = OutgoingProductForm()
    # Populate product choices dynamically
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
                    aktivitas=f'Input barang keluar: {quantity} unit {product.nama}'
                )
                db.session.add(activity)

                db.session.commit()
                flash(f'{quantity} unit {product.nama} berhasil dikeluarkan dari stok.', 'message')
                return redirect(url_for('admin.outgoing_products'))
            else:
                flash(f'Stok {product.nama} tidak mencukupi. Stok tersedia: {product.stok}.', 'error')
        else:
            flash('Produk tidak ditemukan.', 'error')
    
    return render_template('admin/outgoing_products.html', title='Input Barang Keluar', form=form)


@admin_bp.route('/transactions')
@admin_required
def view_transactions():
    incoming_transactions = TransaksiMasuk.query.order_by(TransaksiMasuk.tanggal_masuk.desc()).all()
    outgoing_transactions = TransaksiKeluar.query.order_by(TransaksiKeluar.tanggal_keluar.desc()).all()
    return render_template('admin/view_transactions.html',
                           title='Lihat Semua Transaksi',
                           incoming_transactions=incoming_transactions,
                           outgoing_transactions=outgoing_transactions)

@admin_bp.route('/activity_log')
@admin_required
def activity_log():
    activities = RiwayatAktivitas.query.order_by(RiwayatAktivitas.timestamp.desc()).all()
    return render_template('admin/activity_log.html', title='Console Aktivitas', activities=activities)

@admin_bp.route('/my_activity')
@admin_required
def my_activity():
    activities = RiwayatAktivitas.query.filter_by(user_id=current_user.id).order_by(RiwayatAktivitas.timestamp.desc()).all()
    return render_template('admin/my_activity.html', title='Riwayat Aktivitas Pribadi', activities=activities)
