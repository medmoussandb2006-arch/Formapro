import sqlite3
import hashlib
import os
from datetime import datetime

DATABASE = 'formapro.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','etudiant','formateur')),
            telephone TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actif INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS formations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            description TEXT,
            duree_heures INTEGER NOT NULL,
            niveau TEXT DEFAULT 'Débutant',
            categorie TEXT,
            prix REAL DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actif INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            formation_id INTEGER NOT NULL,
            formateur_id INTEGER NOT NULL,
            date_debut DATE NOT NULL,
            date_fin DATE NOT NULL,
            lieu TEXT,
            capacite_max INTEGER DEFAULT 20,
            statut TEXT DEFAULT 'planifiee' CHECK(statut IN ('planifiee','en_cours','terminee','annulee')),
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (formation_id) REFERENCES formations(id),
            FOREIGN KEY (formateur_id) REFERENCES utilisateurs(id)
        );

        CREATE TABLE IF NOT EXISTS participations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'inscrit' CHECK(statut IN ('inscrit','present','absent','abandonne')),
            note REAL,
            commentaire TEXT,
            UNIQUE(etudiant_id, session_id),
            FOREIGN KEY (etudiant_id) REFERENCES utilisateurs(id),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id INTEGER NOT NULL,
            formation_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            numero_certificat TEXT UNIQUE NOT NULL,
            date_emission DATE NOT NULL,
            date_expiration DATE,
            mention TEXT DEFAULT 'Satisfaisant',
            note_finale REAL,
            valide INTEGER DEFAULT 1,
            FOREIGN KEY (etudiant_id) REFERENCES utilisateurs(id),
            FOREIGN KEY (formation_id) REFERENCES formations(id),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
    ''')

    # Seed admin if not exists
    existing = c.execute("SELECT id FROM utilisateurs WHERE role='admin'").fetchone()
    if not existing:
        c.execute('''INSERT INTO utilisateurs (nom, prenom, email, password, role, telephone)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  ('Admin', 'FormaPro', 'admin@formapro.mr', hash_password('admin123'), 'admin', '+222 00 00 00 00'))

        # Sample formateurs
        c.execute('''INSERT INTO utilisateurs (nom, prenom, email, password, role, telephone)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  ('Ould Mohamed', 'Abdallah', 'formateur@formapro.mr', hash_password('form123'), 'formateur', '+222 22 22 22 22'))

        # Sample etudiants
        c.execute('''INSERT INTO utilisateurs (nom, prenom, email, password, role, telephone)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  ('Sidi', 'Ahmed', 'etudiant@formapro.mr', hash_password('etu123'), 'etudiant', '+222 33 33 33 33'))

        # Sample formations
        c.execute('''INSERT INTO formations (titre, description, duree_heures, niveau, categorie, prix)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  ('Python & Data Science', 'Apprenez Python et l\'analyse de données', 40, 'Débutant', 'Informatique', 15000))
        c.execute('''INSERT INTO formations (titre, description, duree_heures, niveau, categorie, prix)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  ('Gestion de Projet', 'Méthodes agiles et traditionnelles', 24, 'Intermédiaire', 'Management', 12000))
        c.execute('''INSERT INTO formations (titre, description, duree_heures, niveau, categorie, prix)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  ('Marketing Digital', 'Stratégies marketing en ligne', 32, 'Débutant', 'Marketing', 10000))

        # Sample session
        c.execute('''INSERT INTO sessions (formation_id, formateur_id, date_debut, date_fin, lieu, capacite_max, statut)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (1, 2, '2025-01-15', '2025-03-15', 'Salle A - Nouakchott', 15, 'en_cours'))

        c.execute('''INSERT INTO sessions (formation_id, formateur_id, date_debut, date_fin, lieu, capacite_max, statut)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (2, 2, '2025-02-01', '2025-02-28', 'Salle B - Nouakchott', 20, 'planifiee'))

        # Sample participation
        c.execute('''INSERT INTO participations (etudiant_id, session_id, statut, note)
                     VALUES (?, ?, ?, ?)''', (3, 1, 'present', 16.5))

        # Sample certification
        c.execute('''INSERT INTO certifications (etudiant_id, formation_id, session_id, numero_certificat, date_emission, mention, note_finale)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (3, 1, 1, 'FP-2025-001', '2025-03-15', 'Bien', 16.5))

    conn.commit()
    conn.close()

