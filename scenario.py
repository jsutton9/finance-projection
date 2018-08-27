import datetime
import heapq

ONE_DAY = datetime.timedelta(1)
DAYS_PER_YEAR = 365.2425

def parseDate(dateString):
    return datetime.datetime.strptime(dateString, "%Y-%m-%d").date()

class Scenario:
    def __init__(self, startDate, tax, initialBalance):
        self.eventQueue = []
        self.date = parseDate(startDate)
        self.balance = initialBalance
        self.taxPolicy = tax
        self.principal = 0.0
        self.pay = 0.0
        self.expenses = 0.0
        self.returnRate = 0.0

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
            principalPortion = self.principal/self.balance
            self.principal += amount*principalPortion
            self.taxPolicy.recordCapitalGains(amount*(1-principalPortion))
        else:
            self.principal += amount
        self.balance += amount

    def step(self):
        while len(self.eventQueue) > 0 and (self.eventQueue[0][0] - self.date) < ONE_DAY/2:
            heapq.heappop(self.eventQueue)[1]()

        pay = self.pay/DAYS_PER_YEAR
        pay = self.taxPolicy.withhold(pay)
        surplus = pay - self.expenses/DAYS_PER_YEAR
        self.deposit(surplus)
        self.balance *= (1+self.returnRate)**(1./DAYS_PER_YEAR)

        if self.date.month == 1 and self.date.day == 1:
            self.deposit(self.taxPolicy.refund())

        self.date += ONE_DAY
