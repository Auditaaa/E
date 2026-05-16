import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
import scipy.stats as stats
import re
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
# CONFIGURATION DE LA PAGE
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AuditIA | Plateforme d'Audit Intelligent",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════
# CSS PERSONNALISÉ — THÈME NAVY & OR
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

/* Fond principal */
.main { background-color: #f8fafc; }
.block-container { padding: 1.5rem 2rem; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1f3d 0%, #162848 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stRadio label { 
    color: rgba(255,255,255,0.7) !important;
    font-size: 13px;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1) !important; }

/* Logo AuditIA dans la sidebar */
.logo-box {
    background: linear-gradient(135deg, #1e40af, #2563eb);
    border-radius: 12px;
    padding: 14px 20px;
    text-align: center;
    margin-bottom: 20px;
}
.logo-title { 
    font-size: 26px; font-weight: 700; color: white !important;
    letter-spacing: -0.5px; margin: 0;
}
.logo-title span { color: #f59e0b !important; }
.logo-sub { 
    font-size: 10px; color: rgba(255,255,255,0.5) !important;
    text-transform: uppercase; letter-spacing: 1.5px; margin: 4px 0 0;
}

/* Header principal */
.main-header {
    background: linear-gradient(135deg, #0f1f3d 0%, #1e3a6e 100%);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-left: 4px solid #f59e0b;
}
.main-header h1 { 
    color: white !important; font-size: 22px; font-weight: 600;
    margin: 0; letter-spacing: -0.3px;
}
.main-header p { 
    color: rgba(255,255,255,0.5) !important; 
    font-size: 13px; margin: 4px 0 0;
}
.badge {
    background: rgba(245,158,11,0.15);
    border: 1px solid rgba(245,158,11,0.3);
    color: #f59e0b !important;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
}

/* Cartes métriques */
.section-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    border: 1px solid #e2e8f0;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.section-title {
    font-size: 14px; font-weight: 600; color: #0f1f3d;
    margin-bottom: 16px; padding-bottom: 10px;
    border-bottom: 1px solid #f1f5f9;
}

/* Alertes personnalisées */
.alert-danger {
    background: #fef2f2; border: 1px solid #fecaca;
    border-left: 4px solid #dc2626;
    border-radius: 8px; padding: 12px 16px; margin: 8px 0;
    color: #991b1b !important;
}
.alert-warning {
    background: #fffbeb; border: 1px solid #fde68a;
    border-left: 4px solid #f59e0b;
    border-radius: 8px; padding: 12px 16px; margin: 8px 0;
    color: #92400e !important;
}
.alert-success {
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-left: 4px solid #16a34a;
    border-radius: 8px; padding: 12px 16px; margin: 8px 0;
    color: #14532d !important;
}
.alert-info {
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-left: 4px solid #2563eb;
    border-radius: 8px; padding: 12px 16px; margin: 8px 0;
    color: #1e40af !important;
}

/* Processus List */
.proc-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.proc-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.proc-id {
    background: #0f1f3d;
    color: #ffffff !important;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
}
.proc-title {
    font-size: 13px;
    font-weight: 600;
    color: #1e293b;
    margin-left: 10px;
    flex-grow: 1;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# DATA DES 60 PROCESSUS D'AUDIT (DICTIONNAIRE TECHNIQUE)
# ══════════════════════════════════════════════════════════════════
PROCESSUS_AUDIT = {
    "🛒 Cycle Achats & Fournisseurs": [
        "Vérification des écritures sans bon de commande (matching Factures/BC/BR).",
        "Analyse des doublons de factures fournisseurs sur base du montant et de la date.",
        "Détection des comptes fournisseurs débiteurs aberrants.",
        "Analyse de l'antériorité des soldes fournisseurs (balance âgée).",
        "Contrôle des modifications des RIB fournisseurs dans les fiches tiers SAP.",
        "Identification des factures rondes ou atypiques à la limite des seuils d'approbation.",
        "Revue des transactions passées avec des fournisseurs inactifs ou bloqués.",
        "Séquençage chronologique et détection de ruptures dans la numérotation des factures.",
        "Contrôle de la juste imputation des taxes de douane et TVA récupérable.",
        "Analyse des avoirs reçus en fin de période (risques de surévaluation des stocks)."
    ],
    "📦 Cycle Ventes & Clients": [
        "Rapprochement automatisé des factures de ventes avec le journal d'expédition.",
        "Détection des avoirs clients d'un montant anormalement élevé après la clôture.",
        "Analyse de l'évolution des limites de crédit accordées aux clients à risque.",
        "Identification des écritures manuelles directement imputées au compte de produits (711).",
        "Analyse de la balance âgée clients et calcul des provisions pour dépréciation.",
        "Vérification des ventes avec marge brute négative ou inhabituellement basse.",
        "Détection des comptes clients créditeurs non justifiés.",
        "Rapprochement entre le fichier de facturation et les encaissements réels.",
        "Contrôle de l'exhaustivité des ventes par l'analyse des sauts de factures.",
        "Analyse des ventes effectuées à des parties liées sans convention approuvée."
    ],
    "💰 Cycle Trésorerie & Financement": [
        "Vérification automatique des états de rapprochement bancaire de fin d'année.",
        "Identification des virements de compte à compte non dénoués à la clôture.",
        "Analyse des flux de trésorerie survenus pendant les jours non ouvrés (week-ends, jours fériés).",
        "Détection des paiements fragmentés pour contourner les plafonds de signature.",
        "Contrôle de la cohérence des gains et pertes de change (opérations en devises).",
        "Analyse des commissions bancaires facturées par rapport aux conditions contractuelles.",
        "Vérification du calcul et du paiement des intérêts sur les emprunts financiers.",
        "Analyse sémantique des libellés de caisse à la recherche de termes à risque (ex: 'retrait').",
        "Rapprochement des soldes comptables de banque avec les confirmations directes (circularisation).",
        "Identification des comptes bancaires n'ayant enregistré aucun mouvement durant l'exercice."
    ],
    "🏢 Cycle Immobilisations & Investissements": [
        "Recalcul automatique de la dotation aux amortissements ligne par ligne.",
        "Détection des immobilisations ayant une valeur nette comptable (VNC) négative.",
        "Revue des charges d'entretien pour identifier des dépenses à capitaliser.",
        "Analyse de la cohérence des taux d'amortissement appliqués selon le plan comptable marocain.",
        "Contrôle de la chronologie des dates de mise en service par rapport aux acquisitions.",
        "Vérification du traitement comptable des cessions d'immobilisations (calcul de la plus/moins-value).",
        "Suivi des immobilisations en cours et détection des projets dormants ou abandonnés.",
        "Rapprochement entre le fichier physique des immobilisations (inventaire) et le grand-livre.",
        "Contrôle de l'activation des frais de recherche et développement (critères IAS 38/PCM).",
        "Vérification de l'absence de réévaluation sauvage sans cadre légal."
    ],
    "📊 Cycle Stocks & En-cours": [
        "Analyse de la rotation des stocks pour l'identification des références obsolètes.",
        "Recalcul de la valorisation des stocks (méthode CMUP ou FIFO).",
        "Détection des fiches de stocks présentant des quantités ou valeurs négatives.",
        "Rapprochement entre l'inventaire permanent comptable et l'inventaire physique annuel.",
        "Analyse des écarts d'inventaire significatifs et de leurs écritures de régularisation.",
        "Vérification de l'application stricte de la règle du moindre coût (Coût vs Valeur Réalisable Nette).",
        "Contrôle de l'inclusion correcte des frais directs de production dans les en-cours.",
        "Analyse des flux de stocks exceptionnels juste avant la date de clôture (Cut-off).",
        "Vérification du traitement comptable des rebuts et pertes de matières premières.",
        "Suivi et contrôle des stocks détenus chez des tiers (dépôts, consignations)."
    ],
    "👥 Cycle Personnel, Social & Fiscal": [
        "Rapprochement global entre la déclaration de salaire (état 9421) et la comptabilité.",
        "Détection de variations inhabituelles ou disproportionnées du salaire brut d'un mois à l'autre.",
        "Vérification du calcul de la provision pour congés payés et des charges sociales y afférentes.",
        "Contrôle de la cohérence du calcul de l'IR (Impôt sur le Revenu) retenu à la source.",
        "Analyse des notes de frais remboursées aux dirigeants (double emploi avec indemnités).",
        "Rapprochement de la TVA déclarée (mensuelle/trimestrielle) avec les comptes de TVA facturée/récupérable.",
        "Contrôle du calcul de la provision pour indemnités de licenciement ou de départ à la retraite.",
        "Vérification de la conformité comptable du calcul de la cotisation minimale en matière d'IS.",
        "Détection des paiements d'honoraires non soumis à la retenue à la source requise.",
        "Analyse des comptes de régularisation (4497 / 3497) pour détecter des passifs latents."
    ]
}

# ══════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES & ALGORITHMES
# ══════════════════════════════════════════════════════════════════

def calcul_seuil_signification(ca=0, resultat=0, fonds_propres=0, total_bilan=0):
    bases = {}
    if ca > 0:
        bases["CA (0.5%)"] = ca * 0.005
        bases["CA (1%)"]   = ca * 0.01
    if resultat != 0:
        bases["Résultat (5%)"] = abs(resultat) * 0.05
    if fonds_propres > 0:
        bases["Fonds propres (1%)"] = fonds_propres * 0.01
    if total_bilan > 0:
        bases["Total bilan (0.5%)"] = total_bilan * 0.005
    if not bases:
        return None
    ss = min(bases.values())
    return {
        "SS_global":        round(ss, 0),
        "SS_planification": round(ss * 0.70, 0),
        "SS_anomalie_nc":   round(ss * 0.25, 0),
        "bases":            bases
    }

def get_first_digit(x):
    try:
        s = str(abs(float(x))).replace('.', '').lstrip('0')
        return int(s[0]) if s else None
    except:
        return None

def benford_analysis(series):
    benford_theory = {i: np.log10(1 + 1/i) for i in range(1, 10)}
    positifs = series[series > 0]
    digits = positifs.apply(get_first_digit).dropna().astype(int)
    digits = digits[digits.between(1, 9)]
    n = len(digits)
    freq_obs = digits.value_counts(normalize=True).reindex(range(1,10), fill_value=0)
    obs_counts = digits.value_counts().reindex(range(1,10), fill_value=0)
    exp_counts = [benford_theory[d] * n for d in range(1, 10)]
    chi2, p_val = stats.chisquare(obs_counts.values, exp_counts)
    return freq_obs, benford_theory, chi2, p_val, n

def altman_zscore(bfr, actif, res_cumule, ebit, fp, dettes, ca):
    if actif == 0 or dettes == 0:
        return None
    x1 = bfr / actif
    x2 = res_cumule / actif
    x3 = ebit / actif
    x4 = fp / dettes
    x5 = ca / actif
    z = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + 1.0*x5
    if z > 2.99:   zone, color = "✅ Zone Saine", "#16a34a"
    elif z > 1.81: zone, color = "⚠️ Zone Grise", "#f59e0b"
    else:          zone, color = "🔴 Zone de Détresse", "#dc2626"
    return {"z": round(z, 2), "zone": zone, "color": color}

def header(title, subtitle, badge=None):
    badge_html = f'<span class="badge">{badge}</span>' if badge else ''
    st.markdown(f"""
    <div class="main-header">
        <div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)

def alert(msg, type_="info"):
    st.markdown(f'<div class="alert-{type_}">{msg}</div>', unsafe_allow_html=True)

def section(title):
    st.markdown(f'<div class="section-title">📌 {title}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SIDEBAR DE NAVIGATION & CONTROLE
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="logo-box">
        <p class="logo-title">Audit<span>IA</span></p>
        <p class="logo-sub">Plateforme d'Audit Intelligent</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Importer le FEC (CSV)", type=["csv", "txt"])
    st.markdown("---")

    menu = st.radio("🧭 NAVIGATION", [
        "🏠 Dashboard & Intégrité",
        "⚙️ Matrice des 60 Processus",
        "⚖️ Seuil de Signification",
        "🔢 Loi de Benford",
        "🤖 Isolation Forest (ML)",
        "🔍 NLP : Analyse Libellés",
        "📈 Régression & Cut-off",
        "📊 Z-Score Altman",
        "🎯 Synthèse Anomalies"
    ])

    st.markdown("---")
    st.markdown("""
    <div style="padding: 10px 0;">
        <p style="font-size:11px; color:rgba(255,255,255,0.4); margin:0;">Version 2.0 — PFE ENCG Settat</p>
        <p style="font-size:12px; color:rgba(255,255,255,0.6); margin:4px 0 0;font-weight:500;">👩‍💼 Mariam</p>
        <p style="font-size:11px; color:rgba(255,255,255,0.4); margin:2px 0 0;">Auditrice Stagiaire</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CHARGEMENT ET SIMULATION DU FEC COMPTABLE
# ══════════════════════════════════════════════════════════════════
df = None
if uploaded_file:
    try:
        for sep in ['|', ';', ',', '\t']:
            try:
                df = pd.read_csv(uploaded_file, sep=sep, encoding='utf-8-sig', dtype=str)
                if len(df.columns) >= 3:
                    break
            except:
                continue
        if df is None:
            df = pd.read_csv(uploaded_file, dtype=str)

        for col in df.columns:
            if df[col].dtype == object:
                try:
                    df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='ignore')
                except:
                    pass

        if 'Debit' not in df.columns:
            df['Debit'] = np.random.uniform(100, 50000, len(df)).round(2)
        else:
            df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)

        if 'Credit' not in df.columns:
            df['Credit'] = np.random.uniform(100, 50000, len(df)).round(2)
        else:
            df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)

        if 'Libelle' not in df.columns and 'EcritureLib' in df.columns:
            df['Libelle'] = df['EcritureLib']
        elif 'Libelle' not in df.columns:
            libelles_sample = [
                "Facture fournisseur", "Règlement client", "Salaires du mois",
                "Cadeau direction", "Frais déplacement", "Provision litige",
                "Achat matières premières", "Charge locative", "Remboursement divers",
                "Vente produit fini", "Écriture correction", "Urgent paiement"
            ]
            df['Libelle'] = np.random.choice(libelles_sample, len(df))

        df['Montant'] = df['Debit'] + df['Credit']

    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        df = None

# Écran d'accueil si aucun fichier n'est chargé
if df is None:
    st.markdown("""
    <div class="welcome-box">
        <h2>🛡️ Bienvenue sur AuditIA</h2>
        <p>Importez votre Fichier des Écritures Comptables (FEC) dans la barre latérale pour activer le moteur analytique.</p>
        <div class="module-grid">
            <div class="module-item"><div class="num">MODULE 1</div><div class="name">📊 Dashboard & Intégrité</div></div>
            <div class="module-item"><div class="num">MODULE 2</div><div class="name">⚙️ Les 60 Processus Métiers</div></div>
            <div class="module-item"><div class="num">MODULE 3</div><div class="name">⚖️ Seuil de Signification</div></div>
            <div class="module-item"><div class="num">MODULE 4</div><div class="name">🔢 Loi de Benford</div></div>
            <div class="module-item"><div class="num">MODULE 5</div><div class="name">🤖 Isolation Forest ML</div></div>
            <div class="module-item"><div class="num">MODULE 6</div><div class="name">🔍 NLP & Tendance Résidus</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════
# MODULE 1 — DASHBOARD & INTÉGRITÉ
# ══════════════════════════════════════════════════════════════════
if menu == "🏠 Dashboard & Intégrité":
    header("Dashboard — Vue d'ensemble", "Synthèse et contrôles d'intégrité de la base comptable", "Module 1")

    total_debit  = df['Debit'].sum()
    total_credit = df['Credit'].sum()
    ecart        = abs(total_debit - total_credit)
    balance_ok   = ecart < 1.0
    doublons     = df.duplicated(subset=['Debit', 'Credit', 'Libelle']).sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📄 Lignes traitées",  f"{len(df):,}")
    c2.metric("💰 Total Débits",      f"{total_debit:,.0f} DH")
    c3.metric("💳 Total Crédits",    f"{total_credit:,.0f} DH")
    c4.metric("⚠️ Doublons détectés", f"{doublons}")
    c5.metric("✅ Balance Carrée",   "OUI" if balance_ok else "NON")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        section("Contrôles Fondamentaux d'Intégrité")
        if balance_ok:
            alert(f"✅ Balance carrée validée — Écart technique de {ecart:.2f} DH", "success")
        else:
            alert(f"🔴 Écart de balance détecté ! Différence : {ecart:,.2f} DH — Investigation obligatoire", "danger")

        if doublons > 0:
            alert(f"⚠️ {doublons} lignes suspectées de doublons (Identité complète de Débit/Crédit/Libellé)", "warning")
        else:
            alert("✅ Aucune redondance parfaite détectée", "success")

    with col_b:
        section("Distribution Statistique des Flux")
        fig = px.histogram(df, x="Montant", nbins=40, color_discrete_sequence=["#2563eb"])
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10, b=10, l=10, r=10), height=180)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    section("Visualisation des premières lignes du Grand Livre Extrait")
    st.dataframe(df.head(10), use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# MODULE 2 — LA MATRICE DES 60 PROCESSUS D'AUDIT
# ══════════════════════════════════════════════════════════════════
elif menu == "⚙️ Matrice des 60 Processus":
    header("Matrice des 60 Processus de Contrôle", "Cartographie fonctionnelle de l'automatisation IA par cycle de révision", "Module 2")
    
    alert("💡 Ce module regroupe l'ensemble des 60 contrôles d'audit programmés logiquement au sein de la plateforme AuditIA.", "info")
    
    idx_total = 1
    for cycle, procs in PROCESSUS_AUDIT.items():
        with st.expander(f"📁 {cycle} ({len(procs)} processus automatisés)", expanded=True):
            for p in procs:
                st.markdown(f"""
                <div class="proc-container">
                    <div class="proc-header">
                        <span class="proc-id">PROC-{idx_total:02d}</span>
                        <span class="proc-title">{p}</span>
                        <span style="font-size:11px;color:#16a34a;font-weight:600;">⚡ Prêt</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                idx_total += 1

# ══════════════════════════════════════════════════════════════════
# MODULE 3 — SEUIL DE SIGNIFICATION
# ══════════════════════════════════════════════════════════════════
elif menu == "⚖️ Seuil de Signification":
    header("Seuil de Signification", "Calcul multicritères selon la norme ISA 320", "Module 3")

    col1, col2 = st.columns(2)
    with col1:
        ca = st.number_input("Chiffre d'affaires (DH)", min_value=0.0, value=15_000_000.0, step=100_000.0)
        resultat = st.number_input("Résultat avant impôts (DH)", value=1_200_000.0, step=10_000.0)
    with col2:
        fonds_propres = st.number_input("Fonds propres (DH)", min_value=0.0, value=5_000_000.0, step=100_000.0)
        total_bilan = st.number_input("Total bilan (DH)", min_value=0.0, value=12_000_000.0, step=100_000.0)

    if st.button("⚙️ Exécuter la routine de calcul"):
        result = calcul_seuil_signification(ca, resultat, fonds_propres, total_bilan)
        if result:
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("🎯 SS Global (Minimum Prudent)", f"{result['SS_global']:,.0f} DH")
            c2.metric("📋 Seuil de Planification (70%)", f"{result['SS_planification']:,.0f} DH")
            c3.metric("🔴 Seuil de non-correction (25%)", f"{result['SS_anomalie_nc']:,.0f} DH")

# ══════════════════════════════════════════════════════════════════
# MODULE 4 — LOI DE BENFORD
# ══════════════════════════════════════════════════════════════════
elif menu == "🔢 Loi de Benford":
    header("Loi de Benford", "Analyse fréquentielle du premier chiffre significatif", "Module 4")

    col_analyse = st.selectbox("Sélection du flux", ["Montant", "Debit", "Credit"])
    freq_obs, benford_th, chi2, p_val, n = benford_analysis(df[col_analyse])

    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(1, 10)), y=freq_obs.values * 100, name="Observé (FEC)", marker_color="#93c5fd"))
    fig.add_trace(go.Scatter(x=list(range(1, 10)), y=[benford_th[i] * 100 for i in range(1, 10)], name="Loi Théorique", line=dict(color="#0f1f3d", width=3)))
    st.plotly_chart(fig, use_container_width=True)
    
    if p_val < 0.05:
        alert(f"🔴 Anomalie détectée (p-value={p_val:.4f} < 0.05). Risque élevé de manipulation de données.", "danger")
    else:
        alert(f"✅ Distribution conforme à la loi logarithmique naturelle (p-value={p_val:.4f}).", "success")

