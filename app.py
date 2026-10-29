import pickle
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd
import streamlit as st

BASE = Path(__file__).parent
CONTACT_EMAIL = "ouedaalexis@gmail.com"   # uniquement l'adresse, sans "mailto:"

st.set_page_config(page_title="MotorTriage", page_icon="⚙️", layout="wide")

# ---------- Style ----------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1150px;}
.hero {background: linear-gradient(120deg,#0b1f3a 0%,#0f4c81 55%,#13a89e 100%);
       padding: 2.8rem 2.4rem; border-radius: 22px; color: #fff; margin-bottom: 1.4rem;
       box-shadow: 0 12px 30px rgba(15,76,129,.28);}
.hero h1 {margin:0 0 .6rem 0; font-size: 2.7rem; line-height:1.1; color:#fff; font-weight:800;}
.hero h1 span {color:#ffb347;}
.hero p {margin:0 0 1.1rem 0; font-size: 1.15rem; opacity:.95; max-width: 760px;}
.pill {display:inline-block; background:rgba(255,255,255,.18); padding:.35rem .9rem; margin:0 .4rem .4rem 0;
       border-radius:999px; font-size:.85rem; font-weight:600; backdrop-filter: blur(4px);}
.feat {background:#fff; border-radius:16px; padding:1.1rem 1.2rem; height:100%;
       box-shadow:0 4px 14px rgba(15,23,42,.08); border-top:5px solid #13a89e; color:#0f172a;}
.feat.o {border-top-color:#f97316;} .feat.b {border-top-color:#0f4c81;} .feat.p {border-top-color:#8b5cf6;}
.feat .ic {font-size:1.8rem;} .feat h4 {margin:.3rem 0 .2rem 0; color:#0b1f3a;} .feat p {margin:0; font-size:.92rem; color:#475569;}
h2.sec {color:#0b1f3a; margin:1.6rem 0 .6rem 0; font-weight:800;}
[data-testid="stForm"] {background:#f8fafc; border:2px solid #e2e8f0; border-radius:18px; padding:1.4rem;}
[data-testid="stFormSubmitButton"] button {background: linear-gradient(90deg,#f97316,#ef4444); color:#fff; border:none;
       font-size:1.15rem; font-weight:700; padding:.8rem 1rem; border-radius:12px; box-shadow:0 8px 18px rgba(249,115,22,.35);}
[data-testid="stFormSubmitButton"] button:hover {filter:brightness(1.08); color:#fff;}
.verdict {padding:1.3rem 1.6rem; border-radius:16px; font-size:1.5rem; font-weight:800; margin:.8rem 0 1.1rem 0; color:#fff;}
.v-repair {background:linear-gradient(90deg,#059669,#10b981);} .v-replace {background:linear-gradient(90deg,#ea580c,#f97316);}
.kpi {background:#fff; border-radius:16px; padding:1rem 1.2rem; box-shadow:0 4px 14px rgba(15,23,42,.09); border-left:6px solid #0f4c81;}
.kpi.t {border-left-color:#13a89e;} .kpi.o {border-left-color:#f97316;} .kpi.p {border-left-color:#8b5cf6;}
.kpi .l {font-size:.8rem; text-transform:uppercase; letter-spacing:.05em; color:#64748b; font-weight:700;}
.kpi .v {font-size:1.7rem; font-weight:800; color:#0b1f3a; margin-top:.15rem;}
.barwrap {margin:.5rem 0 .9rem 0;} .barlab {display:flex; justify-content:space-between; font-weight:600; color:#0b1f3a; font-size:.95rem;}
.bar {background:#e2e8f0; border-radius:999px; height:14px; overflow:hidden; margin-top:.25rem;}
.bar div {height:100%; background:linear-gradient(90deg,#13a89e,#0f4c81); border-radius:999px;}
.cta {background:linear-gradient(120deg,#0b1f3a,#0f4c81); color:#fff; padding:2rem; border-radius:22px; text-align:center; margin-top:1.6rem;}
.cta h3 {color:#fff; margin:0 0 .5rem 0; font-size:1.7rem;} .cta p {opacity:.92; max-width:640px; margin:0 auto 1.1rem auto;}
.cta a {display:inline-block; background:linear-gradient(90deg,#f97316,#fbbf24); color:#0b1f3a !important; font-weight:800;
        padding:.85rem 1.6rem; border-radius:999px; text-decoration:none; margin:.25rem;}
.cta a.alt {background:#fff;}
.cta .addr {margin-top:.8rem; font-size:.95rem; opacity:.9;}
.small {font-size:.82rem; color:#64748b;}
</style>
""", unsafe_allow_html=True)

# ---------- Textes FR / DE ----------
TR = {
"fr": {
 "pill1": "⚙️ Ateliers de réparation de moteurs électriques", "pill2": "⚡ Résultat en quelques secondes",
 "h1a": "Réparer ou remplacer ?", "h1b": "Décidez avant de démonter.",
 "hero_p": "Saisissez les tests de réception : MotorTriage recommande la meilleure option, estime la cause de panne, le devis et le délai, pour répondre à vos clients plus vite et avec plus d'assurance.",
 "f1t": "Décision claire", "f1p": "Réparer ou remplacer, avec un niveau de confiance.",
 "f2t": "Devis cohérent", "f2p": "Une estimation de départ pour chiffrer plus vite.",
 "f3t": "Cause probable", "f3p": "Roulements, bobinage, rotor : où chercher en premier.",
 "f4t": "Délai annoncé", "f4p": "Un délai estimé à communiquer au client.",
 "sec_analyse": "🔧 Analysez un moteur",
 "motor": "Le moteur", "context": "Le contexte", "measures": "Mesures (optionnelles)",
 "power": "Puissance (kW)", "poles": "Nombre de pôles", "age": "Âge (années)", "effclass": "Classe d'efficacité",
 "vfd": "Piloté par variateur de vitesse", "application": "Application", "env": "Environnement",
 "urgency": "Urgence du client", "symptom": "Symptôme signalé", "newprice": "Prix d'un moteur neuf (€)",
 "use_ir": "Résistance d'isolement mesurée", "ir": "Isolement 1 min (MΩ)",
 "use_vib": "Vibrations mesurées", "vib": "Vibrations (mm/s RMS)",
 "use_nl": "Courant à vide mesuré", "nl": "Courant à vide (% du nominal)",
 "analyze": "🚀 Analyser le moteur", "result": "📋 Résultat de l'analyse",
 "ie5": "IE5 n'existait pas dans les données d'entraînement : le modèle a utilisé IE4, la classe la plus proche.",
 "replace": "🔄 Remplacement recommandé", "repair": "🛠️ Réparation recommandée", "conf": "de confiance",
 "k_quote": "Devis estimé", "k_days": "Délai estimé", "k_ratio": "Réparation / prix du neuf", "k_cause": "Cause probable",
 "days": "jours", "causes_title": "🔍 Causes de panne probables",
 "disclaimer": "⚠️ Démonstration : modèles entraînés sur des données synthétiques, non validés sur de vrais moteurs. Ne pas utiliser comme outil de décision réel.",
 "cta_title": "🤝 Vous dirigez un atelier de réparation ?",
 "cta_p": "Nous cherchons des ateliers pilotes pour tester MotorTriage sur de vrais dossiers et l'adapter à votre façon de travailler.",
 "cta_btn": "Devenir atelier pilote", "cta_gmail": "Ouvrir dans Gmail", "cta_addr": "Ou écrivez-nous :",
 "subject": "Atelier pilote MotorTriage",
},
"de": {
 "pill1": "⚙️ Werkstätten für die Reparatur von Elektromotoren", "pill2": "⚡ Ergebnis in Sekunden",
 "h1a": "Reparieren oder ersetzen?", "h1b": "Entscheiden Sie vor dem Zerlegen.",
 "hero_p": "Geben Sie die Eingangsprüfungen ein: MotorTriage empfiehlt die beste Option und schätzt Schadensursache, Angebotspreis und Bearbeitungszeit, damit Sie Ihren Kunden schneller und mit mehr Sicherheit antworten können.",
 "f1t": "Klare Entscheidung", "f1p": "Reparieren oder ersetzen, mit Konfidenzwert.",
 "f2t": "Konsistentes Angebot", "f2p": "Ein Richtwert, um schneller zu kalkulieren.",
 "f3t": "Wahrscheinliche Ursache", "f3p": "Lager, Wicklung, Rotor: wo man zuerst sucht.",
 "f4t": "Angekündigte Frist", "f4p": "Eine geschätzte Bearbeitungszeit für den Kunden.",
 "sec_analyse": "🔧 Motor analysieren",
 "motor": "Der Motor", "context": "Der Kontext", "measures": "Messwerte (optional)",
 "power": "Leistung (kW)", "poles": "Polzahl", "age": "Alter (Jahre)", "effclass": "Effizienzklasse",
 "vfd": "Mit Frequenzumrichter betrieben", "application": "Anwendung", "env": "Umgebung",
 "urgency": "Dringlichkeit des Kunden", "symptom": "Gemeldetes Symptom", "newprice": "Preis eines Neumotors (€)",
 "use_ir": "Isolationswiderstand gemessen", "ir": "Isolation 1 min (MΩ)",
 "use_vib": "Schwingungen gemessen", "vib": "Schwingungen (mm/s RMS)",
 "use_nl": "Leerlaufstrom gemessen", "nl": "Leerlaufstrom (% vom Nennwert)",
 "analyze": "🚀 Motor analysieren", "result": "📋 Analyseergebnis",
 "ie5": "IE5 war in den Trainingsdaten nicht enthalten: das Modell hat IE4 verwendet, die nächstliegende Klasse.",
 "replace": "🔄 Austausch empfohlen", "repair": "🛠️ Reparatur empfohlen", "conf": "Konfidenz",
 "k_quote": "Geschätztes Angebot", "k_days": "Geschätzte Bearbeitungszeit", "k_ratio": "Reparatur / Neupreis", "k_cause": "Wahrscheinliche Ursache",
 "days": "Tage", "causes_title": "🔍 Wahrscheinliche Schadensursachen",
 "disclaimer": "⚠️ Demo: Die Modelle wurden mit synthetischen Daten trainiert und nicht an echten Motoren validiert. Nicht als reales Entscheidungswerkzeug verwenden.",
 "cta_title": "🤝 Sie leiten eine Motorenwerkstatt?",
 "cta_p": "Wir suchen Pilotwerkstätten, die MotorTriage an echten Aufträgen testen und an Ihre Arbeitsweise anpassen.",
 "cta_btn": "Pilotwerkstatt werden", "cta_gmail": "In Gmail öffnen", "cta_addr": "Oder schreiben Sie uns:",
 "subject": "Pilotwerkstatt MotorTriage",
},
}

LBL = {
"fr": {
 "pump": "Pompe", "fan": "Ventilateur", "compressor": "Compresseur", "conveyor": "Convoyeur",
 "mixer_agitator": "Mélangeur / agitateur", "crusher_mill": "Broyeur / concasseur",
 "machine_tool": "Machine-outil", "other": "Autre",
 "clean_dry": "Propre et sec", "dusty": "Poussiéreux", "humid_washdown": "Humide / lavage",
 "outdoor_exposed": "Extérieur", "corrosive_chemical": "Corrosif / chimique",
 "standard": "Standard", "urgent": "Urgent", "critical_line_down": "Critique (ligne à l'arrêt)",
 "noise_or_vibration": "Bruit ou vibrations", "overheating": "Surchauffe",
 "tripping_or_no_start": "Disjonction / ne démarre pas", "seized_shaft": "Arbre bloqué",
 "high_current": "Courant élevé", "water_or_dirt_ingress": "Eau / saleté à l'intérieur",
 "none_planned_overhaul": "Aucun (révision prévue)",
},
"de": {
 "pump": "Pumpe", "fan": "Lüfter", "compressor": "Kompressor", "conveyor": "Förderband",
 "mixer_agitator": "Mischer / Rührwerk", "crusher_mill": "Brecher / Mühle",
 "machine_tool": "Werkzeugmaschine", "other": "Sonstige",
 "clean_dry": "Sauber und trocken", "dusty": "Staubig", "humid_washdown": "Feucht / Nassreinigung",
 "outdoor_exposed": "Außenbereich", "corrosive_chemical": "Korrosiv / chemisch",
 "standard": "Standard", "urgent": "Dringend", "critical_line_down": "Kritisch (Anlage steht)",
 "noise_or_vibration": "Geräusche oder Schwingungen", "overheating": "Überhitzung",
 "tripping_or_no_start": "Schutz löst aus / startet nicht", "seized_shaft": "Blockierte Welle",
 "high_current": "Erhöhter Strom", "water_or_dirt_ingress": "Wasser / Schmutz im Inneren",
 "none_planned_overhaul": "Keines (geplante Revision)",
},
}
CAUSES = {
"fr": {
 "bearing_failure": "Roulements", "stator_insulation_failure": "Isolation du bobinage",
 "stator_turn_short": "Court-circuit entre spires", "rotor_bar_or_endring": "Barres / anneau du rotor",
 "shaft_or_housing_mechanical": "Arbre / carter (mécanique)",
 "contamination_or_moisture": "Humidité / contamination", "no_fault_found": "Aucun défaut trouvé",
},
"de": {
 "bearing_failure": "Lager", "stator_insulation_failure": "Wicklungsisolation",
 "stator_turn_short": "Windungsschluss", "rotor_bar_or_endring": "Rotorstäbe / Kurzschlussring",
 "shaft_or_housing_mechanical": "Welle / Gehäuse (mechanisch)",
 "contamination_or_moisture": "Feuchtigkeit / Verunreinigung", "no_fault_found": "Kein Fehler gefunden",
},
}

# ---------- Choix de la langue ----------
choix = st.radio("🌐 Langue / Sprache", ["Français", "Deutsch"], horizontal=True, key="langue")
lang = "de" if choix == "Deutsch" else "fr"
t = lambda k: TR[lang][k]
fr = lambda v: LBL[lang].get(v, v)
cause = lambda v: CAUSES[lang].get(v, v)

def nombre(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", " ").replace(".", ",") if lang == "fr" else s.replace(",", "X").replace(".", ",").replace("X", ".")

def pct(x):
    return f"{x:.0%}"

def kpi(label, value, cls=""):
    return f'<div class="kpi {cls}"><div class="l">{label}</div><div class="v">{value}</div></div>'

# ---------- Modèles ----------
@st.cache_resource
def charger():
    noms = ["m_decision", "m_mode", "m_quote", "m_days"]
    return {n: pickle.load(open(BASE / f"{n}.pkl", "rb")) for n in noms}

P = charger()
x_cols = P["m_decision"]["x_cols"]
cats = P["m_decision"]["categories"]

# ---------- Hero ----------
st.markdown(f"""
<div class="hero">
  <span class="pill">{t("pill1")}</span>
  <span class="pill">{t("pill2")}</span>
  <h1>{t("h1a")}<br><span>{t("h1b")}</span></h1>
  <p>{t("hero_p")}</p>
</div>
""", unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
f1.markdown(f'<div class="feat"><div class="ic">🎯</div><h4>{t("f1t")}</h4><p>{t("f1p")}</p></div>', unsafe_allow_html=True)
f2.markdown(f'<div class="feat o"><div class="ic">💶</div><h4>{t("f2t")}</h4><p>{t("f2p")}</p></div>', unsafe_allow_html=True)
f3.markdown(f'<div class="feat b"><div class="ic">🔍</div><h4>{t("f3t")}</h4><p>{t("f3p")}</p></div>', unsafe_allow_html=True)
f4.markdown(f'<div class="feat p"><div class="ic">⏱️</div><h4>{t("f4t")}</h4><p>{t("f4p")}</p></div>', unsafe_allow_html=True)

st.markdown(f'<h2 class="sec">{t("sec_analyse")}</h2>', unsafe_allow_html=True)

# ---------- Formulaire (clés fixes : les valeurs restent quand on change de langue) ----------
saisie = {}
with st.form("form_moteur"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader(t("motor"))
        saisie["rated_power_kw"] = st.number_input(t("power"), 0.75, 315.0, 11.0, key="w_power")
        saisie["pole_count"] = st.selectbox(t("poles"), [2, 4, 6, 8], index=1, key="w_poles")
        saisie["age_years"] = st.number_input(t("age"), 1, 50, 10, key="w_age")
        saisie["efficiency_class_nameplate"] = st.selectbox(
            t("effclass"), cats["efficiency_class_nameplate"] + ["IE5"], key="w_eff")
        saisie["vfd_driven"] = int(st.checkbox(t("vfd"), key="w_vfd"))
    with c2:
        st.subheader(t("context"))
        saisie["application_type"] = st.selectbox(t("application"), cats["application_type"], format_func=fr, key="w_app")
        saisie["environment"] = st.selectbox(t("env"), cats["environment"], format_func=fr, key="w_env")
        saisie["customer_urgency"] = st.selectbox(t("urgency"), cats["customer_urgency"], format_func=fr, key="w_urg")
        saisie["reported_symptom"] = st.selectbox(t("symptom"), cats["reported_symptom"], format_func=fr, key="w_sym")
        saisie["new_motor_ie3_list_price_eur"] = st.number_input(t("newprice"), 0.0, 50000.0, 1000.0, key="w_price")
    with c3:
        st.subheader(t("measures"))
        use_ir = st.checkbox(t("use_ir"), key="w_use_ir")
        ir = st.number_input(t("ir"), 0.1, 20000.0, 500.0, key="w_ir")
        use_vib = st.checkbox(t("use_vib"), key="w_use_vib")
        vib = st.number_input(t("vib"), 0.1, 30.0, 1.5, key="w_vib")
        use_nl = st.checkbox(t("use_nl"), key="w_use_nl")
        nl = st.number_input(t("nl"), 10.0, 100.0, 35.0, key="w_nl")
    go = st.form_submit_button(t("analyze"), type="primary", use_container_width=True)

def construire_ligne(saisie):
    ligne = {c: np.nan for c in x_cols}   # non saisi = valeur manquante
    ligne.update(saisie)
    df = pd.DataFrame([ligne])[x_cols]
    for c in x_cols:
        if c in cats:
            df[c] = pd.Categorical(df[c], categories=cats[c])
        else:
            df[c] = pd.to_numeric(df[c])
    return df

if go:
    if use_ir: saisie["insulation_resistance_1min_mohm"] = ir
    if use_vib: saisie["vibration_rms_mm_s"] = vib
    if use_nl: saisie["no_load_current_pct_of_rated"] = nl
    ie5 = saisie["efficiency_class_nameplate"] == "IE5"
    if ie5:
        saisie["efficiency_class_nameplate"] = "IE4"   # IE5 absent de l'entraînement
    st.session_state["derniere"] = {"saisie": dict(saisie), "ie5": ie5}

# ---------- Résultats (restent affichés quand on change de langue) ----------
if "derniere" in st.session_state:
    S = st.session_state["derniere"]["saisie"]
    ie5 = st.session_state["derniere"]["ie5"]
    ligne = construire_ligne(S)
    m_dec = P["m_decision"]["model"]
    p_rempl = float(m_dec.predict_proba(ligne)[0][list(m_dec.classes_).index(1)])
    m_mode = P["m_mode"]["model"]
    modes = pd.Series(m_mode.predict_proba(ligne)[0], index=m_mode.classes_).sort_values(ascending=False)
    devis = float(np.exp(P["m_quote"]["model"].predict(ligne)[0]))
    jours = float(P["m_days"]["model"].predict(ligne)[0])
    prix_neuf = S["new_motor_ie3_list_price_eur"]

    st.markdown(f'<h2 class="sec">{t("result")}</h2>', unsafe_allow_html=True)
    if ie5:
        st.info(t("ie5"))
    if p_rempl >= 0.5:
        st.markdown(f'<div class="verdict v-replace">{t("replace")} · {pct(p_rempl)} {t("conf")}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="verdict v-repair">{t("repair")} · {pct(1-p_rempl)} {t("conf")}</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(kpi(t("k_quote"), f"{nombre(devis)} €", "o"), unsafe_allow_html=True)
    k2.markdown(kpi(t("k_days"), f"{nombre(max(jours, 1))} {t('days')}", "t"), unsafe_allow_html=True)
    ratio = pct(devis / prix_neuf) if prix_neuf > 0 else "n/a"
    k3.markdown(kpi(t("k_ratio"), ratio, ""), unsafe_allow_html=True)
    k4.markdown(kpi(t("k_cause"), cause(modes.index[0]), "p"), unsafe_allow_html=True)

    st.markdown(f'<h2 class="sec">{t("causes_title")}</h2>', unsafe_allow_html=True)
    for nom, p in modes.head(3).items():
        st.markdown(
            f'<div class="barwrap"><div class="barlab"><span>{cause(nom)}</span><span>{pct(p)}</span></div>'
            f'<div class="bar"><div style="width:{min(max(p,0),1)*100:.0f}%"></div></div></div>',
            unsafe_allow_html=True)

    st.markdown(f'<p class="small">{t("disclaimer")}</p>', unsafe_allow_html=True)

# ---------- Appel à l'action ----------
sujet = quote(t("subject"))
href_mail = f"mailto:{CONTACT_EMAIL}?subject={sujet}"
href_gmail = f"https://mail.google.com/mail/?view=cm&fs=1&to={CONTACT_EMAIL}&su={sujet}"
st.markdown(f"""
<div class="cta">
  <h3>{t("cta_title")}</h3>
  <p>{t("cta_p")}</p>
  <a href="{href_mail}">✉️ {t("cta_btn")}</a>
  <a class="alt" href="{href_gmail}" target="_blank" rel="noopener">{t("cta_gmail")}</a>
  <div class="addr">{t("cta_addr")} <b>{CONTACT_EMAIL}</b></div>
</div>
""", unsafe_allow_html=True)
