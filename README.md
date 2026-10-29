# MotorTriage ⚙️

**Réparer ou remplacer un moteur électrique ? Décidez avant de démonter.**

MotorTriage est un prototype d'aide à la décision pour les ateliers de réparation de moteurs électriques. À partir des tests de réception, il recommande de réparer ou de remplacer, estime la cause probable de la panne, le devis et le délai. L'interface est disponible en **français** et en **allemand**.

🔗 **Démo** : [lien Streamlit]

> ⚠️ **Démonstration uniquement.** Les modèles sont entraînés sur un jeu de données **synthétique**. Ils n'ont pas été validés sur de vrais moteurs et ne doivent pas être utilisés pour des décisions réelles.

## Le problème

Quand un moteur en panne arrive à l'atelier, il faut décider vite : le réparer ou conseiller un moteur neuf. Cette décision se prend souvent à l'expérience, avec des règles simples (par exemple « si la réparation dépasse 60 % du prix du neuf, on remplace »). Les devis sont peu homogènes et les choix difficiles à justifier devant le client.

## Ce que fait l'application

L'atelier saisit les mesures de réception (puissance, âge, application, environnement, résistance d'isolement, vibrations, courant à vide…). L'app renvoie en quelques secondes :

- une **recommandation** réparer / remplacer, avec un niveau de confiance ;
- les **3 causes de panne** les plus probables (roulements, isolation, rotor, etc.) ;
- un **devis estimé** et son rapport au prix d'un moteur neuf ;
- un **délai estimé**.

Les mesures non saisies sont traitées comme des valeurs manquantes : l'atelier peut n'en renseigner que quelques-unes.

## Données et modèles

- **Données** : environ 60 000 dossiers d'atelier **simulés**, avec 47 variables connues à la réception et 5 cibles. Seules les proportions de pannes s'inspirent des enquêtes IEEE/EPRI. Les prix, coûts, tarifs et seuils sont des hypothèses, pas des statistiques.
- **Modèles** : 4 modèles scikit-learn (`HistGradientBoosting`), un par cible.
- **Découpage** : temporel (entraînement jusqu'en 2023, test en 2024), pour éviter les fuites de données. Les colonnes postérieures au diagnostic sont exclues de X.

| Cible | Type | Résultat sur le test 2024 |
|---|---|---|
| Décision (réparer / remplacer) | classification | AUC 0,88 ; balanced accuracy 0,79 |
| Mode de panne (7 classes) | multiclasse | F1 macro 0,89 |
| Devis (log €) | régression | erreur médiane 15 % |
| Délai (jours) | régression | MAE 1,5 jour |
| Panne précoce à 12 mois | classification | AUC 0,59 |

**Ces scores sont optimistes** : les relations entre variables ont été codées par l'auteur, donc le modèle les retrouve facilement. Ils ne disent rien de la performance sur de vrais moteurs. Seul le modèle de panne précoce, bruité par construction, est à peu près honnête.

## Structure du dépôt

```
motortriage/
├── app.py                  # application Streamlit (FR / DE)
├── m_decision.pkl          # modèle : réparer ou remplacer
├── m_mode.pkl              # modèle : cause de panne
├── m_quote.pkl             # modèle : devis
├── m_days.pkl              # modèle : délai
├── requirements.txt
├── colab_launch.sh         # lancement dans Google Colab
├── .streamlit/config.toml  # thème
└── notebooks/              # génération des données et entraînement
```

## Lancer en local

```bash
git clone https://github.com/alexsouye09-lds/Motortriage.git
cd Motortriage
pip install -r requirements.txt
streamlit run app.py
```

Puis ouvrir http://localhost:8501 dans le navigateur.

## Lancer dans Google Colab

Dans une cellule Colab, sans rien installer à la main : le script affiche **un seul lien** (`trycloudflare.com`) à ouvrir.
Les liens `Local`, `Network` et `External URL` de Streamlit ne fonctionnent pas depuis Colab.

```bash
!wget -q https://raw.githubusercontent.com/alexsouye09-lds/Motortriage/main/colab_launch.sh
!bash colab_launch.sh
```

Le lien est temporaire : il disparaît à la fermeture de la session Colab.

Les fichiers `.pkl` ont été créés avec la version de scikit-learn indiquée dans `requirements.txt`. Gardez la même version pour pouvoir les charger. N'ouvrez que des fichiers `.pkl` dont vous connaissez l'origine, car ce format peut exécuter du code.

## Limites

- Un modèle entraîné sur ce fichier n'est **pas utilisable chez de vrais clients** : il sert à construire et tester le pipeline.
- La disposition à payer des ateliers n'est pas validée.
- La classe d'efficacité IE5 n'existe pas dans les données d'entraînement (l'app utilise IE4 à la place).

## Suite prévue

1. Faire tester l'outil par 2 ou 3 ateliers et recueillir leurs vrais dossiers.
2. Réentraîner et valider les modèles sur ces données réelles (sinon : jeux publics de défauts de roulements, DOE MotorMaster+, dont les licences restent à vérifier).
3. Mesurer l'intérêt réel des ateliers avant tout développement supplémentaire.

## 🤝 Ateliers pilotes recherchés

Vous dirigez un atelier de réparation de moteurs ? Je cherche des ateliers pour tester MotorTriage sur de vrais dossiers et l'adapter à votre façon de travailler.

📧 ouedaalexis@gmail.com