# ── Utilisateurs ──────────────────────────────────────────────
def get_all_users(role=None):
    conn = get_db()
    if role:
        rows = conn.execute("SELECT * FROM utilisateurs WHERE role=? ORDER BY nom", (role,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM utilisateurs ORDER BY role, nom").fetchall()
    conn.close()
    return rows

def get_user_by_id(uid):
    conn = get_db()
    row = conn.execute("SELECT * FROM utilisateurs WHERE id=?", (uid,)).fetchone()
    conn.close()
    return row

def get_user_by_email(email):
    conn = get_db()
    row = conn.execute("SELECT * FROM utilisateurs WHERE email=?", (email,)).fetchone()
    conn.close()
    return row

def create_user(nom, prenom, email, password, role, telephone=''):
    conn = get_db()
    try:
        conn.execute('''INSERT INTO utilisateurs (nom, prenom, email, password, role, telephone)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (nom, prenom, email, hash_password(password), role, telephone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_user(uid, nom, prenom, email, telephone, actif):
    conn = get_db()
    conn.execute('''UPDATE utilisateurs SET nom=?, prenom=?, email=?, telephone=?, actif=? WHERE id=?''',
                 (nom, prenom, email, telephone, actif, uid))
    conn.commit()
    conn.close()

def delete_user(uid):
    conn = get_db()
    conn.execute("DELETE FROM utilisateurs WHERE id=?", (uid,))
    conn.commit()
    conn.close()

# ── Formations ────────────────────────────────────────────────
def get_all_formations(actif_only=False):
    conn = get_db()
    if actif_only:
        rows = conn.execute("SELECT * FROM formations WHERE actif=1 ORDER BY titre").fetchall()
    else:
        rows = conn.execute("SELECT * FROM formations ORDER BY titre").fetchall()
    conn.close()
    return rows

def get_formation_by_id(fid):
    conn = get_db()
    row = conn.execute("SELECT * FROM formations WHERE id=?", (fid,)).fetchone()
    conn.close()
    return row

def create_formation(titre, description, duree_heures, niveau, categorie, prix):
    conn = get_db()
    conn.execute('''INSERT INTO formations (titre, description, duree_heures, niveau, categorie, prix)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (titre, description, duree_heures, niveau, categorie, prix))
    conn.commit()
    conn.close()

def update_formation(fid, titre, description, duree_heures, niveau, categorie, prix, actif):
    conn = get_db()
    conn.execute('''UPDATE formations SET titre=?, description=?, duree_heures=?, niveau=?, categorie=?, prix=?, actif=?
                    WHERE id=?''', (titre, description, duree_heures, niveau, categorie, prix, actif, fid))
    conn.commit()
    conn.close()

def delete_formation(fid):
    conn = get_db()
    conn.execute("DELETE FROM formations WHERE id=?", (fid,))
    conn.commit()
    conn.close()

# ── Sessions ──────────────────────────────────────────────────
def get_all_sessions():
    conn = get_db()
    rows = conn.execute('''
        SELECT s.*, f.titre as formation_titre, f.duree_heures,
               u.nom || ' ' || u.prenom as formateur_nom,
               (SELECT COUNT(*) FROM participations p WHERE p.session_id = s.id) as nb_inscrits
        FROM sessions s
        JOIN formations f ON s.formation_id = f.id
        JOIN utilisateurs u ON s.formateur_id = u.id
        ORDER BY s.date_debut DESC
    ''').fetchall()
    conn.close()
    return rows

def get_session_by_id(sid):
    conn = get_db()
    row = conn.execute('''
        SELECT s.*, f.titre as formation_titre, f.duree_heures, f.description as formation_desc,
               u.nom || ' ' || u.prenom as formateur_nom
        FROM sessions s
        JOIN formations f ON s.formation_id = f.id
        JOIN utilisateurs u ON s.formateur_id = u.id
        WHERE s.id=?
    ''', (sid,)).fetchone()
    conn.close()
    return row

def get_sessions_by_formateur(formateur_id):
    conn = get_db()
    rows = conn.execute('''
        SELECT s.*, f.titre as formation_titre,
               (SELECT COUNT(*) FROM participations p WHERE p.session_id = s.id) as nb_inscrits
        FROM sessions s
        JOIN formations f ON s.formation_id = f.id
        WHERE s.formateur_id=?
        ORDER BY s.date_debut DESC
    ''', (formateur_id,)).fetchall()
    conn.close()
    return rows

def get_sessions_by_etudiant(etudiant_id):
    conn = get_db()
    rows = conn.execute('''
        SELECT s.*, f.titre as formation_titre, u.nom || ' ' || u.prenom as formateur_nom,
               p.statut as participation_statut, p.note
        FROM sessions s
        JOIN formations f ON s.formation_id = f.id
        JOIN utilisateurs u ON s.formateur_id = u.id
        JOIN participations p ON p.session_id = s.id AND p.etudiant_id=?
        ORDER BY s.date_debut DESC
    ''', (etudiant_id,)).fetchall()
    conn.close()
    return rows

def get_available_sessions(etudiant_id):
    conn = get_db()
    rows = conn.execute('''
        SELECT s.*, f.titre as formation_titre, f.description as formation_desc,
               u.nom || ' ' || u.prenom as formateur_nom,
               (SELECT COUNT(*) FROM participations p WHERE p.session_id = s.id) as nb_inscrits,
               CASE WHEN EXISTS(SELECT 1 FROM participations p WHERE p.session_id=s.id AND p.etudiant_id=?) THEN 1 ELSE 0 END as deja_inscrit
        FROM sessions s
        JOIN formations f ON s.formation_id = f.id
        JOIN utilisateurs u ON s.formateur_id = u.id
        WHERE s.statut IN ('planifiee','en_cours')
        ORDER BY s.date_debut
    ''', (etudiant_id,)).fetchall()
    conn.close()
    return rows

def create_session(formation_id, formateur_id, date_debut, date_fin, lieu, capacite_max):
    conn = get_db()
    conn.execute('''INSERT INTO sessions (formation_id, formateur_id, date_debut, date_fin, lieu, capacite_max)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (formation_id, formateur_id, date_debut, date_fin, lieu, capacite_max))
    conn.commit()
    conn.close()

def update_session(sid, formation_id, formateur_id, date_debut, date_fin, lieu, capacite_max, statut):
    conn = get_db()
    conn.execute('''UPDATE sessions SET formation_id=?, formateur_id=?, date_debut=?, date_fin=?,
                    lieu=?, capacite_max=?, statut=? WHERE id=?''',
                 (formation_id, formateur_id, date_debut, date_fin, lieu, capacite_max, statut, sid))
    conn.commit()
    conn.close()

def delete_session(sid):
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE id=?", (sid,))
    conn.commit()
    conn.close()

# ── Participations ────────────────────────────────────────────
def get_all_participations():
    conn = get_db()
    rows = conn.execute('''
        SELECT p.*, u.nom || ' ' || u.prenom as etudiant_nom, u.email as etudiant_email,
               f.titre as formation_titre, s.date_debut, s.date_fin
        FROM participations p
        JOIN utilisateurs u ON p.etudiant_id = u.id
        JOIN sessions s ON p.session_id = s.id
        JOIN formations f ON s.formation_id = f.id
        ORDER BY p.date_inscription DESC
    ''').fetchall()
    conn.close()
    return rows

def get_participations_by_session(session_id):
    conn = get_db()
    rows = conn.execute('''
        SELECT p.*, u.nom || ' ' || u.prenom as etudiant_nom, u.email as etudiant_email, u.telephone
        FROM participations p
        JOIN utilisateurs u ON p.etudiant_id = u.id
        WHERE p.session_id=?
        ORDER BY u.nom
    ''', (session_id,)).fetchall()
    conn.close()
    return rows

def inscrire_etudiant(etudiant_id, session_id):
    conn = get_db()
    try:
        conn.execute('''INSERT INTO participations (etudiant_id, session_id) VALUES (?, ?)''',
                     (etudiant_id, session_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_participation(pid, statut, note, commentaire):
    conn = get_db()
    conn.execute('''UPDATE participations SET statut=?, note=?, commentaire=? WHERE id=?''',
                 (statut, note, commentaire, pid))
    conn.commit()
    conn.close()

def delete_participation(pid):
    conn = get_db()
    conn.execute("DELETE FROM participations WHERE id=?", (pid,))
    conn.commit()
    conn.close()

# ── Certifications ────────────────────────────────────────────
def get_all_certifications():
    conn = get_db()
    rows = conn.execute('''
        SELECT c.*, u.nom || ' ' || u.prenom as etudiant_nom, u.email as etudiant_email,
               f.titre as formation_titre
        FROM certifications c
        JOIN utilisateurs u ON c.etudiant_id = u.id
        JOIN formations f ON c.formation_id = f.id
        ORDER BY c.date_emission DESC
    ''').fetchall()
    conn.close()
    return rows

def get_certifications_by_etudiant(etudiant_id):
    conn = get_db()
    rows = conn.execute('''
        SELECT c.*, f.titre as formation_titre, f.duree_heures,
               u.nom || ' ' || u.prenom as formateur_nom
        FROM certifications c
        JOIN formations f ON c.formation_id = f.id
        JOIN sessions s ON c.session_id = s.id
        JOIN utilisateurs u ON s.formateur_id = u.id
        WHERE c.etudiant_id=?
        ORDER BY c.date_emission DESC
    ''', (etudiant_id,)).fetchall()
    conn.close()
    return rows

def get_certification_by_numero(numero):
    conn = get_db()
    row = conn.execute('''
        SELECT c.*, u.nom || ' ' || u.prenom as etudiant_nom, u.email as etudiant_email,
               f.titre as formation_titre, f.duree_heures,
               s.date_debut, s.date_fin, s.lieu,
               uf.nom || ' ' || uf.prenom as formateur_nom
        FROM certifications c
        JOIN utilisateurs u ON c.etudiant_id = u.id
        JOIN formations f ON c.formation_id = f.id
        JOIN sessions s ON c.session_id = s.id
        JOIN utilisateurs uf ON s.formateur_id = uf.id
        WHERE c.numero_certificat=?
    ''', (numero,)).fetchone()
    conn.close()
    return row

def get_certification_by_id(cid):
    conn = get_db()
    row = conn.execute('''
        SELECT c.*, u.nom || ' ' || u.prenom as etudiant_nom, u.email as etudiant_email,
               f.titre as formation_titre, f.duree_heures,
               s.date_debut, s.date_fin, s.lieu,
               uf.nom || ' ' || uf.prenom as formateur_nom
        FROM certifications c
        JOIN utilisateurs u ON c.etudiant_id = u.id
        JOIN formations f ON c.formation_id = f.id
        JOIN sessions s ON c.session_id = s.id
        JOIN utilisateurs uf ON s.formateur_id = uf.id
        WHERE c.id=?
    ''', (cid,)).fetchone()
    conn.close()
    return row

def generate_numero_certificat():
    year = datetime.now().year
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM certifications WHERE date_emission LIKE ?", (f"{year}%",)).fetchone()[0]
    conn.close()
    return f"FP-{year}-{count+1:04d}"

def create_certification(etudiant_id, formation_id, session_id, mention, note_finale):
    numero = generate_numero_certificat()
    date_emission = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    conn.execute('''INSERT INTO certifications (etudiant_id, formation_id, session_id, numero_certificat,
                    date_emission, mention, note_finale) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (etudiant_id, formation_id, session_id, numero, date_emission, mention, note_finale))
    conn.commit()
    conn.close()
    return numero

def delete_certification(cid):
    conn = get_db()
    conn.execute("DELETE FROM certifications WHERE id=?", (cid,))
    conn.commit()
    conn.close()

# ── Stats ─────────────────────────────────────────────────────
def get_dashboard_stats():
    conn = get_db()
    stats = {
        'nb_etudiants': conn.execute("SELECT COUNT(*) FROM utilisateurs WHERE role='etudiant' AND actif=1").fetchone()[0],
        'nb_formateurs': conn.execute("SELECT COUNT(*) FROM utilisateurs WHERE role='formateur' AND actif=1").fetchone()[0],
        'nb_formations': conn.execute("SELECT COUNT(*) FROM formations WHERE actif=1").fetchone()[0],
        'nb_sessions': conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
        'nb_certifications': conn.execute("SELECT COUNT(*) FROM certifications WHERE valide=1").fetchone()[0],
        'nb_participations': conn.execute("SELECT COUNT(*) FROM participations").fetchone()[0],
        'sessions_en_cours': conn.execute("SELECT COUNT(*) FROM sessions WHERE statut='en_cours'").fetchone()[0],
    }
    conn.close()
    return stats
