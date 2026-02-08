"""
Test script for Organizze API integration
Run this to verify all endpoints are working correctly
"""

from organizze_client import OrganizzeClient, OrganizzeAPIError
from datetime import datetime
import json


def test_basic_endpoints():
    """Test basic read-only endpoints"""
    print("=" * 60)
    print("ORGANIZZE API TEST SUITE")
    print("=" * 60)

    try:
        client = OrganizzeClient()
        print("✅ API client initialized successfully\n")

        # Test Accounts
        print("📊 Testing GET /accounts...")
        accounts = client.get_accounts()
        print(f"   Found {len(accounts)} accounts")
        if accounts:
            print(f"   Sample: {accounts[0]['name']} - R$ {accounts[0].get('default_balance', 0):.2f}")
        print()

        # Test Categories
        print("🏷️  Testing GET /categories...")
        categories = client.get_categories()
        print(f"   Found {len(categories)} categories")
        if categories:
            sample_cats = [c['name'] for c in categories[:5]]
            print(f"   Samples: {', '.join(sample_cats)}")
        print()

        # Test Credit Cards
        print("💳 Testing GET /credit_cards...")
        cards = client.get_credit_cards()
        print(f"   Found {len(cards)} credit cards")
        if cards:
            for card in cards:
                if not card.get('archived'):
                    limit = card.get('limit_cents', 0) / 100
                    print(f"   {card['name']}: R$ {limit:,.2f} limit")
        print()

        # Test Transactions
        print("💰 Testing GET /transactions...")
        today = datetime.now()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        transactions = client.get_transactions(start_date, end_date)
        print(f"   Found {len(transactions)} transactions this month")

        if transactions:
            # Calculate totals
            income = sum(t.get('amount_cents', 0) for t in transactions if t.get('amount_cents', 0) > 0) / 100
            expenses = sum(abs(t.get('amount_cents', 0)) for t in transactions if t.get('amount_cents', 0) < 0) / 100
            print(f"   Income: R$ {income:,.2f}")
            print(f"   Expenses: R$ {expenses:,.2f}")
            print(f"   Balance: R$ {income - expenses:,.2f}")
        print()

        # Test Budgets
        print("🎯 Testing GET /budgets...")
        budgets = client.get_budgets(today.year, today.month)
        print(f"   Found {len(budgets)} budget entries")
        if budgets:
            for budget in budgets[:3]:
                amount = budget.get('amount_cents', 0) / 100
                cat_id = budget.get('category_id')
                print(f"   Category {cat_id}: R$ {amount:,.2f}")
        print()

        # Test Credit Card Invoices
        if cards:
            print("📋 Testing GET /credit_cards/{id}/invoices...")
            first_card = next((c for c in cards if not c.get('archived')), None)
            if first_card:
                invoices = client.get_invoices(first_card['id'], year=today.year)
                print(f"   Found {len(invoices)} invoices for {first_card['name']}")
                if invoices:
                    for inv in invoices[:3]:
                        amount = inv.get('amount_cents', 0) / 100
                        date = inv.get('date', 'N/A')
                        print(f"   {date}: R$ {amount:,.2f}")
            print()

        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📊 SUMMARY:")
        print(f"   Accounts: {len(accounts)}")
        print(f"   Categories: {len(categories)}")
        print(f"   Credit Cards: {len(cards)}")
        print(f"   Transactions (this month): {len(transactions)}")
        print(f"   Budget Entries: {len(budgets)}")
        print()

    except OrganizzeAPIError as e:
        print(f"\n❌ API Error: {e}")
        print("\nPlease check:")
        print("  1. ORGANIZZE_EMAIL environment variable is set")
        print("  2. ORGANIZZE_API_KEY environment variable is set")
        print("  3. Credentials are valid")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_write_operations():
    """
    Test write operations (commented out by default to avoid unwanted changes)
    Uncomment specific tests when ready to test creation/modification
    """
    print("\n" + "=" * 60)
    print("WRITE OPERATIONS TEST (DISABLED BY DEFAULT)")
    print("=" * 60)
    print("\nUncomment test_write_operations() code to test:")
    print("  - Creating accounts")
    print("  - Creating categories")
    print("  - Creating transactions")
    print("  - Creating transfers")
    print("  - Updating/deleting operations")
    print("\n⚠️  Be careful - these operations modify your Organizze data!")
    print("=" * 60)

    # Uncomment to test account creation:
    # client = OrganizzeClient()
    # new_account = client.create_account(
    #     name="Test Account",
    #     account_type="checking",
    #     default_balance=100.0
    # )
    # print(f"Created account: {new_account}")
    #
    # # Delete test account
    # if new_account:
    #     client.delete_account(new_account['id'])
    #     print("Deleted test account")


if __name__ == '__main__':
    success = test_basic_endpoints()
    test_write_operations()

    if success:
        print("\n🎉 All systems operational!")
        print("\nNext steps:")
        print("  1. Deploy to Cloud Run: gcloud run deploy organizze-bot --source .")
        print("  2. Test bot commands in Telegram")
        print("  3. Monitor logs: gcloud run services logs read organizze-bot")
    else:
        print("\n❌ Tests failed. Please fix the issues above.")