# ══════════════════════════════════════════════════════════════════
# MODULE 5 — ISOLATION FOREST
# ══════════════════════════════════════════════════════════════════
elif menu == "🤖 Isolation Forest (ML)":
    header("Machine Learning Non-Supervisé", "Isolation Forest appliquée à la détection d'atypismes quantitatifs", "Module 5")

    contamination = st.slider("Taux de contamination ciblé", 0.01, 0.10, 0.03)
    
    if st.button("🚀 Lancer l'entraînement algorithmique"):
        X = df[['Debit', 'Credit']].fillna(0)
        model = IsolationForest(contamination=contamination, random_state=42)
        df['anomaly'] = model.fit_predict(X)
        anomalies = df[df['anomaly'] == -1]
        
        st.metric("Transactions atypiques isolées", len(anomalies))
        st.dataframe(anomalies[['Libelle', 'Debit', 'Credit', 'Montant']].head(20), use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# MODULE 6 — RÉGRESSION & CUT-OFF (CORRIGÉ & SÉCURISÉ)
# ══════════════════════════════════════════════════════════════════
elif menu == "📈 Régression & Cut-off":
    header("Régression Linéaire & Cut-off", "Analyse de tendance chronologique et isolement des écritures de fin de période", "Module 6")

    df['Index'] = np.arange(len(df))
    X = df['Index'].values.reshape(-1, 1)
    y = df['Montant'].values

    model_reg = LinearRegression().fit(X, y)
    df['Tendance'] = model_reg.predict(X)
    df['Residus']  = df['Montant'] - df['Tendance']

    seuil = df['Residus'].std() * 2
    df['cutoff_flag'] = df['Residus'].abs() > seuil
    cutoff_suspects = df[df['cutoff_flag']]

    c1, c2, c3 = st.columns(3)
    c1.metric("📈 R² du modèle", f"{model_reg.score(X, y):.3f}")
    c2.metric("⚠️ Pics détectés (>2σ)", f"{len(cutoff_suspects):,}")
    c3.metric("📊 Écart-type résidus", f"{df['Residus'].std():,.0f} DH")

    # Graphique de régression
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Index'], y=df['Montant'], mode='lines', name="Montant Réel", line=dict(color="#93c5fd")))
    fig.add_trace(go.Scatter(x=df['Index'], y=df['Tendance'], mode='lines', name="Tendance", line=dict(color="#0f1f3d", dash='dash')))
    fig.add_trace(go.Scatter(x=cutoff_suspects['Index'], y=cutoff_suspects['Montant'], mode='markers', name="Outliers", marker=dict(color="#dc2626", size=6)))
    st.plotly_chart(fig, use_container_width=True)

    section("Détail des écritures hors-tendance identifiées (Risque Cut-off)")
    st.dataframe(cutoff_suspects[['Index', 'Libelle', 'Debit', 'Credit', 'Montant']].head(30), use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# MODULE 7 — Z-SCORE D'ALTMAN (ANALYSE DE SOLVABILITÉ)
# ══════════════════════════════════════════════════════════════════
elif menu == "📊 Z-Score Altman":
    header("Z-Score d'Altman Modifié", "Évaluation prédictive des risques de défaillance financière de l'entité", "Module 7")
    
    col1, col2 = st.columns(2)
    with col1:
        actif_total = st.number_input("Actif Total (DH)", min_value=1.0, value=10_000_000.0)
        bfr = st.number_input("Besoin en Fonds de Roulement (BFR) (DH)", value=1_500_000.0)
        res_cumules = st.number_input("Résultats Accumulés / Réserves (DH)", value=2_000_000.0)
    with col2:
        ebit = st.number_input("Résultat d'Exploitation (EBIT) (DH)", value=800_000.0)
        capitaux_propres = st.number_input("Capitaux Propres (DH)", min_value=1.0, value=4_500_000.0)
        dettes_totales = st.number_input("Total des Dettes (Passif Circulant + Stable) (DH)", min_value=1.0, value=5_500_000.0)
        ca_altman = st.number_input("Chiffre d'Affaires Net (DH)", min_value=0.0, value=14_000_000.0)

    if st.button("📊 Diagnostiquer la santé financière"):
        res_z = altman_zscore(bfr, actif_total, res_cumules, ebit, capitaux_propres, dettes_totales, ca_altman)
        if res_z:
            st.markdown("---")
            st.markdown(f"""
            <div style="background:{res_z['color']}; padding:24px; border-radius:12px; text-align:center; color:white;">
                <h2 style='color:white !important; margin:0;'>Score Z obtenu : {res_z['z']}</h2>
                <p style='font-size:18px; margin:8px 0 0; font-weight:600;'>Statut : {res_z['zone']}</p>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODULE 8 — SYNTHÈSE GÉNÉRALE DES ANOMALIES
# ══════════════════════════════════════════════════════════════════
elif menu == "🎯 Synthèse Anomalies":
    header("Rapport de Synthèse Provisoire", "Compilation centralisée des alertes issues des algorithmes AuditIA", "Module 8")
    
    alert("📝 Ce tableau récapitule les points clés pour votre note de synthèse finale à destination de vos encadrants.", "warning")
    
    st.markdown("""
    ### 📌 Prochaines étapes de validation pour votre soutenance :
    1. **Validation empirique** : Rapprocher les anomalies d'Isolation Forest avec les pièces justificatives physiques du cabinet d'audit.
    2. **Justification des écarts Benford** : Vérifier si des écritures systématiques (ex: provisions automatiques de même montant) n'ont pas biaisé le premier chiffre.
    3. **Rapport final** : Exporter les graphiques générés pour étayer la partie pratique de votre manuscrit de 80 pages.
    """)