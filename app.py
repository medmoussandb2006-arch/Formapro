from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import database as db

app = Flask(__name__)
app.secret_key = 'formapro_secret_key_mauritanie_2025'

# ── Auth helpers ──────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') not in roles:
                flash('Accès non autorisé.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ── Auth routes ───────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = db.get_user_by_email(email)
        if user and user['password'] == db.hash_password(password) and user['actif']:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['nom'] = f"{user['prenom']} {user['nom']}"
            session['email'] = user['email']
            flash(f"Bienvenue, {session['nom']} !", 'success')
            return redirect(url_for('dashboard'))
        flash('Email ou mot de passe incorrect.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'formateur':
        return redirect(url_for('formateur_dashboard'))
    else:
        return redirect(url_for('etudiant_dashboard'))

# ══════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════
@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    stats = db.get_dashboard_stats()
    sessions_list = db.get_all_sessions()[:5]
    return render_template('admin/dashboard.html', stats=stats, sessions=sessions_list)

# ── Etudiants ──────────────────────────────────────────────────
@app.route('/admin/etudiants')
@login_required
@role_required('admin')
def admin_etudiants():
    etudiants = db.get_all_users('etudiant')
    return render_template('admin/etudiants.html', etudiants=etudiants)

@app.route('/admin/etudiants/ajouter', methods=['POST'])
@login_required
@role_required('admin')
def admin_ajouter_etudiant():
    nom = request.form.get('nom', '').strip()
    prenom = request.form.get('prenom', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    telephone = request.form.get('telephone', '').strip()
    if db.create_user(nom, prenom, email, password, 'etudiant', telephone):
        flash('Étudiant ajouté avec succès.', 'success')
    else:
        flash('Cet email est déjà utilisé.', 'danger')
    return redirect(url_for('admin_etudiants'))

@app.route('/admin/etudiants/modifier/<int:uid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_modifier_etudiant(uid):
    nom = request.form.get('nom', '').strip()
    prenom = request.form.get('prenom', '').strip()
    email = request.form.get('email', '').strip()
    telephone = request.form.get('telephone', '').strip()
    actif = 1 if request.form.get('actif') else 0
    db.update_user(uid, nom, prenom, email, telephone, actif)
    flash('Étudiant modifié.', 'success')
    return redirect(url_for('admin_etudiants'))

@app.route('/admin/etudiants/supprimer/<int:uid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_supprimer_etudiant(uid):
    db.delete_user(uid)
    flash('Étudiant supprimé.', 'success')
    return redirect(url_for('admin_etudiants'))

# ── Formateurs ─────────────────────────────────────────────────
@app.route('/admin/formateurs')
@login_required
@role_required('admin')
def admin_formateurs():
    formateurs = db.get_all_users('formateur')
    return render_template('admin/formateurs.html', formateurs=formateurs)

@app.route('/admin/formateurs/ajouter', methods=['POST'])
@login_required
@role_required('admin')
def admin_ajouter_formateur():
    nom = request.form.get('nom', '').strip()
    prenom = request.form.get('prenom', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    telephone = request.form.get('telephone', '').strip()
    if db.create_user(nom, prenom, email, password, 'formateur', telephone):
        flash('Formateur ajouté avec succès.', 'success')
    else:
        flash('Cet email est déjà utilisé.', 'danger')
    return redirect(url_for('admin_formateurs'))

@app.route('/admin/formateurs/modifier/<int:uid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_modifier_formateur(uid):
    nom = request.form.get('nom', '').strip()
    prenom = request.form.get('prenom', '').strip()
    email = request.form.get('email', '').strip()
    telephone = request.form.get('telephone', '').strip()
    actif = 1 if request.form.get('actif') else 0
    db.update_user(uid, nom, prenom, email, telephone, actif)
    flash('Formateur modifié.', 'success')
    return redirect(url_for('admin_formateurs'))

@app.route('/admin/formateurs/supprimer/<int:uid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_supprimer_formateur(uid):
    db.delete_user(uid)
    flash('Formateur supprimé.', 'success')
    return redirect(url_for('admin_formateurs'))

# ── Formations ─────────────────────────────────────────────────
@app.route('/admin/formations')
@login_required
@role_required('admin')
def admin_formations():
    formations = db.get_all_formations()
    return render_template('admin/formations.html', formations=formations)

@app.route('/admin/formations/ajouter', methods=['POST'])
@login_required
@role_required('admin')
def admin_ajouter_formation():
    titre = request.form.get('titre', '').strip()
    description = request.form.get('description', '').strip()
    duree = int(request.form.get('duree_heures', 0))
    niveau = request.form.get('niveau', 'Débutant')
    categorie = request.form.get('categorie', '').strip()
    prix = float(request.form.get('prix', 0))
    db.create_formation(titre, description, duree, niveau, categorie, prix)
    flash('Formation ajoutée.', 'success')
    return redirect(url_for('admin_formations'))

@app.route('/admin/formations/modifier/<int:fid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_modifier_formation(fid):
    titre = request.form.get('titre', '').strip()
    description = request.form.get('description', '').strip()
    duree = int(request.form.get('duree_heures', 0))
    niveau = request.form.get('niveau', 'Débutant')
    categorie = request.form.get('categorie', '').strip()
    prix = float(request.form.get('prix', 0))
    actif = 1 if request.form.get('actif') else 0
    db.update_formation(fid, titre, description, duree, niveau, categorie, prix, actif)
    flash('Formation modifiée.', 'success')
    return redirect(url_for('admin_formations'))

@app.route('/admin/formations/supprimer/<int:fid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_supprimer_formation(fid):
    db.delete_formation(fid)
    flash('Formation supprimée.', 'success')
    return redirect(url_for('admin_formations'))

# ── Sessions ───────────────────────────────────────────────────
@app.route('/admin/sessions')
@login_required
@role_required('admin')
def admin_sessions():
    sessions_list = db.get_all_sessions()
    formations = db.get_all_formations(actif_only=True)
    formateurs = db.get_all_users('formateur')
    return render_template('admin/sessions.html', sessions=sessions_list, formations=formations, formateurs=formateurs)

@app.route('/admin/sessions/ajouter', methods=['POST'])
@login_required
@role_required('admin')
def admin_ajouter_session():
    formation_id = int(request.form.get('formation_id'))
    formateur_id = int(request.form.get('formateur_id'))
    date_debut = request.form.get('date_debut')
    date_fin = request.form.get('date_fin')
    lieu = request.form.get('lieu', '').strip()
    capacite = int(request.form.get('capacite_max', 20))
    db.create_session(formation_id, formateur_id, date_debut, date_fin, lieu, capacite)
    flash('Session créée.', 'success')
    return redirect(url_for('admin_sessions'))

@app.route('/admin/sessions/modifier/<int:sid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_modifier_session(sid):
    formation_id = int(request.form.get('formation_id'))
    formateur_id = int(request.form.get('formateur_id'))
    date_debut = request.form.get('date_debut')
    date_fin = request.form.get('date_fin')
    lieu = request.form.get('lieu', '').strip()
    capacite = int(request.form.get('capacite_max', 20))
    statut = request.form.get('statut', 'planifiee')
    db.update_session(sid, formation_id, formateur_id, date_debut, date_fin, lieu, capacite, statut)
    flash('Session modifiée.', 'success')
    return redirect(url_for('admin_sessions'))

@app.route('/admin/sessions/supprimer/<int:sid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_supprimer_session(sid):
    db.delete_session(sid)
    flash('Session supprimée.', 'success')
    return redirect(url_for('admin_sessions'))

# ── Participations ─────────────────────────────────────────────
@app.route('/admin/participations')
@login_required
@role_required('admin')
def admin_participations():
    participations = db.get_all_participations()
    etudiants = db.get_all_users('etudiant')
    sessions_list = db.get_all_sessions()
    return render_template('admin/participations.html',
                           participations=participations,
                           etudiants=etudiants,
                           sessions=sessions_list)

@app.route('/admin/participations/ajouter', methods=['POST'])
@login_required
@role_required('admin')
def admin_ajouter_participation():
    etudiant_id = int(request.form.get('etudiant_id'))
    session_id = int(request.form.get('session_id'))
    if db.inscrire_etudiant(etudiant_id, session_id):
        flash('Inscription ajoutée.', 'success')
    else:
        flash('Cet étudiant est déjà inscrit à cette session.', 'warning')
    return redirect(url_for('admin_participations'))

@app.route('/admin/participations/modifier/<int:pid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_modifier_participation(pid):
    statut = request.form.get('statut', 'inscrit')
    note = request.form.get('note') or None
    commentaire = request.form.get('commentaire', '').strip()
    if note:
        note = float(note)
    db.update_participation(pid, statut, note, commentaire)
    flash('Participation mise à jour.', 'success')
    return redirect(url_for('admin_participations'))

@app.route('/admin/participations/supprimer/<int:pid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_supprimer_participation(pid):
    db.delete_participation(pid)
    flash('Participation supprimée.', 'success')
    return redirect(url_for('admin_participations'))

# ── Certifications ─────────────────────────────────────────────
@app.route('/admin/certifications')
@login_required
@role_required('admin')
def admin_certifications():
    certifications = db.get_all_certifications()
    etudiants = db.get_all_users('etudiant')
    formations = db.get_all_formations()
    sessions_list = db.get_all_sessions()
    return render_template('admin/certifications.html',
                           certifications=certifications,
                           etudiants=etudiants,
                           formations=formations,
                           sessions=sessions_list)

@app.route('/admin/certifications/ajouter', methods=['POST'])
@login_required
@role_required('admin')
def admin_ajouter_certification():
    etudiant_id = int(request.form.get('etudiant_id'))
    formation_id = int(request.form.get('formation_id'))
    session_id = int(request.form.get('session_id'))
    mention = request.form.get('mention', 'Satisfaisant')
    note = float(request.form.get('note_finale', 0))
    numero = db.create_certification(etudiant_id, formation_id, session_id, mention, note)
    flash(f'Certification {numero} créée.', 'success')
    return redirect(url_for('admin_certifications'))

@app.route('/admin/certifications/supprimer/<int:cid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_supprimer_certification(cid):
    db.delete_certification(cid)
    flash('Certification supprimée.', 'success')
    return redirect(url_for('admin_certifications'))

# ══════════════════════════════════════════════════════════════
# ETUDIANT
# ══════════════════════════════════════════════════════════════
@app.route('/etudiant/dashboard')
@login_required
@role_required('etudiant')
def etudiant_dashboard():
    uid = session['user_id']
    mes_sessions = db.get_sessions_by_etudiant(uid)
    mes_certifs = db.get_certifications_by_etudiant(uid)
    return render_template('etudiant/dashboard.html', sessions=mes_sessions, certifications=mes_certifs)

@app.route('/etudiant/sessions')
@login_required
@role_required('etudiant')
def etudiant_sessions():
    uid = session['user_id']
    mes_sessions = db.get_sessions_by_etudiant(uid)
    return render_template('etudiant/sessions.html', sessions=mes_sessions)

@app.route('/etudiant/catalogue')
@login_required
@role_required('etudiant')
def etudiant_catalogue():
    uid = session['user_id']
    sessions_dispo = db.get_available_sessions(uid)
    return render_template('etudiant/catalogue.html', sessions=sessions_dispo)

@app.route('/etudiant/inscrire/<int:session_id>', methods=['POST'])
@login_required
@role_required('etudiant')
def etudiant_inscrire(session_id):
    uid = session['user_id']
    if db.inscrire_etudiant(uid, session_id):
        flash('Inscription réussie !', 'success')
    else:
        flash('Vous êtes déjà inscrit à cette session.', 'warning')
    return redirect(url_for('etudiant_catalogue'))

@app.route('/etudiant/certifications')
@login_required
@role_required('etudiant')
def etudiant_certifications():
    uid = session['user_id']
    certifs = db.get_certifications_by_etudiant(uid)
    return render_template('etudiant/certifications.html', certifications=certifs)

# ══════════════════════════════════════════════════════════════
# FORMATEUR
# ══════════════════════════════════════════════════════════════
@app.route('/formateur/dashboard')
@login_required
@role_required('formateur')
def formateur_dashboard():
    uid = session['user_id']
    mes_sessions = db.get_sessions_by_formateur(uid)
    return render_template('formateur/dashboard.html', sessions=mes_sessions)

@app.route('/formateur/sessions')
@login_required
@role_required('formateur')
def formateur_sessions():
    uid = session['user_id']
    mes_sessions = db.get_sessions_by_formateur(uid)
    return render_template('formateur/sessions.html', sessions=mes_sessions)

@app.route('/formateur/sessions/<int:sid>/etudiants')
@login_required
@role_required('formateur')
def formateur_etudiants(sid):
    sess = db.get_session_by_id(sid)
    participants = db.get_participations_by_session(sid)
    return render_template('formateur/etudiants.html', session=sess, participants=participants)

@app.route('/formateur/sessions/<int:sid>/noter/<int:pid>', methods=['POST'])
@login_required
@role_required('formateur')
def formateur_noter(sid, pid):
    statut = request.form.get('statut', 'present')
    note = request.form.get('note') or None
    commentaire = request.form.get('commentaire', '').strip()
    if note:
        note = float(note)
    db.update_participation(pid, statut, note, commentaire)
    flash('Note enregistrée.', 'success')
    return redirect(url_for('formateur_etudiants', sid=sid))

@app.route('/formateur/certifications')
@login_required
@role_required('formateur')
def formateur_certifications():
    uid = session['user_id']
    mes_sessions = db.get_sessions_by_formateur(uid)
    session_ids = [s['id'] for s in mes_sessions]
    all_certifs = db.get_all_certifications()
    certifs = [c for c in all_certifs if c['session_id'] in session_ids]
    return render_template('formateur/certifications.html', certifications=certifs)

# ── Certificat public ──────────────────────────────────────────
@app.route('/certificat/<numero>')
def certificat(numero):
    certif = db.get_certification_by_numero(numero)
    if not certif:
        flash('Certificat introuvable.', 'danger')
        return redirect(url_for('login'))
    return render_template('certificat.html', certif=certif)

@app.route('/certificat/imprimer/<int:cid>')
@login_required
def imprimer_certificat(cid):
    certif = db.get_certification_by_id(cid)
    if not certif:
        flash('Certificat introuvable.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('certificat.html', certif=certif, print_mode=True)

# ── Run ────────────────────────────────────────────────────────
if __name__ == '__main__':
    db.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
