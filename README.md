# Banking Transactions API

## ESG MBA – Évaluation de fin de cours  
**MBA 2 – Python – Exposition de données sous forme d’API**

---

## 📌 Présentation du projet

Ce projet consiste à développer une **API REST basée sur FastAPI** permettant d’exposer et d’analyser des données de transactions bancaires fictives.

L’API est destinée à être utilisée par une application métier de gestion des portefeuilles clients bancaires.

Le projet respecte les exigences du cours en matière de :
- Qualité du code
- Tests unitaires et fonctionnels
- Typage Python
- Packaging
- Industrialisation (Docker & GitHub Actions)

---

## 👥 Équipe projet

| Nom | Email |
|----|------|
| **Idriss MBE** | i_mbe@stu-mba-esg.com |
| **Nadiath SAKA** | n_saka@stu-mba-esg.com |
| **Michele FAMENI** | m_fameni@stu-mba-esg.com |
| **Raouf OROUGOURA** | r_orougoura@stu-mba-esg.com |

---

## 🧱 Architecture du projet

```text
FastApi/
│
├── .github/
│   └── workflows/         # GitHub Actions (CI)
│
├── app/                   # Application FastAPI
│   ├── __init__.py
│   ├── main.py
│   ├── routers/           # Endpoints API
│   ├── services/          # Logique métier
│   ├── models/            # Schémas Pydantic
│   └── utils/
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
