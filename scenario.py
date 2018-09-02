import datetime
import heapq

ONE_DAY = datetime.timedelta(1)
DAYS_PER_YEAR = 365.2425

def parseDate(dateString):
    return datetime.datetime.strptime(dateString, "%Y-%m-%d").date()

class Scenario:
    def __init__(self, startDate, tax, initialBalance, initialRetirementBalance):
        self.eventQueue = []
        self.date = parseDate(startDate)
        self.balance = initialBalance
        self.retirementBalance = initialRetirementBalance
        self.taxPolicy = tax
        self.principal = 0.0
        self.pay = 0.0
        self.expenses = 0.0
        self.returnRate = 0.0
        self.lastRetirementIncome = 0.0

    def addEvent(self, dateString, event):
        date = parseDate(dateString)
        heapq.heappush(self.eventQueue, (date, event))

    def addPayChange(self, dateString, pay):
        def f():
            self.pay = pay
        self.addEvent(dateString, f)

    def addExpenseChange(self, dateString, expenses):
        def f():
            self.expenses = expenses
        self.addEvent(dateString, f)

    def addRateChange(self, dateString, rate):
        def f():
            self.returnRate = rate
        self.addEvent(dateString, f)

    def liquidate(self, amount):
        principalPortion = self.principal/self.balance
        self.principal += amount*principalPortion
        self.taxPolicy.recordCapitalGains(surplus*(1-principalPortion))

    def deposit(self, amount):
        if amount < 0:
            taxed = min(-amount, self.balance)
            retirement = -amount - taxed
            principalPortion = self.principal/self.balance if self.balance > 0 else 1.0
            self.balance -= taxed
            self.principal -= taxed*principalPortion
            self.taxPolicy.recordCapitalGains(taxed*(1-principalPortion))
            self.retirementBalance -= retirement
            self.lastRetirementIncome += retirement
        else:
            self.principal += amount
            self.balance += amount

    def retirementTransfer(self, amount):
        self.deposit(-amount)
        self.retirementBalance += amount

    def step(self):
        while len(self.eventQueue) > 0 and (self.eventQueue[0][0] - self.date) < ONE_DAY/2:
            heapq.heappop(self.eventQueue)[1]()

        pay = self.pay/DAYS_PER_YEAR + self.lastRetirementIncome
        pay = self.taxPolicy.withhold(pay)
        pay -= self.lastRetirementIncome
        self.lastRetirementIncome = 0.0
        surplus = pay - self.expenses/DAYS_PER_YEAR
        self.deposit(surplus)
        self.balance *= (1+self.returnRate)**(1./DAYS_PER_YEAR)
        self.retirementBalance *= (1+self.returnRate)**(1./DAYS_PER_YEAR)

        if self.date.month == 1 and self.date.day == 1:
            refund, k401, ira = self.taxPolicy.refund()
            self.deposit(refund)
            self.retirementTransfer(2*k401+ira) # assume 1:1 matching

        self.date += ONE_DAY
