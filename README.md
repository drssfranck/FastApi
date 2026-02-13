# 📘 Banking Transactions API — FastAPI Project

## ESG MBA – Évaluation de fin de cours

**MBA 2 – Python – Exposition de données sous forme d’API**

---

## 📌 Présentation du projet

Ce projet consiste à développer une **API REST complète avec FastAPI** pour exposer, filtrer et analyser des données de transactions bancaires fictives.

L’API est conçue pour une application métier de **gestion des portefeuilles clients bancaires** et répond aux exigences académiques en matière de :

* Qualité du code
* Tests unitaires et fonctionnels
* Typage Python
* Packaging
* Industrialisation (Docker & CI/CD GitHub Actions)

---

## 👥 Équipe projet

| Nom                 | Email                                                             |
| ------------------- | ----------------------------------------------------------------- |
| **Idriss MBE**      | [i_mbe@stu-mba-esg.com](mailto:i_mbe@stu-mba-esg.com)             |
| **Nadiath SAKA**    | [n_saka@stu-mba-esg.com](mailto:n_saka@stu-mba-esg.com)           |
| **Michele FAMENI**  | [m_fameni@stu-mba-esg.com](mailto:m_fameni@stu-mba-esg.com)       |
| **Raouf OROUGOURA** | [r_orougoura@stu-mba-esg.com](mailto:r_orougoura@stu-mba-esg.com) |

---

## 🧱 Architecture du projet

```text
FastApi/
│
├── .github/
│   └── workflows/         # CI GitHub Actions
│
├── app/                   # Application FastAPI
│   ├── __init__.py
│   ├── main.py
│   ├── routers/           # Endpoints API
│   ├── services/          # Logique métier
│   ├── models/            # Schémas Pydantic
│   ├── utils/             # Fonctions utilitaires
│   └── data/              # Importation et gestion des datasets
│       ├── import_data.py
│       ├── load_data.py
│       └── datasets/      # Fichiers téléchargés manuellement
│
├── test/                  # Tests
│   ├── unit/              # Tests unitaires
│   └── feature/           # Tests fonctionnels
│
├── Dockerfile
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 📥 Téléchargement manuel du dataset

Les données ne sont pas incluses dans le dépôt GitHub. Vous devez télécharger le dataset depuis Kaggle :

👉 https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets/data?select=transactions_data.csv
