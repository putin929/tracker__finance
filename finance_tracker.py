#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Трекер расходов и доходов
Простое приложение для учета личных финансов с категориями и аналитикой
"""

import json
import datetime
from collections import defaultdict
import os

class FinanceTracker:
    def __init__(self, data_file="finances.json"):
        self.data_file = data_file
        self.transactions = []
        self.categories = {
            'income': ['Зарплата', 'Фриланс', 'Инвестиции', 'Подарки', 'Прочие доходы'],
            'expense': ['Еда', 'Транспорт', 'Развлечения', 'Коммунальные', 'Здоровье', 
                       'Одежда', 'Образование', 'Прочие расходы']
        }
        self.load_data()
    
    def load_data(self):
        """Загружает данные из файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.transactions = data.get('transactions', [])
                    # Восстанавливаем даты из строк
                    for transaction in self.transactions:
                        transaction['date'] = datetime.datetime.strptime(
                            transaction['date'], '%Y-%m-%d'
                        ).date()
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            self.transactions = []
    
    def save_data(self):
        """Сохраняет данные в файл"""
        try:
            # Конвертируем даты в строки для JSON
            transactions_to_save = []
            for transaction in self.transactions:
                trans_copy = transaction.copy()
                trans_copy['date'] = transaction['date'].strftime('%Y-%m-%d')
                transactions_to_save.append(trans_copy)
            
            data = {
                'transactions': transactions_to_save
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
    
    def add_transaction(self, amount, category, description, transaction_type, date=None):
        """
        Добавляет новую транзакцию
        
        Args:
            amount (float): Сумма
            category (str): Категория
            description (str): Описание
            transaction_type (str): 'income' или 'expense'
            date (datetime.date): Дата транзакции
        """
        if date is None:
            date = datetime.date.today()
        
        transaction = {
            'id': len(self.transactions) + 1,
            'date': date,
            'amount': abs(amount),  # Всегда положительное число
            'category': category,
            'description': description,
            'type': transaction_type
        }
        
        self.transactions.append(transaction)
        self.save_data()
        print(f"✅ Транзакция добавлена: {transaction_type} {amount} руб. - {description}")
    
    def get_transactions(self, days=30, transaction_type=None):
        """
        Получает транзакции за определенный период
        
        Args:
            days (int): Количество дней назад
            transaction_type (str): Тип транзакций или None для всех
            
        Returns:
            list: Отфильтрованные транзакции
        """
        cutoff_date = datetime.date.today() - datetime.timedelta(days=days)
        
        filtered = [
            t for t in self.transactions 
            if t['date'] >= cutoff_date
        ]
        
        if transaction_type:
            filtered = [t for t in filtered if t['type'] == transaction_type]
        
        return sorted(filtered, key=lambda x: x['date'], reverse=True)
    
    def get_balance(self, days=30):
        """Вычисляет баланс за период"""
        transactions = self.get_transactions(days)
        income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        return income - expenses
    
    def get_category_summary(self, days=30):
        """Получает сводку по категориям"""
        transactions = self.get_transactions(days)
        
        income_by_category = defaultdict(float)
        expense_by_category = defaultdict(float)
        
        for transaction in transactions:
            if transaction['type'] == 'income':
                income_by_category[transaction['category']] += transaction['amount']
            else:
                expense_by_category[transaction['category']] += transaction['amount']
        
        return dict(income_by_category), dict(expense_by_category)
    
    def display_transactions(self, days=30, limit=10):
        """Отображает последние транзакции"""
        transactions = self.get_transactions(days)[:limit]
        
        if not transactions:
            print("Транзакций не найдено.")
            return
        
        print(f"\n📋 Последние {len(transactions)} транзакций за {days} дней:")
        print("-" * 80)
        print(f"{'Дата':<12} {'Тип':<8} {'Сумма':<12} {'Категория':<15} {'Описание'}")
        print("-" * 80)
        
        for t in transactions:
            amount_str = f"{t['amount']:,.0f} руб."
            type_icon = "💰" if t['type'] == 'income' else "💸"
            print(f"{t['date']!s:<12} {type_icon:<8} {amount_str:<12} {t['category']:<15} {t['description'][:25]}")
    
    def display_summary(self, days=30):
        """Отображает финансовую сводку"""
        income_summary, expense_summary = self.get_category_summary(days)
        balance = self.get_balance(days)
        
        total_income = sum(income_summary.values())
        total_expenses = sum(expense_summary.values())
        
        print(f"\n📊 ФИНАНСОВАЯ СВОДКА за {days} дней")
        print("=" * 50)
        
        print(f"\n💰 ДОХОДЫ: {total_income:,.0f} руб.")
        for category, amount in sorted(income_summary.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_income * 100) if total_income > 0 else 0
            print(f"  • {category}: {amount:,.0f} руб. ({percentage:.1f}%)")
        
        print(f"\n💸 РАСХОДЫ: {total_expenses:,.0f} руб.")
        for category, amount in sorted(expense_summary.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            print(f"  • {category}: {amount:,.0f} руб. ({percentage:.1f}%)")
        
        print(f"\n🏦 БАЛАНС: {balance:,.0f} руб.")
        
        if balance > 0:
            print("✅ Отличная работа! Вы в плюсе.")
        elif balance < 0:
            print("⚠️  Внимание: расходы превышают доходы.")
        else:
            print("🔄 Вы на нуле.")

def main():
    tracker = FinanceTracker()
    
    print("=== ТРЕКЕР ФИНАНСОВ ===\n")
    
    while True:
        print("1. Добавить доход")
        print("2. Добавить расход")
        print("3. Показать транзакции")
        print("4. Финансовая сводка")
        print("5. Показать категории")
        print("6. Выход")
        
        choice = input("\nВыберите действие (1-6): ")
        
        if choice == "1" or choice == "2":
            transaction_type = 'income' if choice == "1" else 'expense'
            type_name = 'доход' if choice == "1" else 'расход'
            categories = tracker.categories[transaction_type]
            
            try:
                # Выбор категории
                print(f"\nКатегории для {type_name}:")
                for i, cat in enumerate(categories, 1):
                    print(f"{i}. {cat}")
                
                cat_choice = int(input(f"Выберите категорию (1-{len(categories)}): ")) - 1
                if not (0 <= cat_choice < len(categories)):
                    print("Неверная категория")
                    continue
                
                category = categories[cat_choice]
                amount = float(input(f"Введите сумму {type_name}: "))
                description = input("Описание (необязательно): ") or f"{type_name.capitalize()} - {category}"
                
                # Опционально - дата
                date_input = input("Дата (YYYY-MM-DD) или Enter для сегодня: ")
                date = None
                if date_input:
                    try:
                        date = datetime.datetime.strptime(date_input, '%Y-%m-%d').date()
                    except ValueError:
                        print("Неверный формат даты, используется сегодняшняя дата")
                
                tracker.add_transaction(amount, category, description, transaction_type, date)
                
            except ValueError:
                print("Ошибка: введите корректные данные")
                
        elif choice == "3":
            try:
                days = int(input("За сколько дней показать транзакции? (по умолчанию 30): ") or "30")
                limit = int(input("Сколько транзакций показать? (по умолчанию 10): ") or "10")
                tracker.display_transactions(days, limit)
            except ValueError:
                print("Ошибка: введите корректное число")
                
        elif choice == "4":
            try:
                days = int(input("За сколько дней показать сводку? (по умолчанию 30): ") or "30")
                tracker.display_summary(days)
            except ValueError:
                print("Ошибка: введите корректное число")
                
        elif choice == "5":
            print("\n📂 КАТЕГОРИИ:")
            print("\n💰 Доходы:")
            for cat in tracker.categories['income']:
                print(f"  • {cat}")
            print("\n💸 Расходы:")
            for cat in tracker.categories['expense']:
                print(f"  • {cat}")
                
        elif choice == "6":
            print("До свидания! 💰")
            break
            
        else:
            print("Неверный выбор. Попробуйте снова.")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
