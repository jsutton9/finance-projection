DAYS_PER_YEAR = 365.2425

INCOME_TAX_BRACKETS_2018 = [
        [9525, .1],
        [38700, 0.12],
        [82500, .22],
        [157500, .24],
        [200000, .32],
        [500000, .35],
        [float("inf"), .37]
    ]

CAPITAL_GAINS_TAX_BRACKETS_2018 = [
        [38600, 0.],
        [425800, .15],
        [float("inf"), .2]
    ]

DEDUCTION_2018 = 12000
PA_TAX_2018 = 0.037
PIT_TAX_2018 = 0.03
SS_TAX_2018 = 0.062
SS_CAP_2018 = 127200

class TaxPolicy:
    def __init__(self):
        self.federalIncomeBrackets = []
        self.federalCapitalGainsBrackets = []
        self.federalDeduction = 0.0
        self.stateRate = 0.0
        self.cityRate = 0.0
        self.socialSecurityRate = 0.0
        self.socialSecurityWageBase = 0.0

        self.totalPay = 0.0
        self.totalCapitalGains = 0.0
        self.withheld = 0.0

        self.lastLiability = 0.0

    def setFederalTax(self, incomeBrackets, capitalGainsBrackets, deduction):
        self.federalIncomeBrackets = incomeBrackets
        self.federalCapitalGainsBrackets = capitalGainsBrackets
        self.federalDeduction = deduction

    def setStateTax(self, rate):
        self.stateRate = rate

    def setCityTax(self, rate):
        self.cityRate = rate

    def setSocialSecurityTax(self, rate, wageBase):
        self.socialSecurityRate = rate
        self.socialSecurityWageBase = wageBase

    def federalIncomeTax(self, pay):
        taxablePay = pay - self.federalDeduction
        if taxablePay < 0:
            return 0.0

        liability = 0.0
        previousCap = 0.0
        for cap, rate in self.federalIncomeBrackets:
            liability += (min(taxablePay, cap) - previousCap)*rate
            if taxablePay <= cap:
                break
            previousCap = cap

        return liability

    def federalCapitalGainsTax(self, pay, capitalGains):
        taxablePay = pay - self.federalDeduction
        taxableGains = capitalGains
        if taxablePay < 0:
            taxableGains -= taxablePay
            taxablePay = 0.0

        liability = 0.0
        previousCap = 0.0
        for cap, rate in self.federalCapitalGainsBrackets:
            inBracket = min(taxablePay+taxableGains, cap) - max(taxablePay, previousCap)
            if inBracket > 0:
                liability += inBracket*rate
            if taxablePay < cap:
                break

        return liability

    def stateTax(self, pay, capitalGains):
        taxableIncome = max(0, pay + capitalGains - self.federalDeduction)
        return taxableIncome*self.stateRate

    def cityTax(self, pay):
        taxableIncome = max(0, pay - self.federalDeduction)
        return taxableIncome*self.cityRate

    def socialSecurityTax(self, pay):
        taxableIncome = min(max(0, pay - self.federalDeduction), self.socialSecurityWageBase)
        return taxableIncome*self.socialSecurityRate

    def withhold(self, pay):
        self.totalPay += pay
        expectedPay = pay*DAYS_PER_YEAR

        withholding = (self.federalIncomeTax(expectedPay) + self.stateTax(expectedPay, 0) \
                       + self.cityTax(expectedPay) + self.socialSecurityTax(expectedPay)) \
                      /DAYS_PER_YEAR
        self.withheld += withholding

        return pay - withholding

    def recordCapitalGains(self, capitalGains):
        self.totalCapitalGains += capitalGains

    def refund(self):
        liability = self.federalIncomeTax(self.totalPay) \
                  + self.federalCapitalGainsTax(self.totalPay, self.totalCapitalGains) \
                  + self.stateTax(self.totalPay, self.totalCapitalGains) \
                  + self.cityTax(self.totalPay) \
                  + self.socialSecurityTax(self.totalPay)
        refund = self.withheld - liability

        self.totalPay = 0.0
        self.totalCapitalGains = 0.0
        self.withheld = 0.0

        self.lastLiability = liability

        return refund
