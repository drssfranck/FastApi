import pandas as pd
from typing import Dict, List, Any
import numpy as np

class FraudDetectionService:
    """
    Service pour la détection de fraude bancaire.
    Fournit des méthodes pour calculer les taux de fraude et effectuer du scoring simplifié.
    """

    def __init__(self):
        self.fraud_threshold = 0.5  # Seuil de probabilité pour considérer une transaction comme frauduleuse

    def calculate_fraud_rate(self, df: pd.DataFrame) -> float:
        """
        Calcule le taux de fraude global dans un DataFrame de transactions.

        Args:
            df: DataFrame contenant les transactions avec une colonne 'isFraud'

        Returns:
            Taux de fraude en pourcentage
        """
        if 'isFraud' not in df.columns:
            return 0.0

        total_transactions = len(df)
        fraudulent_transactions = len(df[df['isFraud'] == 1])

        return (fraudulent_transactions / total_transactions) * 100 if total_transactions > 0 else 0.0

    def calculate_fraud_by_type(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Calcule la répartition du taux de fraude par type de transaction.

        Args:
            df: DataFrame contenant les transactions

        Returns:
            Liste de dictionnaires avec type, total_transactions, fraudulent_transactions, fraud_rate_percent
        """
        if 'use_chip' not in df.columns or 'isFraud' not in df.columns:
            return []

        fraud_by_type = []
        for txn_type in df['use_chip'].unique():
            if pd.isna(txn_type):
                continue

            type_df = df[df['use_chip'] == txn_type]
            total = len(type_df)
            fraudulent = len(type_df[type_df['isFraud'] == 1])
            rate = (fraudulent / total) * 100 if total > 0 else 0.0

            fraud_by_type.append({
                "type": txn_type,
                "total_transactions": total,
                "fraudulent_transactions": fraudulent,
                "fraud_rate_percent": round(rate, 2)
            })

        return fraud_by_type

    def predict_fraud_probability(self, transaction_data: Dict[str, Any]) -> float:
        """
        Calcule la probabilité de fraude pour une transaction donnée.
        Utilise des règles simplifiées basées sur les caractéristiques de la transaction.

        Args:
            transaction_data: Dictionnaire contenant les données de la transaction
                - type: str (type de transaction)
                - amount: float (montant)
                - oldbalanceOrg: float (solde avant)
                - newbalanceOrig: float (solde après)

        Returns:
            Probabilité de fraude entre 0 et 1
        """
        amount = transaction_data.get('amount', 0.0)
        txn_type = transaction_data.get('type', '').upper()
        old_balance = transaction_data.get('oldbalanceOrg', 0.0)
        new_balance = transaction_data.get('newbalanceOrig', 0.0)

        # Calcul de la différence de balance
        balance_diff = old_balance - new_balance

        # Probabilité de base
        probability = 0.1

        # Règles de détection basées sur les montants
        if amount > 5000:
            probability += 0.4
        elif amount > 2000:
            probability += 0.3
        elif amount > 1000:
            probability += 0.2

        # Montants extrêmes
        if amount > 10000:
            probability += 0.3

        # Incohérence dans les balances
        if abs(balance_diff - amount) > 0.01:  # Tolérance pour les arrondis
            probability += 0.3

        # Types de transaction risqués
        if txn_type == "TRANSFER" and amount > 1000:
            probability += 0.2
        elif txn_type == "CASH_OUT" and amount > 500:
            probability += 0.15

        # Limiter entre 0 et 1
        return min(max(probability, 0.0), 1.0)

    def is_fraudulent(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Détermine si une transaction est frauduleuse basée sur le seuil.

        Args:
            transaction_data: Données de la transaction

        Returns:
            True si frauduleuse, False sinon
        """
        probability = self.predict_fraud_probability(transaction_data)
        return probability > self.fraud_threshold

    def get_fraud_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule les statistiques complètes de fraude.

        Args:
            df: DataFrame des transactions

        Returns:
            Dictionnaire avec total_transactions, fraudulent_transactions, fraud_percentage, total_fraud_amount
        """
        if df.empty:
            return {
                "total_transactions": 0,
                "fraudulent_transactions": 0,
                "fraud_percentage": 0.0,
                "total_fraud_amount": 0.0
            }

        total_transactions = len(df)
        fraudulent_transactions = len(df[df['isFraud'] == 1]) if 'isFraud' in df.columns else 0
        fraud_percentage = (fraudulent_transactions / total_transactions) * 100 if total_transactions > 0 else 0.0
        total_fraud_amount = df[df['isFraud'] == 1]['amount'].sum() if 'isFraud' in df.columns and 'amount' in df.columns else 0.0

        return {
            "total_transactions": total_transactions,
            "fraudulent_transactions": fraudulent_transactions,
            "fraud_percentage": round(fraud_percentage, 2),
            "total_fraud_amount": float(total_fraud_amount)
        }

    def get_suspicious_transactions(self, df: pd.DataFrame, threshold: float = 1000.0) -> List[Dict[str, Any]]:
        """
        Identifie les transactions suspectes basées sur un seuil de montant.

        Args:
            df: DataFrame des transactions
            threshold: Seuil de montant pour considérer une transaction suspecte

        Returns:
            Liste des transactions suspectes
        """
        if 'amount' not in df.columns:
            return []

        suspicious_df = df[df['amount'] >= threshold]
        transactions = suspicious_df.where(pd.notna(suspicious_df), None).to_dict('records')

        # Remplacer NaN par None
        for trans in transactions:
            for key, value in trans.items():
                if isinstance(value, float) and np.isnan(value):
                    trans[key] = None

        return transactions

    def detect_fraud_by_id(self, df: pd.DataFrame, transaction_id: int) -> Dict[str, Any]:
        """
        Détecte si une transaction spécifique est frauduleuse.

        Args:
            df: DataFrame des transactions
            transaction_id: ID de la transaction

        Returns:
            Dictionnaire avec transaction_id, is_fraud, amount, client_id
        """
        if 'id' not in df.columns:
            raise ValueError("DataFrame doit contenir une colonne 'id'")

        transaction = df[df['id'] == transaction_id]
        if transaction.empty:
            raise ValueError(f"Transaction non trouvée")

        row = transaction.iloc[0]
        is_fraud = bool(row.get('isFraud', 0))

        return {
            "transaction_id": transaction_id,
            "is_fraud": is_fraud,
            "amount": float(row.get('amount', 0.0)),
            "client_id": int(row.get('client_id', 0))
        }