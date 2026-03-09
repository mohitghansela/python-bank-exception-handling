"""
╔══════════════════════════════════════════════════════════╗
║       🏦 BANK MANAGEMENT SYSTEM - MINI PROJECT          ║
║         Python Exception Handling Demonstration         ║
╚══════════════════════════════════════════════════════════╝

Topics Covered:
  ✅ try / except / else / finally
  ✅ Custom Exceptions (User-defined)
  ✅ Multiple except blocks
  ✅ Exception chaining
  ✅ Logging errors
  ✅ raise keyword
"""

import logging
import datetime

# ─────────────────────────────────────────────
# 📋 LOGGING SETUP
# ─────────────────────────────────────────────
logging.basicConfig(
    filename="bank_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ─────────────────────────────────────────────
# 🔴 CUSTOM EXCEPTIONS (User-Defined)
# ─────────────────────────────────────────────

class BankException(Exception):
    """Base class for all Bank related exceptions"""
    pass


class InsufficientFundsError(BankException):
    """Raised when account balance is less than withdrawal amount"""
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(
            f"❌ Insufficient Funds! Balance: ₹{balance}, Requested: ₹{amount}"
        )


class InvalidAmountError(BankException):
    """Raised when a negative or zero amount is entered"""
    def __init__(self, amount):
        self.amount = amount
        super().__init__(
            f"❌ Invalid Amount: ₹{amount}. Amount must be positive!"
        )


class AccountNotFoundError(BankException):
    """Raised when account number does not exist"""
    def __init__(self, acc_no):
        self.acc_no = acc_no
        super().__init__(
            f"❌ Account '{acc_no}' not found in the system!"
        )


class AccountLockedError(BankException):
    """Raised when account is locked due to multiple failed attempts"""
    def __init__(self, acc_no):
        super().__init__(
            f"🔒 Account '{acc_no}' is LOCKED due to multiple failed PIN attempts!"
        )


# ─────────────────────────────────────────────
# 🏦 BANK ACCOUNT CLASS
# ─────────────────────────────────────────────

class BankAccount:
    def __init__(self, acc_no, holder_name, balance, pin):
        self.acc_no = acc_no
        self.holder_name = holder_name
        self._balance = balance
        self.__pin = pin
        self._locked = False
        self._failed_attempts = 0
        self.transactions = []

    def get_balance(self):
        return self._balance

    def verify_pin(self, entered_pin):
        """PIN verification with lockout after 3 failed attempts"""
        if self._locked:
            raise AccountLockedError(self.acc_no)

        if entered_pin != self.__pin:
            self._failed_attempts += 1
            remaining = 3 - self._failed_attempts
            if self._failed_attempts >= 3:
                self._locked = True
                raise AccountLockedError(self.acc_no)
            raise ValueError(
                f"❌ Wrong PIN! {remaining} attempt(s) remaining."
            )

        self._failed_attempts = 0  # Reset on success
        return True

    def deposit(self, amount):
        """Deposit money into account"""
        try:
            if not isinstance(amount, (int, float)):
                raise TypeError(f"Amount must be a number, got {type(amount).__name__}")
            if amount <= 0:
                raise InvalidAmountError(amount)

            self._balance += amount
            self._log_transaction("DEPOSIT", amount)
            return self._balance

        except InvalidAmountError as e:
            logging.error(f"Deposit failed for {self.acc_no}: {e}")
            raise  # re-raise to caller

        except TypeError as e:
            logging.error(f"Type error during deposit: {e}")
            raise

    def withdraw(self, amount):
        """Withdraw money from account"""
        try:
            if not isinstance(amount, (int, float)):
                raise TypeError(f"Amount must be a number, got {type(amount).__name__}")
            if amount <= 0:
                raise InvalidAmountError(amount)
            if amount > self._balance:
                raise InsufficientFundsError(self._balance, amount)

            self._balance -= amount
            self._log_transaction("WITHDRAWAL", amount)
            return self._balance

        except (InvalidAmountError, InsufficientFundsError) as e:
            logging.error(f"Withdrawal failed for {self.acc_no}: {e}")
            raise

    def _log_transaction(self, txn_type, amount):
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.transactions.append({
            "type": txn_type,
            "amount": amount,
            "balance": self._balance,
            "time": timestamp
        })

    def show_statement(self):
        print(f"\n{'='*55}")
        print(f"  📄 ACCOUNT STATEMENT - {self.holder_name}")
        print(f"  Account No: {self.acc_no}")
        print(f"{'='*55}")
        if not self.transactions:
            print("  No transactions yet.")
        for txn in self.transactions:
            symbol = "➕" if txn["type"] == "DEPOSIT" else "➖"
            print(f"  {symbol} {txn['type']:<12} ₹{txn['amount']:<10} Balance: ₹{txn['balance']:<10} [{txn['time']}]")
        print(f"{'='*55}")
        print(f"  💰 Current Balance: ₹{self._balance}")
        print(f"{'='*55}\n")


# ─────────────────────────────────────────────
# 🏦 BANK CLASS (manages multiple accounts)
# ─────────────────────────────────────────────

class Bank:
    def __init__(self, name):
        self.name = name
        self._accounts = {}

    def create_account(self, acc_no, holder_name, initial_balance, pin):
        """Create new bank account"""
        try:
            if acc_no in self._accounts:
                raise ValueError(f"Account '{acc_no}' already exists!")
            if initial_balance < 0:
                raise InvalidAmountError(initial_balance)
            if not str(pin).isdigit() or len(str(pin)) != 4:
                raise ValueError("PIN must be a 4-digit number!")

            self._accounts[acc_no] = BankAccount(acc_no, holder_name, initial_balance, pin)
            print(f"  ✅ Account created successfully for {holder_name} | Acc No: {acc_no}")
            return self._accounts[acc_no]

        except (ValueError, InvalidAmountError) as e:
            print(f"  Account Creation Failed: {e}")
            logging.error(f"Account creation failed: {e}")
            return None

    def get_account(self, acc_no):
        """Fetch account or raise error"""
        if acc_no not in self._accounts:
            raise AccountNotFoundError(acc_no)
        return self._accounts[acc_no]

    def transfer(self, from_acc, to_acc, amount, pin):
        """Transfer funds between accounts"""
        print(f"\n  🔄 Initiating Transfer: ₹{amount} from {from_acc} → {to_acc}")
        try:
            sender = self.get_account(from_acc)
            receiver = self.get_account(to_acc)

            sender.verify_pin(pin)
            sender.withdraw(amount)
            receiver.deposit(amount)

            print(f"  ✅ Transfer Successful! ₹{amount} transferred to {receiver.holder_name}")

        except AccountNotFoundError as e:
            print(f"  Transfer Failed: {e}")

        except AccountLockedError as e:
            print(f"  Transfer Blocked: {e}")

        except ValueError as e:
            print(f"  PIN Error: {e}")

        except InsufficientFundsError as e:
            print(f"  Transfer Failed: {e}")

        except Exception as e:
            print(f"  Unexpected Error: {e}")
            logging.error(f"Transfer error: {e}")

        finally:
            print("  📋 Transfer process completed (finally block executed)")


# ─────────────────────────────────────────────
# 🚀 MAIN DEMO - EXCEPTION HANDLING IN ACTION
# ─────────────────────────────────────────────

def divider(title=""):
    print(f"\n{'─'*55}")
    if title:
        print(f"  🔷 {title}")
    print(f"{'─'*55}")


def main():
    print("\n" + "═"*55)
    print("  🏦  PYTHON BANK SYSTEM - Exception Handling Demo")
    print("═"*55)

    bank = Bank("PyBank India")

    # 1. Account Creation
    divider("ACCOUNT CREATION")
    acc1 = bank.create_account("ACC001", "Rahul Sharma", 10000, 1234)
    acc2 = bank.create_account("ACC002", "Priya Verma",  5000,  5678)
    bank.create_account("ACC001", "Duplicate Test", 1000, 0000)   # duplicate
    bank.create_account("ACC003", "Bad Balance", -500, 9999)       # negative balance
    bank.create_account("ACC004", "Bad PIN",    1000, 12)          # invalid pin

    # 2. Deposit 
    divider("DEPOSIT OPERATIONS")

    # Valid deposit
    try:
        new_bal = acc1.deposit(5000)
        print(f"  ✅ Deposited ₹5000 | New Balance: ₹{new_bal}")
    except Exception as e:
        print(f"  Error: {e}")

    # Invalid deposit - negative
    try:
        acc1.deposit(-200)
    except InvalidAmountError as e:
        print(f"  Caught InvalidAmountError: {e}")

    # Invalid deposit - wrong type
    try:
        acc1.deposit("paanch_sau")
    except TypeError as e:
        print(f"  Caught TypeError: {e}")

    # 3. Withdrawal 
    divider("WITHDRAWAL OPERATIONS")

    # Valid withdrawal
    try:
        new_bal = acc2.withdraw(1000)
        print(f"  ✅ Withdrew ₹1000 | New Balance: ₹{new_bal}")
    except Exception as e:
        print(f"  Error: {e}")

    # Insufficient funds
    try:
        acc2.withdraw(99999)
    except InsufficientFundsError as e:
        print(f"  Caught InsufficientFundsError: {e}")

    # Zero amount
    try:
        acc2.withdraw(0)
    except InvalidAmountError as e:
        print(f"  Caught InvalidAmountError: {e}")

    # 4. Account Not Found 
    divider("ACCOUNT NOT FOUND ERROR")
    try:
        bank.get_account("ACC999")
    except AccountNotFoundError as e:
        print(f"  Caught AccountNotFoundError: {e}")

    # 5. PIN Verification & Lockout 
    divider("PIN VERIFICATION & ACCOUNT LOCKOUT")
    try:
        acc1.verify_pin(9999)  # Wrong
    except ValueError as e:
        print(f"  {e}")

    try:
        acc1.verify_pin(8888)  # Wrong
    except ValueError as e:
        print(f"  {e}")

    try:
        acc1.verify_pin(7777)  # Wrong → Account Locked
    except AccountLockedError as e:
        print(f"  Caught AccountLockedError: {e}")

    # Try using locked account
    try:
        acc1.deposit(100)
        acc1.verify_pin(1234)  # Even correct PIN won't work now
    except AccountLockedError as e:
        print(f"  Locked account access attempt: {e}")

    #  6. Fund Transfer
    divider("FUND TRANSFER")

    # Create fresh account for transfer demo
    acc3 = bank.create_account("ACC005", "Amit Kumar", 8000, 4321)
    acc4 = bank.create_account("ACC006", "Sneha Patel", 2000, 8765)

    bank.transfer("ACC005", "ACC006", 3000, 4321)   # ✅ Valid
    bank.transfer("ACC005", "ACC006", 50000, 4321)  # ❌ Insufficient
    bank.transfer("ACC005", "ACC099", 1000, 4321)   # ❌ Account not found
    bank.transfer("ACC005", "ACC006", 500, 0000)    # ❌ Wrong PIN

    # 7. Account Statements 
    divider("ACCOUNT STATEMENTS")
    acc3.show_statement()
    acc4.show_statement()

    # 8. else & finally demo 
    divider("try / else / finally DEMO")
    print("\n  Example: else runs only if NO exception occurs\n")

    for amount in [2000, -500, 999999]:
        print(f"  Attempting to withdraw ₹{amount}...")
        try:
            bal = acc4.withdraw(amount)
        except InvalidAmountError as e:
            print(f"  [except] {e}")
        except InsufficientFundsError as e:
            print(f"  [except] {e}")
        else:
            print(f"  [else]   ✅ Withdrawal successful! Balance: ₹{bal}")
        finally:
            print(f"  [finally] This always runs!\n")

    print("\n" + "═"*55)
    print("  ✅ Exception Handling Demo Complete!")
    print("  📁 Errors logged in: bank_errors.log")
    print("═"*55 + "\n")


if __name__ == "__main__":
    main()